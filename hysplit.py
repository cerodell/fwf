#*****************************************************************************
#
#  BlueSky Framework - Controls the estimation of emissions, incorporation of 
#                      meteorology, and the use of dispersion models to 
#                      forecast smoke impacts from fires.
#  Copyright (C) 2003-2006  USDA Forest Service - Pacific Northwest Wildland 
#                           Fire Sciences Laboratory
#  BlueSky Framework - Version 3.5.1    
#  Copyright (C) 2007-2009  USDA Forest Service - Pacific Northwest Wildland Fire 
#                      Sciences Laboratory and Sonoma Technology, Inc.
#                      All rights reserved.
#
# See LICENSE.TXT for the Software License Agreement governing the use of the
# BlueSky Framework - Version 3.5.1.
#
# Contributors to the BlueSky Framework are identified in ACKNOWLEDGEMENTS.TXT
#
#*********************HYSPLIT Version Notes********************************************
#   Version 6 - Added particle initialization option
#               1) User can set HYSPLIT to write a model initialization file (PARDUMP)
#               2) User can read in a particle input file (PARINIT)
#
#               Erin Pollard, Sonoma Technology Inc., August 2012
#
#   Version 7 - Added support for HYSPLIT v4.9 (KJC, Sonoma Technology, Inc., June 2013
#
#***************************************************************************************
_bluesky_version_ = "3.5.1"

import os.path
import math
from datetime import timedelta
import tarfile
import contextlib
from shutil import copyfileobj

from arlgridfile import ARLGridFile
from hysplitIndexedDataLocation import IndexedDataLocation, CatalogIndexedData, ARLArchiveIndexer

from glob import glob
from kernel.core import Process
from kernel.utility import which
from kernel.bs_datetime import BSDateTime,UTC
from kernel.types import construct_type
from kernel.log import SUMMARY
from trajectory import Trajectory, TrajectoryMet
from dispersion import Dispersion, DispersionMet

class InputARL(Process):
    """ Read ARL-format input meteorological data
    """

    def init(self):
        self.declare_input("met_info", "MetInfo")
        self.declare_output("met_info", "MetInfo")

    def run(self, context):
        ARL_PATTERN = self.config("ARL_PATTERN")

        # added lines for strftime conversion in path names (rcs)
        pathdate = self.config("DATE",BSDateTime)

        met = self.get_input("met_info")
        if met is None:
            met = construct_type("MetInfo")

        metfiles = list()

        date = met["dispersion_start"]
        date_naive = BSDateTime(date.year, date.month, date.day, date.hour,
                               date.minute, date.second, date.microsecond, tzinfo=None)

        disp_time = met["dispersion_end"] - date
        hours_to_run = ((disp_time.days * 86400) + disp_time.seconds) / 3600

        if self.config("USE_INDEXED_ARL_DATA", bool):
            # If the USE_INDEXED_ARL_DATA flag is set, then use pre-indexed
            # ARL data files.  See hysplitIndexedDataLocation.py for more details.

            self.log.info("Using Indexed ARL data archive")
            arlIndexedDataDir = met["dispersion_start"].strftime(self.config("ARL_INDEXED_DATA_DIR"))

            # added lines for strftime conversion in path names (rcs)
            if "%" in arlIndexedDataDir:
                arlIndexedDataDir = pathdate.strftime(arlIndexedDataDir)

            arlIndexFile = self.config("ARL_INDEX_FILE")

            # added lines for strftime conversion in path names (rcs)
            if "%" in arlIndexFile:
                arlIndexFile = pathdate.strftime(arlIndexFile)

            arlindex = os.path.join(arlIndexedDataDir,arlIndexFile)
            if not context.file_exists(arlindex):
                raise IOError("Missing required ARL index file: %s" % arlindex)

            arlHistoricalArchiveDir = self.config("ARL_HISTORICAL_ARCHIVE_DIR")
            metfiles = IndexedDataLocation(arlIndexedDataDir,arlHistoricalArchiveDir,arlindex).getInputFiles(date_naive, hours_to_run)

        elif self.config("USE_CATALOG_INDEXING", bool):
            self.log.info("Using catalog indexed ARL data")
            catalog_indexed_data = CatalogIndexedData(self.config("CATALOG_DATA_INDEX_FILE"))
            # Fix for situation when there are multiple paths to the same met file, causing said file to be listed more
            # than once.  Hysplit fails when given multiple references to the same met file.
            inputfiles = catalog_indexed_data.get_input_files(date_naive, hours_to_run)
            metfiles = list()
            for inputfile in inputfiles:
                if os.path.basename(inputfile) not in [os.path.basename(metfile) for metfile in metfiles]:
                    metfiles.append(inputfile)

        elif self.config("USE_ARL_ARCHIVE_INDEXER", bool):
            self.log.info("Using arl archiver indexed ARL data")
            arl_indexer = ARLArchiveIndexer(self.config("INDEX_DATA_FILE"))
            is_complete, metfiles = arl_indexer.get_input_files(date_naive, hours_to_run)
            if not is_complete:
                self.log.warn("Unable to find complete arl data for run date %s with a rum time of % hours." % (date_naive, hours_to_run))

        elif self.config("ARL_TWO_FILES_PER_MONTH", bool):
            self.log.info("Assuming two-file-per-month ARL archive structure.")
            month = 0
            firstHalf = 1
            secondHalf = 1
            while date <= met["dispersion_end"]:
                if date.day < 16 and firstHalf == 1:
                    halfMonth = '.001'
                    metglob = date.strftime(ARL_PATTERN) + halfMonth
                    metfiles += sorted(glob(metglob))
                    firstHalf = 0
                elif date.day >= 16 and secondHalf == 1:
                    halfMonth = '.002'
                    metglob = date.strftime(ARL_PATTERN) + halfMonth
                    metfiles += sorted(glob(metglob))
                    secondHalf = 0
                date += timedelta(days=1)

        else:
            self.log.info("Using arbitrary ARL file pattern with no additional assumptions.")
            metglob = date.strftime(ARL_PATTERN)
            metfiles += sorted(glob(metglob))

        self.log.info("Got %d ARL files" % len(metfiles))
        for f in metfiles:
            self.log.info("ARL file: %s " % os.path.basename(f))

        if not len(metfiles):
            if self.config("STOP_IF_NO_MET", bool):
                raise Exception("Found no matching ARL files. Stop.")
            self.log.warn("Found no matching ARL files; meteorological data are not available")
            self.log.debug("No ARL files matched '%s'", os.path.basename(ARL_PATTERN))
            self.set_output("met_info", met)
            return

        # HYSPLIT only allows up to 12 meteorological data files
        if len(metfiles) > 12:
            raise Exception("HYSPLIT only allows 12 met files...reduce HOURS_TO_RUN in configuration file")

        for arlfile in metfiles:
            if not context.file_exists(arlfile):
                raise IOError("Missing required file: %s" % arlfile)

            fileInfo, domainInfo = self.ARLsize(arlfile)

            if fileInfo["end"] >= met["dispersion_start"] and fileInfo["start"] <= met["dispersion_end"]:
                met["files"].append(fileInfo)
            else:
                self.log.debug("Ignoring file %s because it's outside the dispersion range",
                               os.path.basename(arlfile))

            if not len(met["files"]):
                self.log.warn("No matching ARL files fit the requested dispersion interval")
                self.set_output("met_info", met)
                return

        met_start = min([f["start"] for f in met["files"]])
        met_end = max(f["end"] for f in met["files"])

        self.log.log(SUMMARY, "Available meteorology: " + met_start.strftime('%Y%m%d %HZ') +
                      " to " + met_end.strftime('%Y%m%d %HZ'))

        if not ((met_start <= met["dispersion_start"]) and (met_end >= met["dispersion_start"])):
            raise Exception("Insufficient ARL data to run selected dispersion period")

        if met_end < met["dispersion_end"]:
            self.log.warn("WARNING: Insufficient ARL data to run full dispersion period; truncating dispersion")

        disp_end = min(met["dispersion_end"], met_end)
        disp_time = disp_end - met["dispersion_start"]
        disp_hours = ((disp_time.days * 86400) + disp_time.seconds) / 3600
        self.log.info("Dispersion will run for %d hours", disp_hours)

        met["met_start"] = met_start
        met["met_end"] = met_end
        met["file_type"] = "ARL"
        met["met_domain_info"] = domainInfo

        self.set_output("met_info", met)

    def ARLsize(self,f):
        """Retrieve ARL file information using arldata module"""

        arlfile = ARLGridFile(f)

        self.log.info("%s projection detected." % arlfile.metadata["projection"])

        fileInfo = construct_type("MetFileInfo")
        fileInfo["filename"] = arlfile.metadata["filename"]
        dt = arlfile.metadata["start_dt"]
        fileInfo["start"] = BSDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, UTC())
        dt = arlfile.metadata["end_dt"]
        fileInfo["end"] = BSDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, UTC())

        domainInfo = construct_type("MetDomainInfo")
        domainInfo["domainID"] = arlfile.metadata["projection"]
        domainInfo["lonC"] = arlfile.metadata["tangent_long"]
        domainInfo["latC"] = arlfile.metadata["tangent_lat"]
        domainInfo["alpha"] = arlfile.metadata["cone_angle"]
        domainInfo["beta"] = arlfile.metadata["cone_angle"]
        domainInfo["gamma"] = arlfile.metadata["tangent_long"]
        domainInfo["nxCRS"] = arlfile.metadata["num_x_pnts"]
        domainInfo["nyCRS"] = arlfile.metadata["num_y_pnts"]
        domainInfo["dxKM"] = arlfile.metadata["grid_size"]

        # Compute a bounding box that covers at least the full grid
        # in the projected coordinate system.  Do this by scanning
        # the grid boundaries.

        boundaryEW = [(i, j) for i in 0,arlfile.sizeX-1 for j in xrange(0,arlfile.sizeY)]
        boundaryNS = [(i, j) for j in 0,arlfile.sizeY-1 for i in xrange(0,arlfile.sizeX)]
        boundary_latlon = [arlfile.getLatLonByCell(i, j) for (i, j) in boundaryEW + boundaryNS]
        lats = [cell[0] for cell in boundary_latlon]
        lons = [cell[1] for cell in boundary_latlon]
        domainInfo["lat_min"] = min(lats)
        domainInfo["lat_max"] = max(lats)
        domainInfo["lon_min"] = min(lons)
        domainInfo["lon_max"] = max(lons)

        if arlfile.metadata["projection"] == "LatLon":
            self.log.warn("Setting CONUS bounds for ARL lat-lon grid.  Use USER_DEFINED_GRID to override.")
            domainInfo["lon_min"] = -130.0
            domainInfo["lon_max"] = -65.0
            domainInfo["lat_min"] = 20.0
            domainInfo["lat_max"] = 55.0

        return fileInfo, domainInfo

    def output_handler(self, logger, output, is_stderr):
        if is_stderr:
            logger.error(output)
            self.binary_output += output + "\n"
        else:
            self.binary_output += output + "\n"


