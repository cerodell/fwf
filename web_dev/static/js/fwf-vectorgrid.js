

function loadgeojson(geojson_dir, geojson_layer, geojson_layergeojson_layer){
    fetch(geojson_dir).then(function(response){
    return response.json();
}).then(function(json){
    var code = geojson_layer
    geojson_layer.addLayer(L.vectorGrid.slicer( json, {
        rendererFactory: L.canvas.tile,
        vectorTileLayerStyles:{
            code: geo_json_styler
                }
            }
        ).setZIndex(500)
    )
})

};
