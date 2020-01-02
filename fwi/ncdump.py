from netCDF4 import Dataset
import textwrap
import json
import click


def ncdump(nc_fid, verbose=True):
    '''
    ncdump outputs dimensions, variables and their attribute information.
    The information is similar to that of NCAR's ncdump utility.
    ncdump requires a valid instance of Dataset.
    Parameters
    ----------
    nc_fid : netCDF4.Dataset
        A netCDF4 dateset object
    verbose : Boolean
        whether or not nc_attrs, nc_dims, and nc_vars are printed
    Returns
    -------
    final_dict: dict
        dictionary with json structure of netcdf file and attributes
    if verbose=True, dictionary is both printed to screen
    '''
    ######
    def print_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key
        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        try:
            print("\t\ttype:", repr(nc_fid.variables[key].dtype))
            for ncattr in nc_fid.variables[key].ncattrs():
                print('\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr)))
        except KeyError:
            print("\t\tWARNING: %s does not contain variable attributes" % key)
        return None
######

    def save_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key
        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        save_dict = {}
        try:
            the_dtype = repr(nc_fid.variables[key].dtype)
            var_list = []

            for ncattr in nc_fid.variables[key].ncattrs():
                save_dict[ncattr] = repr(
                    nc_fid.variables[key].getncattr(ncattr))
        except KeyError:
            save_dict = None
            the_dtype = None
        var_dict = {'dtype': the_dtype, 'var_attrs': save_dict}
        return {key: var_dict}

    def save_global():
        """
        retrieve all global metadata
        """
        nc_attrs = nc_fid.ncattrs()
        attr_dict = {}
        for nc_attr in nc_attrs:
            attr_dict[nc_attr] = repr(nc_fid.getncattr(nc_attr))
        nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
        dim_dict = {}
        for dim in nc_dims:
            dim_len = int(len(nc_fid.dimensions[dim]))
            dim_attrs = save_ncattr(dim)
            dim_dict[dim] = {'size': dim_len, 'attrs': dim_attrs}
        global_dict = {'dimensions': dim_dict, 'attributes': attr_dict}
        return global_dict

    def save_groups():
        group_name = "root"
        groups = [(group_name, nc_fid)]
        groups_other = list(nc_fid.groups.items())
        groups.extend(groups_other)
        group_dict = {}
        for group_name, group in groups:
            the_group = {}
            nc_vars = [var for var in group.variables]  # list of nc variables
            for var in nc_vars:
                if var not in nc_dims:
                    the_group[var] = save_ncattr(var)
                    the_group[var]['dimensions'] = group.variables[
                        var].dimensions
                    the_group[var]['size'] = int(group.variables[var].size)
            group_dict[group_name] = the_group
        return group_dict


######
# NetCDF global attributes

    nc_attrs = nc_fid.ncattrs()
    if verbose:
        print("NetCDF Global Attributes:")
        for nc_attr in nc_attrs:
            print('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verbose:
        print("NetCDF dimension information:")
        for dim in nc_dims:
            print("\tName:", dim)
            print("\t\tsize:", len(nc_fid.dimensions[dim]))
            print_ncattr(dim)
    # Variable information.

    if verbose:
        group_name = "root"
        groups = [(group_name, nc_fid)]
        groups_other = list(nc_fid.groups.items())
        groups.extend(groups_other)
        for group_name, group in groups:
            print(f"NetCDF variable information for group {group_name}:")
            nc_vars = [var for var in group.variables]  # list of nc variables
            for var in nc_vars:
                if var not in nc_dims:
                    print('\tName:', var)
                    print("\t\tdimensions:", group.variables[var].dimensions)
                    print("\t\tsize:", group.variables[var].size)
                    print_ncattr(var)
    final_dict = {'global_attrs': save_global(), 'group_attrs': save_groups()}
    return final_dict


@click.command()
@click.argument("ncfile", type=str, nargs=1)
@click.option('--outfile',
              type=click.File('w'),
              nargs=1,
              default="output.json",
              help="json file for attributes output",
              show_default=True)
@click.option('--verbose/--no-verbose',default=True,help="print to screen")
def main(ncfile, outfile,verbose):
    with Dataset(ncfile) as nc_in:
        out = ncdump(nc_in,verbose)
        json.dump(out, outfile, indent=4)


if __name__ == "__main__":
    main()