class ARLLocalMet(Process):
    """ Extract fire-local meteorological data
    """

    def init(self):
        self.declare_input("met_info", "MetInfo")
        self.declare_input("fires", "FireInformation")
        self.declare_output("met_info", "MetInfo")
        self.declare_output("fires", "FireInformation")

    def run(self, context):
        met_info = self.get_input("met_info")
        fireInfo = self.get_input("fires")

        if met_info.file_type != "ARL":
            raise Exception("ARLLocalMet can only be used with ARL-format met data")

        # TO DO: This should be improved in a future version...
        self.log.info("Unable to extract local met from ARL data; elevation is undefined")
        for fireLoc in fireInfo.locations():
            fireLoc["elevation"] = 0

        self.set_output("met_info", met_info)
        self.set_output("fires", fireInfo)


class MM5ToARL(TrajectoryMet, DispersionMet):
    """ Convert MM5-format met data to ARL format
    """

    def init(self):
        self.declare_input("met_info", "MetInfo")
        self.declare_output("met_info", "MetInfo")

    def run(self, context):
        met_info = self.get_input("met_info")

        if not len(met_info["files"]):
            raise AssertionError("No input meteorological data available! Stop.")

        if not context.get_kept_file("hysplit.arl", met_info):
            self.log.info("Converting MM5 data into ARL format for the HYSPLIT model")

            mm5files = [f["filename"] for f in met_info["files"]]
            for mm5file in mm5files:
                context.link_file(mm5file)

            self.write_mm5toarl_inp(context, mm5files, "hysplit.arl")

            MM52ARL_BINARY = self.config("MM52ARL_BINARY")
            context.execute(MM52ARL_BINARY)
            context.archive_file("mm5toarl.inp")
            context.archive_file("CFG_MM5")
            context.keep_file("hysplit.arl", met_info)

        hysplit_arl = context.full_path("hysplit.arl")

        # Build new MetInfo object for output
        metInfo = construct_type("MetInfo", met_info)
        metFile = construct_type("MetFileInfo")
        metFile.filename = hysplit_arl
        metFile.start = metInfo.met_start
        metFile.end = metInfo.met_end
        metInfo.files = [metFile]
        metInfo.file_type = "ARL"

        if self.config("MM5_NEST", bool):
            if not len(met_info["files_nest"]):
                raise AssertionError("No nested input meteorological data available! Stop.")

            if not context.get_kept_file("hysplit_nest.arl", met_info):
                self.log.info("Converting Nested MM5 data into ARL format for the HYSPLIT model")

                mm5files = [f["filename"] for f in met_info["files_nest"]]
                for mm5file in mm5files:
                     context.link_file(mm5file)

                self.write_mm5toarl_inp(context, mm5files, "hysplit_nest.arl")

                MM52ARL_BINARY = self.config("MM52ARL_BINARY")
                context.execute(MM52ARL_BINARY)
                context.keep_file("hysplit_nest.arl", met_info)

            hysplit_nest_arl = context.full_path("hysplit_nest.arl")
            metFileNest = construct_type("MetFileInfo")
            metFileNest.filename = hysplit_nest_arl
            metFileNest.start = metInfo.met_start
            metFileNest.end = metInfo.met_end
            metInfo.files.append(metFileNest)

        # Write info to new metInfo file
        self.set_output("met_info", metInfo)

    def write_mm5toarl_inp(self, context, mm5data_filenames, outname):
        """ Write the mm5toarl.inp file """

        outfilename = context.full_path("mm5toarl.inp")
        with open(outfilename, "w") as outfile:
            outfile.write("%d\n" % len(mm5data_filenames)) # Number of Met Filenames
            for mm5file in mm5data_filenames:
                self.log.debug("Adding %s to arl file" % mm5file)
                outfile.write("%s\n" % os.path.basename(mm5file)) # Met input filenames
            outfile.write("%s\n" % outname)
        return outfilename


