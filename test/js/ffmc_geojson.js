
var ffmc_topo_file = 'json/ffmc/FFMC_2020061800.geojson';
// var ffmc_topo_file = 'json/ffmc/FFMC_2020061801.geojson';

// /////////////////////////////////////////////////////////
//////////// NEW METHOD FOR LOADING JSONS NEGATING layergroup
// /////////////////////////////////////////////////////////
var json = $.getJSON({'url': ffmc_topo_file, 'async': false});  
console.log(json);
json = JSON.parse(json.responseText); 
// console.log(json);





// var json = JSON.parse($.ajax({'url': ffmc_topo_file, 'async': false}).responseText);
// console.log(json);
// json.property = ffmc_topo_file
// console.log(json);


var geo_json_ffmc = L.vectorGrid.slicer( json, {
    rendererFactory: L.canvas.tile,
    vectorTileLayerStyles:{
          "FFMC" : geo_json_styler
            }
        }
    ).setZIndex(1000)

// var url = geo_json_ffmc.json
// console.log(geo_json_ffmc);

// /////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////


// /////////////////////////////////////////////////////////
// OLD METHOD FROM LOADING JSON USING FETCH AND LAYERGROUPS///
// /////////////////////////////////////////////////////////
// var geo_json_ffmc = L.layerGroup()

// function get_json(file_dir){
// fetch(file_dir).then(function(response){
//     return response.json();
// }).then(function(json){
//     console.log(json);
//     var ffmc = L.vectorGrid.slicer( json, {
//         rendererFactory: L.canvas.tile,
//         vectorTileLayerStyles:{
//               "FFMC" : geo_json_styler
//                 }
//             }
//         ).setZIndex(1000)
//     geo_json_ffmc.addLayer(ffmc)
// }
// )};
// get_json(ffmc_topo_file)
// geo_json_ffmc.addTo(map);
// /////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////