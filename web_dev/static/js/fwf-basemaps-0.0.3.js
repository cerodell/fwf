var gl=L.mapboxGL({attribution:'<a href="https://www.maptiler.com/copyright/" target="_blank">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>', style:"topo.json"}).addTo(map);L.control.scale({position:"bottomright"}).addTo(map),map.fullscreenControl.setPosition("topright");

console.log(gl);