def getVerticalMethod(self):
    # Vertical motion choices:
    verticalChoices = dict(DATA=0, ISOB=1, ISEN=2, DENS=3, SIGMA=4, DIVERG=5, ETA=6)
    VERTICAL_METHOD = self.config("VERTICAL_METHOD")

    try:
        verticalMethod = verticalChoices[VERTICAL_METHOD]
    except KeyError:
        verticalMethod = verticalChoices["DATA"]

    return verticalMethod


class WRFToARL(TrajectoryMet, DispersionMet):
    """ Convert WRF-format met data to ARL format.
    
    This method uses the executable configured with WRFTOARL_BINARY
    to convert WRF NetCDF files to ARL formatted files one at a time
    and then concatenates them to create a single "hysplit.arl" file
    containing all met data.
    """

    def init(self):
        self.declare_input("met_info", "MetInfo")
        self.declare_output("met_info", "MetInfo")

    def run(self, context):
        met_info = self.get_input("met_info")

        WRFTOARL_BINARY = self.config("WRFTOARL_BINARY")

        hysplit_arl = context.full_path("hysplit.arl")

        if not len(met_info["files"]):
            raise AssertionError("No input meteorological data available! Stop.")

        if not context.get_kept_file("hysplit.arl", met_info):
            self.log.info("Converting WRF data into ARL format for the HYSPLIT model")

            # NOTE:  Each time WRFTOARL_BINARY is run it will generate WRFDATA.BIN
            # NOTE:  and WRFDATA.CFG.  WRFDATA.CFG does not change as long as the 
            # NOTE:  spatial domain stays the same.  So we need to create an empty 
            # NOTE:  "hysplit.arl" file where we concatenate all the individual
            # NOTE:  WRFDATA.BIN files.

            # TODO:  Do we need to clean up the WRFDATA.BIN and WRFDATA.CFG files?

            hysplit_arl_file = open(hysplit_arl, 'wb')

            wrffiles = [f["filename"] for f in met_info["files"]]
            for wrffile in wrffiles:
                context.link_file(wrffile)
                self.binary_output = ""
                context.execute(WRFTOARL_BINARY, os.path.basename(wrffile))
                # TODO:  Does binary_output contain the expected output?
                assert ("ERROR" not in self.binary_output), self.binary_output
                wrfdata_bin = context.full_path("WRFDATA.BIN")
                wrfdata_bin_file = open(wrfdata_bin, 'rb')
                copyfileobj(wrfdata_bin_file, hysplit_arl_file)
                wrfdata_bin_file.close()
                context.delete_file("WRFDATA.BIN")

            hysplit_arl_file.close()

            context.archive_file("WRFDATA.CFG")
            context.keep_file("hysplit.arl", met_info)

        # Build new MetInfo object
        metInfo = construct_type("MetInfo", met_info)
        metFile = construct_type("MetFileInfo")
        metFile.filename = hysplit_arl
        metFile.start = metInfo.met_start
        metFile.end = metInfo.met_end
        metInfo.files = [metFile]
        metInfo.file_type = "ARL"

        if self.config("WRF_NEST", bool):

            hysplit_nest_arl = context.full_path("hysplit_nest.arl")

            if not len(met_info["files_nest"]):
                raise AssertionError("No nested input meteorological data available! Stop.")

            if not context.get_kept_file("hysplit_nest.arl", met_info):
                self.log.info("Converting Nested WRF data into ARL format for the HYSPLIT model")

                hysplit_nest_arl_file = open(hysplit_nest_arl, 'wb')

                wrffiles = [f["filename"] for f in met_info["files_nest"]]
                for wrffile in wrffiles:
                    context.link_file(wrffile)
                    self.binary_output = ""
                    context.execute(WRFTOARL_BINARY, os.path.basename(wrffile))
                    # TODO:  Does binary_output contain the expected output?
                    assert ("ERROR" not in self.binary_output), self.binary_output
                    wrfdata_bin = context.full_path("WRFDATA.BIN")
                    wrfdata_bin_file = open(wrfdata_bin, 'rb')
                    copyfileobj(wrfdata_bin_file, hysplit_nest_arl_file)
                    wrfdata_bin_file.close()
                    context.delete_file("WRFDATA.BIN")

                hysplit_nest_arl_file.close()

                context.archive_file("WRFDATA.CFG")
                context.keep_file("hysplit_nest.arl", met_info)

            # Build new MetInfo object for output            
            metFileNest = construct_type("MetFileInfo")
            metFileNest.filename = hysplit_nest_arl
            metFileNest.start = metInfo.met_start
            metFileNest.end = metInfo.met_end
            metInfo.files.append(metFileNest)

        # Write info to new metInfo file
        self.set_output("met_info", metInfo)

    def output_handler(self, logger, output, is_stderr):
        if is_stderr:
            logger.error(output)
            self.binary_output += output + "\n"
        else:
            self.binary_output += output + "\n"


