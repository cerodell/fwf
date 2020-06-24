var geo_json_dmc = L.layerGroup().addTo(map);

fetch('json/DMC_2020061800.geojson').then(function(response){
    return response.json();
}).then(function(json){

    geo_json_dmc.addLayer(L.vectorGrid.slicer( json, {
        rendererFactory: L.canvas.tile,
        vectorTileLayerStyles:{
            'DMC': geo_json_styler
                }
            }
        ).setZIndex(1000)
    )
});





