




// var Topo_GL = L.mapboxGL({
// 	attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>',
// 	style: 'https://api.maptiler.com/maps/topo/style.json?key=PquYEjaZQgGOArfxeoCO'
//   }).addTo(map);

  var openmaptilesUrl = "https://api.maptiler.com/tiles/v3/{z}/{x}/{y}.pbf?key={key}";

  var Topo_GL = L.vectorGrid.protobuf(openMapTilesUrl, {
	vectorTileLayerStyles: vectorStyles,
	subdomains: '0123',
	attribution: '© OpenStreetMap contributors, © MapTiler',
	key: 'AcwSJSEdQL53EDd0mvwp' // Get yours at https://maptiler.com/cloud/
  });

// var CartoDB_PositronNoLabels = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
// 	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
// 	subdomains: 'abcd',
// 	maxZoom: 19
// }).addTo(map);


// var Stamen_TonerBackground = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-background/{z}/{x}/{y}{r}.{ext}', {
// 	attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
// 	subdomains: 'abcd',
// 	minZoom: 0,
// 	maxZoom: 20,
// 	ext: 'png'
// });


// // var Stamen_TerrainBackground = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain-background/{z}/{x}/{y}{r}.{ext}', {
// // 	attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
// // 	subdomains: 'abcd',
// // 	minZoom: 0,
// // 	maxZoom: 18,
// // 	ext: 'png'
// // });

// var Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
// 	attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
// });

// var Esri_WorldTerrain = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}', {
// 	attribution: 'Tiles &copy; Esri &mdash; Source: USGS, Esri, TANA, DeLorme, and NPS',
// 	maxZoom: 13
// });

// var Stamen_Labels = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-labels/{z}/{x}/{y}{r}.{ext}', {
// 	// attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
// 	subdomains: 'abcd',
// 	minZoom: 0,
// 	maxZoom: 18,
// 	ext: 'png'
// }).setZIndex(1000).addTo(map);;


// var Stamen_TonerLines = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lines/{z}/{x}/{y}{r}.{ext}', {
// 	// attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
// 	subdomains: 'abcd',
// 	minZoom: 0,
// 	maxZoom: 20,
// 	ext: 'png'
// }).setZIndex(600).addTo(map);



