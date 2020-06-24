var geo_json_isi = L.layerGroup().addTo(map);

fetch('json/ISI_2020061800.geojson').then(function(response){
    return response.json();
}).then(function(json){

    geo_json_isi.addLayer(L.vectorGrid.slicer( json, {
        rendererFactory: L.canvas.tile,
        vectorTileLayerStyles:{
            'ISI': geo_json_styler
                }
            }
        ).setZIndex(1000)
    )
});