class HYSPLITTrajectory(Trajectory):
    """ HYSPLIT Trajectory model
    
    HYSPLIT Trajectory model version 4.9.
    """

    def run(self, context):
        self.log.info("Running the HYSPLIT49 Trajectory model")

        fireInfo = self.get_input("fires")
        met_info = self.get_input("met_info")

        if met_info.file_type != "ARL":
            raise Exception("HYSPLIT requires ARL-format meteorological data")

        hysplit_arl = met_info.files[0].filename

        # Ancillary data files (note: HYSPLIT49 balks if it can't find ASCDATA.CFG).
        ASCDATA_FILE = self.config("ASCDATA_FILE")
        LANDUSE_FILE = self.config("LANDUSE_FILE")
        ROUGLEN_FILE = self.config("ROUGLEN_FILE")
        context.link_file(ASCDATA_FILE)
        context.link_file(LANDUSE_FILE)
        context.link_file(ROUGLEN_FILE)

        HYSPLIT_BINARY = self.config("HYSPLIT_BINARY")
        MODEL_START_TIME = fireInfo["start_date"]
        HOURS_TO_RUN_TRAJECTORY = self.config("HOURS_TO_RUN_TRAJECTORY", int)
        NUM_CONSECUTIVE_TRAJECTORIES = self.config("NUM_CONSECUTIVE_TRAJECTORIES", int)
        modelTop = self.config("TOP_OF_MODEL_DOMAIN", float)

        verticalMethod = getVerticalMethod(self)

        for fireLoc in fireInfo.locations():
            context.push_dir(fireLoc["id"])
            context.link_file(hysplit_arl)

            fireLoc["metadata"]["extra:hysplit_files"] = dict()

            for hour in range(NUM_CONSECUTIVE_TRAJECTORIES):
                traj_datetime = MODEL_START_TIME + timedelta(hours=hour)

                basename = "%s.%s" % (fireLoc["id"], traj_datetime.strftime("%Y%m%d%H"))
                trjfilename = "%s.trj" % basename

                with open(context.full_path("CONTROL"), "w") as outfile:
                    outfile.write("%02d %02d %02d %02d\n" % (traj_datetime.year-2000, traj_datetime.month,
                                                             traj_datetime.day, traj_datetime.hour))
                    outfile.write("1\n")        # run one trajectory at a time
                    outfile.write("%s %s 10\n" % (fireLoc["latitude"], fireLoc["longitude"]))
                    outfile.write("%02d\n" % HOURS_TO_RUN_TRAJECTORY)
                    outfile.write("%d\n" % verticalMethod)  # method to calc vertical motion
                    outfile.write("%9.1f\n" % modelTop)     # top of model domain (meters?)
                    outfile.write("1\n")        # number of input data grids (met files)
                    outfile.write("./\n")
                    outfile.write("hysplit.arl\n")
                    outfile.write("./\n")
                    outfile.write("%s.trj\n" % basename)

                context.execute(HYSPLIT_BINARY)
                context.trash_file("CONTROL")

                fireLoc["metadata"]["extra:hysplit_files"][hour] = context.full_path(trjfilename)

            context.pop_dir()

        self.set_output("fires", fireInfo)


class OutputTrajectoryArchive(Process):
    def init(self):
        self.declare_input("fires", "FireInformation")

    def run(self, context):
        fireInfo = self.get_input("fires")
        output_file = os.path.join(self.config("OUTPUT_DIR"),
                                   self.config("TrajectoryTarballFile"))

        count = 0
        wroteLocs = 0
        wroteFiles = 0
        with contextlib.closing(tarfile.open(output_file, "w:gz")) as tar:
            for fireLoc in fireInfo.locations():
                count += 1
                if "extra:hysplit_files" in fireLoc["metadata"]:
                    wroteLocs += 1
                    for i in fireLoc["metadata"]["extra:hysplit_files"]:
                        realpath = fireLoc["metadata"]["extra:hysplit_files"][i]
                        if not os.path.exists(realpath):
                            continue
                        arcpath = os.path.basename(realpath)
                        tar.add(realpath, arcpath)
                        wroteFiles += 1

        if count > 0 and wroteLocs == 0:
            self.log.debug("No fires contain trajectory information; skip...")
        elif wroteLocs > 0:
            skipped = count - wroteLocs
            if skipped > 0:
                self.log.info("Wrote %s files for %s fires (%s fires had no trajectories)", wroteFiles, wroteLocs, skipped)
            else:
                self.log.info("Wrote %s files for %s fires", wroteFiles, wroteLocs)


