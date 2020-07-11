    
    var firewx_stns = L.tileLayer.wms('https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms', {
        layers: 'public:firewx_stns_2018',
        format: 'image/png',
        transparent: true,
        attribution: "Weather data © 2012 IEM Nexrad"
    }).setZIndex(2000);
    
    
    