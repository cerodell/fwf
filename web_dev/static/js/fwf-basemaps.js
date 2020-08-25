
var gl = L.mapboxGL({
	attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>',
	style: 'topo-notab.json',
}).addTo(map)




L.control.scale({position: 'bottomright'}).addTo(map);
// Move zoom and full screen controls to top-right
// map.zoomControl.setPosition('topright');
map.fullscreenControl.setPosition('topright');
// 
// Replace default zoom controls with controls that re-center & reset zoom level
// map.zoomControl.remove();
// var zoomHome = L.Control.zoomHome({position: 'topright'});
// zoomHome.addTo(map);


// // // Opacity control
// var multiLayers = [ffmcTimeLayer],
// layerGroup = L.layerGroup(multiLayers),
// opacitySliderGroup = new L.Control.opacitySliderGroup().addTo(map);
// opacitySliderGroup.setOpacityLayerGroup(layerGroup);


