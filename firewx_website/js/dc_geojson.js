
//////////////////////////////////////////////
////////////// DROUGHT CODE //////////////////
//////////////////////////////////////////////

function geo_json_dc_styler(feature) {
        switch(feature.properties.fill) {
            case "#0000e7": 
                return {"color": "#0000e7", "fillColor": "#0000e7", "opacity": 0.95, "weight": 0.2};
            case "#002cca": 
                return {"color": "#002cca", "fillColor": "#002cca", "opacity": 0.95, "weight": 0.2};
            case "#0058ad": 
                return {"color": "#0058ad", "fillColor": "#0058ad", "opacity": 0.95, "weight": 0.2};
            case "#008490": 
                return {"color": "#008490", "fillColor": "#008490", "opacity": 0.95, "weight": 0.2};
            case "#14a475": 
                return {"color": "#14a475", "fillColor": "#14a475", "opacity": 0.95, "weight": 0.2};
            case "#3bb75c": 
                return {"color": "#3bb75c", "fillColor": "#3bb75c", "opacity": 0.95, "weight": 0.2};
            case "#63cb43": 
                return {"color": "#63cb43", "fillColor": "#63cb43", "opacity": 0.95, "weight": 0.2};
            case "#8adf2a": 
                return {"color": "#8adf2a", "fillColor": "#8adf2a", "opacity": 0.95, "weight": 0.2};
            case "#a5d31e": 
                return {"color": "#a5d31e", "fillColor": "#a5d31e", "opacity": 0.95, "weight": 0.2};
            case "#c1c812": 
                return {"color": "#c1c812", "fillColor": "#c1c812", "opacity": 0.95, "weight": 0.2};
            case "#dcbc06": 
                return {"color": "#dcbc06", "fillColor": "#dcbc06", "opacity": 0.95, "weight": 0.2};
            case "#ea9c00": 
                return {"color": "#ea9c00", "fillColor": "#ea9c00", "opacity": 0.95, "weight": 0.2};
            case "#ed6800": 
                return {"color": "#ed6800", "fillColor": "#ed6800", "opacity": 0.95, "weight": 0.2};
            case "#ef3401": 
                return {"color": "#ef3401", "fillColor": "#ef3401", "opacity": 0.95, "weight": 0.2};
            default:
                return {"color": "#f10001", "fillColor": "#f10001", "opacity": 0.95, "weight": 0.2};
        }
    }
function geo_json_dc_onEachFeature(feature, layer) {};


var geo_json_dc = L.geoJson(null, {
        onEachFeature: geo_json_dc_onEachFeature,
    
        style: geo_json_dc_styler,
}).addTo(map_fwi);




function geo_json_dc_add (data) {
    geo_json_dc.addData(data);
};

/////////// ADDD dc DAAAATTTTAAAAAAA !!!!!!!!!!!!!!!!
