var geo_json_dc = L.layerGroup().addTo(map);

fetch('json/DC_2020061800.geojson').then(function(response){
    return response.json();
}).then(function(json){

    geo_json_dc.addLayer(L.vectorGrid.slicer( json, {
        rendererFactory: L.canvas.tile,
        vectorTileLayerStyles:{
            'DC': geo_json_styler
                }
            }
        ).setZIndex(1000)
    )
});





