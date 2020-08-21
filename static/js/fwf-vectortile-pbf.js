
var vectorStyles = {
    water: {	// Apply these options to the "water" layer...
      fill: true,
      weight: 1,
      fillColor: '#06cccc',
      color: '#06cccc',
      fillOpacity: 0.2,
      opacity: 0.4,
    },
    transportation: {	// Apply these options to the "transportation" layer...
      weight: 0.5,
      color: '#f2b648',
      fillOpacity: 0.2,
      opacity: 0.4,
    },
};

var openmaptilesUrl = "https://api.maptiler.com/tiles/v3/{z}/{x}/{y}.pbf?key={key}";

var openMapTilesLayer = L.vectorGrid.protobuf(openMapTilesUrl, {
  vectorTileLayerStyles: vectorStyles,
  subdomains: '0123',
  attribution: '© OpenStreetMap contributors, © MapTiler',
  key: 'abcdefghi01234567890' // Get yours at https://maptiler.com/cloud/
});

openMapTilesLayer.addTo(map);