class HYSPLITDispersion(Dispersion):
    """ HYSPLIT Dispersion model

    HYSPLIT Concentration model version 4.9
    """

    def run(self, context):
        self.log.info("Running the HYSPLIT49 Dispersion model")

        fireInfo = self.get_input("fires")
        metInfo = self.get_input("met_info")

        arlfiles = [f["filename"] for f in metInfo["files"]]
        for arlfile in arlfiles:
            self.log.info(arlfile)

        if metInfo.file_type != "ARL":
            raise Exception("HYSPLIT requires ARL-format meteorological data")

        for f in metInfo.files:
            context.link_file(f.filename)

        # Ancillary data files (note: HYSPLIT49 balks if it can't find ASCDATA.CFG).
        ASCDATA_FILE = self.config("ASCDATA_FILE")
        LANDUSE_FILE = self.config("LANDUSE_FILE")
        ROUGLEN_FILE = self.config("ROUGLEN_FILE")
        context.link_file(ASCDATA_FILE)
        context.link_file(LANDUSE_FILE)
        context.link_file(ROUGLEN_FILE)

        HYSPLIT_BINARY = self.config("HYSPLIT_BINARY")
        HYSPLIT_MPI_BINARY = self.config("HYSPLIT_MPI_BINARY")
        HYSPLIT2NETCDF_BINARY = self.config("HYSPLIT2NETCDF_BINARY")

        # Number of quantiles in vertical emissions allocation scheme
        NQUANTILES = 20

        # Reduction factor for vertical emissions layer allocation
        reductionFactor, num_output_quantiles = self.getReductionFactor(NQUANTILES)

        modelStart = metInfo.dispersion_start
        modelEnd = min(metInfo.dispersion_end, metInfo.met_end)
        dur = modelEnd - modelStart
        hoursToRun = ((dur.days * 86400) + dur.seconds) / 3600

        filteredFires = list(self.filterFires(fireInfo))

        if(len(filteredFires) == 0):
            raise Exception("No fires have data for HYSPLIT dispersion")

        emissionsFile = context.full_path("EMISS.CFG")
        controlFile = context.full_path("CONTROL")
        setupFile = context.full_path("SETUP.CFG")
        messageFiles = [context.full_path("MESSAGE")]
        outputConcFile = context.full_path("hysplit.con")
        outputFile = context.full_path("hysplit_conc.nc")

        # Prepare for an MPI run
        if self.config("MPI", bool):
            NCPUS = self.config("NCPUS", int)
            self.log.info("Running MPI HYSPLIT with %s processors." % NCPUS)
            if NCPUS < 1:
                self.log.warn("Invalid NCPUS specified...resetting NCPUS to 1 for this run.")
                NCPUS = 1
            mpiexec = self.config("MPIEXEC")
            messageFiles = ["MESSAGE.%3.3i" % (i+1) for i in range(NCPUS)]
            pardumpFiles = ["PARDUMP.%3.3i" % (i+1) for i in range(NCPUS)]
            if not context.file_exists(mpiexec):
                raise AssertionError("Failed to find %s. Check MPIEXEC setting and/or your MPICH2 installation." % mpiexec)
            if not context.file_exists(HYSPLIT_MPI_BINARY):
                raise AssertionError("HYSPLIT MPI executable %s not found." % HYSPLIT_MPI_BINARY)
        else:
            NCPUS = 1
            
        # Default value for NINIT for use in set up file.  0 equals no particle initialization
        ninit_val = "0"

        if self.config("READ_INIT_FILE", bool):
           parinit_files = [ os.path.join(self.config("DISPERSION_FOLDER"), "PARINIT") ]
           if self.config("MPI", bool):
               parinit_files = [ os.path.join(self.config("DISPERSION_FOLDER"), "PARINIT.%3.3i" % (i+1)) for i in range(NCPUS) ]
           if not context.file_exists(parinit_files[0]):
              if self.config("STOP_IF_NO_PARINIT", bool):
                 raise Exception("Found no matching particle initialization files. Stop.")
              else:
                 self.log.warn("No matching particle initialization file found; Using no particle initialization")
                 self.log.debug("Particle initialization file not found '%s'", parinit_files[0])
           else:
              for f in parinit_files:
                  context.link_file(f)
                  self.log.info("Using particle initialization file %s" % f)
              ninit_val = "1"

        self.writeEmissions(filteredFires, modelStart, hoursToRun, emissionsFile, reductionFactor, num_output_quantiles)
        self.writeControlFile(filteredFires, metInfo, modelStart, hoursToRun, controlFile, outputConcFile, num_output_quantiles)
        self.writeSetupFile(filteredFires, modelStart, emissionsFile, setupFile, num_output_quantiles, ninit_val, NCPUS)

        # Copy in the user_defined SETUP.CFG file or write a new one
        HYSPLIT_SETUP_FILE = self.config("HYSPLIT_SETUP_FILE")
        if HYSPLIT_SETUP_FILE != None:
            self.log.debug("Copying HYSPLIT SETUP file from %s" % (HYSPLIT_SETUP_FILE))
            config_setup_file = open(HYSPLIT_SETUP_FILE, 'rb')
            setup_file = open(setupFile, 'wb')
            copyfileobj(config_setup_file, setup_file)
            config_setup_file.close()
            setup_file.close()
        else:
            self.writeSetupFile(filteredFires, modelStart, emissionsFile, setupFile, num_output_quantiles, ninit_val, NCPUS)

        # Run HYSPLIT
        if self.config("MPI", bool):
            context.execute(mpiexec, "-n", str(NCPUS), HYSPLIT_MPI_BINARY)
        else:  # standard serial run
            context.execute(HYSPLIT_BINARY)

        if not os.path.exists(outputConcFile):
            raise AssertionError("HYSPLIT failed, check MESSAGE file for details")

        self.log.info("Converting HYSPLIT output to NetCDF format")
        context.execute(HYSPLIT2NETCDF_BINARY,
            "-I" + outputConcFile,
            "-O" + os.path.basename(outputFile),
            "-X1000000.0",  # Scale factor to convert from grams to micrograms
            "-D1",  # Debug flag
            "-L-1"  # Lx is x layers. x=-1 for all layers...breaks KML output for multiple layers
            )

        if not os.path.exists(outputFile):
            raise AssertionError("Unable to convert HYSPLIT concentration file to NetCDF format")

        # DispersionData output
        dispersionData = construct_type("DispersionData")
        dispersionData["grid_filetype"] = "NETCDF"
        dispersionData["grid_filename"] = outputFile
        dispersionData["parameters"] = {"pm25": "PM25"}
        dispersionData["start_time"] = modelStart
        dispersionData["hours"] = hoursToRun
        fireInfo.dispersion = dispersionData
        self.set_output("fires", fireInfo)

        # Archive data files
        context.archive_file(emissionsFile)
        context.archive_file(controlFile)
        context.archive_file(setupFile)
        for f in messageFiles:
            context.archive_file(f)
        if self.config("MAKE_INIT_FILE", bool):
            if self.config("MPI", bool):
                for f in pardumpFiles:
                    context.archive_file(f)
                    context.copy_file(context.full_path(f),self.config("OUTPUT_DIR"))
            else:
                context.archive_file(context.full_path("PARDUMP"))
                context.copy_file(context.full_path("PARDUMP"),self.config("OUTPUT_DIR") + "/PARDUMP_"+ self.config("DATE"))

    def getReductionFactor(self,nquantiles):
        """Retrieve factor for reducing the number of vertical emission levels"""

        #    Ensure the factor divides evenly into the number of quantiles.
        #    For the 20 quantile vertical accounting scheme, the following values are appropriate:
        #       reductionFactor = 1 .... 20 emission levels (no change from the original scheme)
        #       reductionFactor = 2......10 emission levels
        #       reductionFactor = 4......5 emission levels
        #       reductionFactor = 5......4 emission levels
        #       reductionFactor = 10.....2 emission levels
        #       reductionFactor = 20.....1 emission level

        # Pull reduction factor from user input
        reductionFactor = self.config("VERTICAL_EMISLEVELS_REDUCTION_FACTOR")
        reductionFactor = int(reductionFactor)

        # Ensure a valid reduction factor
        if reductionFactor > nquantiles:
            reductionFactor = nquantiles
            self.log.debug("VERTICAL_EMISLEVELS_REDUCTION_FACTOR reset to %s" % str(nquantiles))
        elif reductionFactor <= 0:
            reductionFactor = 1
            self.log.debug("VERTICAL_EMISLEVELS_REDUCTION_FACTOR reset to 1")
        while (nquantiles % reductionFactor) != 0:  # make sure factor evenly divides into the number of quantiles
            reductionFactor -= 1
            self.log.debug("VERTICAL_EMISLEVELS_REDUCTION_FACTOR reset to %s" % str(reductionFactor))

        num_output_quantiles = nquantiles/reductionFactor

        if reductionFactor != 1:
            self.log.info("Number of vertical emission levels reduced by factor of %s" % str(reductionFactor))
            self.log.info("Number of vertical emission quantiles will be %s" % str(num_output_quantiles))

        return reductionFactor,num_output_quantiles

    def filterFires(self, fireInfo):
        for fireLoc in fireInfo.locations():
            if fireLoc.time_profile is None:
                self.log.debug("Fire %s has no time profile data; skip...", fireLoc.id)
                continue

            if fireLoc.plume_rise is None:
                self.log.debug("Fire %s has no plume rise data; skip...", fireLoc.id)
                continue

            if fireLoc.emissions is None:
                self.log.debug("Fire %s has no emissions data; skip...", fireLoc.id)
                continue

            if fireLoc.emissions.sum("heat") < 1.0e-6:
                self.log.debug("Fire %s has less than 1.0e-6 total heat; skip...", fireLoc.id)
                continue

            yield fireLoc

    def writeEmissions(self, filteredFires, modelStart, hoursToRun, emissionsFile, reductionFactor, num_quantiles):
        # Note: HYSPLIT can accept concentrations in any units, but for 
        # consistency with CALPUFF and other dispersion models, we convert to 
        # grams in the emissions file.
        GRAMS_PER_TON = 907184.74

        # Conversion factor for fire size
        SQUARE_METERS_PER_ACRE = 4046.8726

        # A value slightly above ground level at which to inject smoldering
        # emissions into the model.
        SMOLDER_HEIGHT = self.config("SMOLDER_HEIGHT", float)

        with open(emissionsFile, "w") as emis:
            # HYSPLIT skips past the first two records, so these are for comment purposes only
            emis.write("emissions group header: YYYY MM DD HH QINC NUMBER\n")
            emis.write("each emission's source: YYYY MM DD HH MM DUR_HHMM LAT LON RATE AREA HEAT\n")

            # Loop through the timesteps
            for hour in range(hoursToRun):
                dt = modelStart + timedelta(hours=hour)
                dt_str = dt.strftime("%y %m %d %H")

                num_fires = len(filteredFires)
                #num_heights = 21 # 20 quantile gaps, plus ground level
                num_heights = num_quantiles + 1
                num_sources = num_fires * num_heights

                # TODO: What is this and what does it do?
                # A reasonable guess would be that it means a time increment of 1 hour
                qinc = 1

                # Write the header line for this timestep
                emis.write("%s %02d %04d\n" % (dt_str, qinc, num_sources))

                noEmis = 0

                # Loop through the fire locations
                for fireLoc in filteredFires:
                    dummy = False

                    # Get some properties from the fire location
                    lat = fireLoc.latitude
                    lon = fireLoc.longitude

                    # Figure out what index (h) to use into our hourly arrays of data,
                    # based on the hour in our outer loop and the fireLoc's available
                    # data.
                    padding = fireLoc.date_time - modelStart
                    padding_hours = ((padding.days * 86400) + padding.seconds) / 3600
                    num_hours = min(len(fireLoc.emissions.heat), len(fireLoc.plume_rise.hours))
                    h = hour - padding_hours

                    # If we don't have real data for the given timestep, we apparently need
                    # to stick in dummy records anyway (so we have the correct number of sources).

                    if h < 0 or h >= num_hours:
                        self.log.debug("Fire %s has no emissions for hour %s", fireLoc.id, hour)
                        noEmis += 1
                        dummy = True

                    area_meters = 0.0
                    smoldering_fraction = 0.0
                    pm25_injected = 0.0
                    if not dummy:
                        # Extract the fraction of area burned in this timestep, and
                        # convert it from acres to square meters.
                        area = fireLoc.area * fireLoc.time_profile.area_fract[h]
                        area_meters = area * SQUARE_METERS_PER_ACRE

                        smoldering_fraction = fireLoc.plume_rise.hours[h].smoldering_fraction
                        # Total PM2.5 emitted at this timestep (grams)
                        pm25_emitted = fireLoc.emissions.pm25[h].sum() * GRAMS_PER_TON
                        # Total PM2.5 smoldering (not lofted in the plume)
                        pm25_injected = pm25_emitted * smoldering_fraction

                    entrainment_fraction = 1.0 - smoldering_fraction

                    # We don't assign any heat, so the PM2.5 mass isn't lofted
                    # any higher.  This is because we are assigning explicit
                    # heights from the plume rise.
                    heat = 0.0

                    # Inject the smoldering fraction of the emissions at ground level
                    # (SMOLDER_HEIGHT represents a value slightly above ground level)
                    height_meters = SMOLDER_HEIGHT

                    # Write the smoldering record to the file
                    record_fmt = "%s 00 0100 %8.4f %9.4f %6.0f %7.2f %7.2f %15.2f\n"
                    emis.write(record_fmt % (dt_str, lat, lon, height_meters, pm25_injected, area_meters, heat))

                    #for pct in range(0, 100, 5):
                    for pct in range(0, 100, reductionFactor*5):
                        height_meters = 0.0
                        pm25_injected = 0.0

                        if not dummy:
                            # Loop through the heights (20 quantiles of smoke density)
                            # For the unreduced case, we loop through 20 quantiles, but we have 
                            # 21 quantile-edge measurements.  So for each 
                            # quantile gap, we need to find a point halfway 
                            # between the two edges and inject 1/20th of the
                            # total emissions there.

                            # KJC optimization...
                            # Reduce the number of vertical emission levels by a reduction factor
                            # and place the appropriate fraction of emissions at each level.
                            # ReductionFactor MUST evenly divide into the number of quantiles

                            lower_height = fireLoc.plume_rise.hours[h]["percentile_%03d" % (pct)]
                            #upper_height = fireLoc.plume_rise.hours[h]["percentile_%03d" % (pct + 5)]
                            upper_height = fireLoc.plume_rise.hours[h]["percentile_%03d" % (pct + (reductionFactor*5))]
                            if reductionFactor == 1:
                                height_meters = (lower_height + upper_height) / 2.0  # original approach
                            else:
                                 height_meters = upper_height # top-edge approach
                            # Total PM2.5 entrained (lofted in the plume)
                            pm25_entrained = pm25_emitted * entrainment_fraction
                            # Inject the proper fraction of the entrained PM2.5 in each quantile gap.
                            #pm25_injected = pm25_entrained * 0.05  # 1/20 = 0.05
                            pm25_injected = pm25_entrained * (float(reductionFactor)/float(num_quantiles))

                        # Write the record to the file
                        emis.write(record_fmt % (dt_str, lat, lon, height_meters, pm25_injected, area_meters, heat))

                if noEmis > 0:
                    self.log.debug("%d of %d fires had no emissions for hour %d", noEmis, num_fires, hour)

    def writeControlFile(self, filteredFires, metInfo, modelStart, hoursToRun, controlFile, concFile, num_quantiles):
        num_fires = len(filteredFires)
        num_heights = num_quantiles + 1  # number of quantiles used, plus ground level
        num_sources = num_fires * num_heights

        # An arbitrary height value.  Used for the default source height 
        # in the CONTROL file.  This can be anything we want, because 
        # the actual source heights are overridden in the EMISS.CFG file.
        sourceHeight = 15.0

        verticalMethod = getVerticalMethod(self)

        # Height of the top of the model domain
        modelTop = self.config("TOP_OF_MODEL_DOMAIN", float)

        modelEnd = modelStart + timedelta(hours=hoursToRun)

        # Build the vertical Levels string
        verticalLevels = self.config("VERTICAL_LEVELS")
        levels = [int(x) for x in verticalLevels.split()]
        numLevels = len(levels)
        verticalLevels = " ".join(str(x) for x in levels)

        # Warn about multiple sampling grid levels and KML/PNG image generation
        if numLevels > 1:
            self.log.warn("KML and PNG images will be empty since more than 1 vertical level is selected")

        if self.config("USER_DEFINED_GRID", bool):
            # User settings that can override the default concentration grid info
            self.log.info("User-defined sampling/concentration grid invoked")
            centerLat = self.config("CENTER_LATITUDE", float)
            centerLon = self.config("CENTER_LONGITUDE", float)
            widthLon = self.config("WIDTH_LONGITUDE", float)
            heightLat = self.config("HEIGHT_LATITUDE", float)
            spacingLon = self.config("SPACING_LONGITUDE", float)
            spacingLat = self.config("SPACING_LATITUDE", float)
        else:
            # Calculate output concentration grid parameters.
            # Ensure the receptor spacing divides nicely into the grid width and height,
            # and that the grid center will be a receptor point (i.e., nx, ny will be ODD).
            self.log.info("Automatic sampling/concentration grid invoked")

            projection = metInfo.met_domain_info.domainID
            grid_spacing_km = metInfo.met_domain_info.dxKM
            lat_min = metInfo.met_domain_info.lat_min
            lat_max = metInfo.met_domain_info.lat_max
            lon_min = metInfo.met_domain_info.lon_min
            lon_max = metInfo.met_domain_info.lon_max
            lat_center = (lat_min + lat_max) / 2
            spacing = grid_spacing_km / ( 111.32 * math.cos(lat_center*math.pi/180.0) )
            if projection == "LatLon":
                spacing = grid_spacing_km  # degrees

            # Build sampling grid parameters in scaled integer form
            SCALE = 100
            lat_min_s = int(lat_min*SCALE)
            lat_max_s = int(lat_max*SCALE)
            lon_min_s = int(lon_min*SCALE)
            lon_max_s = int(lon_max*SCALE)
            spacing_s = int(spacing*SCALE)

            lat_count = (lat_max_s - lat_min_s) / spacing_s
            lat_count += 1 if lat_count % 2 == 0 else 0  # lat_count should be odd
            lat_max_s = lat_min_s + ((lat_count-1) * spacing_s)

            lon_count = (lon_max_s - lon_min_s) / spacing_s
            lon_count += 1 if lon_count % 2 == 0 else 0  # lon_count should be odd
            lon_max_s = lon_min_s + ((lon_count-1) * spacing_s)
            self.log.info("HYSPLIT grid DIMENSIONS will be %s by %s" % (lon_count, lat_count))

            spacingLon = float(spacing_s)/SCALE
            spacingLat = spacingLon
            centerLon = float((lon_min_s + lon_max_s) / 2) / SCALE
            centerLat = float((lat_min_s + lat_max_s) / 2) / SCALE
            widthLon = float(lon_max_s - lon_min_s) / SCALE
            heightLat = float(lat_max_s - lat_min_s) / SCALE

        # Decrease the grid resolution based on number of fires
        if self.config("OPTIMIZE_GRID_RESOLUTION", bool):
            self.log.info("Grid resolution adjustment option invoked")
            minSpacingLon = spacingLon
            minSpacingLat = spacingLat
            maxSpacingLon = self.config("MAX_SPACING_LONGITUDE", float)
            maxSpacingLat = self.config("MAX_SPACING_LATITUDE", float)
            fireIntervals = self.config("FIRE_INTERVALS")
            intervals = sorted([int(x) for x in fireIntervals.split()])

            # Maximum grid spacing cannot be smaller than the minimum grid spacing
            if maxSpacingLon < minSpacingLon:
                maxSpacingLon = minSpacingLon
                self.log.debug("maxSpacingLon > minSpacingLon...longitude grid spacing will not be adjusted")
            if maxSpacingLat < minSpacingLat:
                maxSpacingLat = minSpacingLat
                self.log.debug("maxSpacingLat > minSpacingLat...latitude grid spacing will not be adjusted")

            # Throw out negative intervals
            intervals = [x for x in intervals if x >= 0]

            if len(intervals) == 0:
                intervals = [0,num_fires]
                self.log.debug("FIRE_INTERVALS had no values >= 0...grid spacing will not be adjusted")

            # First bin should always start with zero
            if intervals[0] != 0:
                intervals.insert(0,0)
                self.log.debug("Zero added to the beginning of FIRE_INTERVALS list")

            # must always have at least 2 intervals
            if len(intervals) < 2:
                intervals = [0,num_fires]
                self.log.debug("Need at least two FIRE_INTERVALS...grid spacing will not be adjusted")

            # Increase the grid spacing depending on number of fires
            i = 0
            numBins = len(intervals)
            rangeSpacingLat = (maxSpacingLat - minSpacingLat)/(numBins - 1)
            rangeSpacingLon = (maxSpacingLon - minSpacingLon)/(numBins - 1)
            for interval in intervals:
                if num_fires > interval:
                    spacingLat = minSpacingLat + (i * rangeSpacingLat)
                    spacingLon = minSpacingLon + (i * rangeSpacingLon)
                    i += 1
                self.log.debug("Lon,Lat grid spacing for interval %d adjusted to %f,%f" % (interval,spacingLon,spacingLat))
            self.log.info("Lon/Lat grid spacing for %d fires will be %f,%f" % (num_fires,spacingLon,spacingLat))

        # Note: Due to differences in projections, the dimensions of this
        #       output grid are conservatively large.
        self.log.info("HYSPLIT grid CENTER_LATITUDE = %s" % centerLat)
        self.log.info("HYSPLIT grid CENTER_LONGITUDE = %s" % centerLon)
        self.log.info("HYSPLIT grid HEIGHT_LATITUDE = %s" % heightLat)
        self.log.info("HYSPLIT grid WIDTH_LONGITUDE = %s" % widthLon)
        self.log.info("HYSPLIT grid SPACING_LATITUDE = %s" % spacingLat)
        self.log.info("HYSPLIT grid SPACING_LONGITUDE = %s" % spacingLon)

        with open(controlFile, "w") as f:
            # Starting time (year, month, day hour)
            f.write(modelStart.strftime("%y %m %d %H") + "\n")

            # Number of sources
            f.write("%d\n" % num_sources)

            # Source locations
            for fireLoc in filteredFires:
                for height in range(num_heights):
                    f.write("%9.3f %9.3f %9.3f\n" % (fireLoc.latitude, fireLoc.longitude, sourceHeight))

            # Total run time (hours)
            f.write("%04d\n" % hoursToRun)

            # Method to calculate vertical motion
            f.write("%d\n" % verticalMethod)

            # Top of model domain
            f.write("%9.1f\n" % modelTop)

            # Number of input data grids (met files)
            f.write("%d\n" % len(metInfo.files))
            # Directory for input data grid and met file name
            for info in metInfo.files:
                f.write("./\n")
                f.write("%s\n" % os.path.basename(info.filename))

            # Number of pollutants = 1 (only modeling PM2.5 for now)
            f.write("1\n")
            # Pollutant ID (4 characters)
            f.write("PM25\n")
            # Emissions rate (per hour) (Ken's code says "Emissions source strength (mass per second)" -- which is right?)
            f.write("0.001\n")
            # Duration of emissions (hours)
            f.write(" %9.3f\n" % hoursToRun)
            # Source release start time (year, month, day, hour, minute)
            f.write("%s\n" % modelStart.strftime("%y %m %d %H %M"))

            # Number of simultaneous concentration grids
            f.write("1\n")

            # NOTE: The size of the output concentration grid is specified 
            # here, but it appears that the ICHEM=4 option in the SETUP.CFG 
            # file may override these settings and make the sampling grid 
            # correspond to the input met grid instead...
            # But Ken's testing seems to indicate that this is not the case...          

            # Sampling grid center location (latitude, longitude)
            f.write("%9.3f %9.3f\n" % (centerLat, centerLon))
            # Sampling grid spacing (degrees latitude and longitude)
            f.write("%9.3f %9.3f\n" % (spacingLat, spacingLon))
            # Sampling grid span (degrees latitude and longitude)
            f.write("%9.3f %9.3f\n" % (heightLat, widthLon))

            # Directory of concentration output file
            f.write("./\n")
            # Filename of concentration output file
            f.write("%s\n" % os.path.basename(concFile))

            # Number of vertical concentration levels in output sampling grid
            f.write("%d\n" % numLevels)
            # Height of each sampling level in meters AGL
            f.write("%s\n" % verticalLevels)

            # Sampling start time (year month day hour minute)
            f.write("%s\n" % modelStart.strftime("%y %m %d %H %M"))
            # Sampling stop time (year month day hour minute)
            f.write("%s\n" % modelEnd.strftime("%y %m %d %H %M"))
            # Sampling interval (type hour minute)
            f.write("0 1 00\n") # Sampling interval:  type hour minute.  A type of 0 gives an average over the interval.

            # Number of pollutants undergoing deposition
            f.write("1\n") # only modeling PM2.5 for now

            # Particle diameter (um), density (g/cc), shape
            f.write("1.0 1.0 1.0\n")

            # Dry deposition: 
            #    deposition velocity (m/s), 
            #    molecular weight (g/mol),
            #    surface reactivity ratio, 
            #    diffusivity ratio,
            #    effective Henry's constant
            f.write("0.0 0.0 0.0 0.0 0.0\n")

            # Wet deposition (gases):
            #     actual Henry's constant (M/atm),
            #     in-cloud scavenging ratio (L/L),
            #     below-cloud scavenging coefficient (1/s)
            f.write("0.0 0.0 0.0\n")

            # Radioactive decay half-life (days)
            f.write("0.0\n")

            # Pollutant deposition resuspension constant (1/m)
            f.write("0.0\n")

    def writeSetupFile(self, filteredFires, modelStart, emissionsFile, setupFile, num_quantiles, ninit_val, ncpus):
        # Advanced setup options
        # adapted from Robert's HysplitGFS Perl script        

        khmax_val = int(self.config("KHMAX"))
        ndump_val = int(self.config("NDUMP"))
        ncycl_val = int(self.config("NCYCL"))
        dump_datetime = modelStart + timedelta(hours=ndump_val)

        num_fires = len(filteredFires)
        num_heights = num_quantiles + 1
        num_sources = num_fires * num_heights

        max_particles = (num_sources * 1000) / ncpus

        with open(setupFile, "w") as f:
            f.write("&SETUP\n")

            # ichem: i'm only really interested in ichem = 4 in which case it causes
            #        the hysplit concgrid to be roughly the same as the met grid
            # -- But Ken says it may not work as advertised...
            #f.write("  ICHEM = 4,\n")

            # qcycle: the number of hours between emission start cycles
            f.write("  QCYCLE = 1.0,\n")

            # mgmin: a run once complained and said i need to reaise this variable to
            #        some value around what i have here...it has something to do with
            #        the minimum size (in grid units) of the met sub-grib.
            f.write("  MGMIN = 750,\n")

            # maxpar: max number of particles that are allowed to be active at one time
            f.write("  MAXPAR = %d,\n" % max_particles)

            # numpar: number of particles (or puffs) permited than can be released
            #         during one time step
            f.write("  NUMPAR = %d,\n" % num_sources)

            # khmax: maximum particle duration in terms of hours after relase
            f.write("  KHMAX = %d,\n" % khmax_val)

            # initd: # 0 - Horizontal and Vertical Particle
            #          1 - Horizontal Gaussian Puff, Vertical Top Hat Puff
            #          2 - Horizontal and Vertical Top Hat Puff
            #          3 - Horizontal Gaussian Puff, Vertical Particle
            #          4 - Horizontal Top-Hat Puff, Vertical Particle (default)
            f.write("  INITD = 1,\n")

            # make the 'smoke initizilaztion' files?
            # pinfp: particle initialization file (see also ninit)
            if self.config("READ_INIT_FILE", bool):
               f.write("  PINPF = \"PARINIT\",\n")

            # ninit: (used along side pinpf) sets the type of initialization...
            #          0 - no initialzation (even if files are present)
            #          1 = read pinpf file only once at initialization time
            #          2 = check each hour, if there is a match then read those values in
            #          3 = like '2' but replace emissions instead of adding to existing
            #              particles
            f.write("  NINIT = %s,\n" % ninit_val)

            # poutf: particle output/dump file
            if self.config("MAKE_INIT_FILE", bool):
                f.write("  POUTF = \"PARDUMP\",\n")
                self.log.info("Dumping particles to PARDUMP starting at %s every %s hours" % (dump_datetime, ncycl_val))

            # ndump: when/how often to dump a poutf file negative values indicate to
            #        just one  create just one 'restart' file at abs(hours) after the
            #        model start
            if self.config("MAKE_INIT_FILE", bool):
                f.write("  NDUMP = %d,\n" % ndump_val)

            # ncycl: set the interval at which time a pardump file is written after the
            #        1st file (which is first created at T = ndump hours after the
            #        start of the model simulation 
            if self.config("MAKE_INIT_FILE", bool):
                f.write("  NCYCL = %d,\n" % ncycl_val)

            # efile: the name of the emissions info (used to vary emission rate etc (and
            #        can also be used to change emissions time
            f.write("  EFILE = \"%s\",\n" % os.path.basename(emissionsFile))

            f.write("&END\n")
