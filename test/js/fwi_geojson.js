var geo_json_fwi = L.layerGroup().addTo(map);

fetch('json/FWI_2020061800.geojson').then(function(response){
    return response.json();
}).then(function(json){

    geo_json_fwi.addLayer(L.vectorGrid.slicer( json, {
        rendererFactory: L.canvas.tile,
        vectorTileLayerStyles:{
            'FWI': geo_json_styler
                }
            }
        ).setZIndex(1000)
    )
});





