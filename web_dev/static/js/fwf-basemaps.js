
var gl = L.mapboxGL({
	// accessToken: 'pk.eyJ1IjoiY3JvZGVsbCIsImEiOiJja2R2NzlndzcwbGt3MnJuc3c2Zmw0a25mIn0.78DDSgHz8FV42ucl_h5RFw',
	attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>',
	style: 'topo-notab.json',
}).addTo(map)

L.control.scale({position: 'bottomright'}).addTo(map);
map.fullscreenControl.setPosition('topright');



// // // Opacity control
// var multiLayers = [ffmcTimeLayer],
// layerGroup = L.layerGroup(multiLayers),
// opacitySliderGroup = new L.Control.opacitySliderGroup().addTo(map);
// opacitySliderGroup.setOpacityLayerGroup(layerGroup);


