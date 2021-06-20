// Fires layer
var firesLayer = omnivore.kml('data/fire_outlines.kml')
    .on('ready', function() {
        this.setStyle({color: "#ff8000"})
    });


// Hotspots layer with marker clustering
var hotspots = omnivore.kml('data/fire_locations.kml'),
    hotspotsMarkers = L.markerClusterGroup({
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        spiderfyOnMaxZoom: true,
        removeOutsideVisibleBounds: true,
        spiderLegPolylineOptions: {weight: 1.5, color: '#ff1100', opacity: 0.5},
        maxClusterRadius: 60,
        disableClusteringAtZoom: 11,
    });

// // Hotspot icon
// var hotspotIcon = L.icon({
//     iconUrl:   '/static/img/fire-marker-5.png',
//     shadowUrl: '',
//     iconSize:     [32, 37],
//     shadowSize:   [],
//     iconAnchor:   [16, 36],
//     shadowAnchor: [],
//     popupAnchor:  [-3, -76],
// });

// // Hotspots layer with marker clustering
// var hotspots = omnivore.kml('data/fire_locations.kml'),
//     hotspotsMarkers = L.markerClusterGroup({
//         showCoverageOnHover: false,
//         zoomToBoundsOnClick: true,
//         spiderfyOnMaxZoom: true,
//         removeOutsideVisibleBounds: true,
//         spiderLegPolylineOptions: {weight: 1.5, color: '#ff1100', opacity: 0.5},
//         maxClusterRadius: 60,
//         disableClusteringAtZoom: 11,
//     });
// hotspots.on('ready', function () {
//     hotspots.eachLayer(function(layer) {
//         if (layer instanceof L.Marker) {
//             layer.setIcon(hotspotIcon);
//             layer.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
//             layer.on('click', test);
//         }
//     });

//     hotspotsMarkers.addLayer(hotspots);
// });
// hotspots.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
// hotspots.on('click', test);
