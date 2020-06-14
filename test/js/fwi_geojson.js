var geo_json_fwi = L.layerGroup().addTo(map_fwi);

fetch('json/FWI_20200607.geojson').then(function(response){
    return response.json();
}).then(function(json){

    geo_json_fwi.addLayer(L.vectorGrid.slicer( json, {
        rendererFactory: L.canvas.tile,
        vectorTileLayerStyles:{
            'FWI': function(properties, zoom) {
                switch(properties.fill) {
                    case "#0000e7": 
                        return {"color": "#0000e7", "fillColor": "#0000e7", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#002cca": 
                        return {"color": "#002cca", "fillColor": "#002cca", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#0058ad": 
                        return {"color": "#0058ad", "fillColor": "#0058ad", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#008490": 
                        return {"color": "#008490", "fillColor": "#008490", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#14a475": 
                        return {"color": "#14a475", "fillColor": "#14a475", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#3bb75c": 
                        return {"color": "#3bb75c", "fillColor": "#3bb75c", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#63cb43": 
                        return {"color": "#63cb43", "fillColor": "#63cb43", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#8adf2a": 
                        return {"color": "#8adf2a", "fillColor": "#8adf2a", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#a5d31e": 
                        return {"color": "#a5d31e", "fillColor": "#a5d31e", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#c1c812": 
                        return {"color": "#c1c812", "fillColor": "#c1c812", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#dcbc06": 
                        return {"color": "#dcbc06", "fillColor": "#dcbc06", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#ea9c00": 
                        return {"color": "#ea9c00", "fillColor": "#ea9c00", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#ed6800": 
                        return {"color": "#ed6800", "fillColor": "#ed6800", "opacity": 0.98, "weight": 0.2, fill: true};
                    case "#ef3401": 
                        return {"color": "#ef3401", "fillColor": "#ef3401", "opacity": 0.98, "weight": 0.2, fill: true};
                    default:
                        return {"color": "#f10001", "fillColor": "#f10001", "opacity": 0.98, "weight": 0.2, fill: true};
                        }
                    }
                }
            }
        )
    )
});





