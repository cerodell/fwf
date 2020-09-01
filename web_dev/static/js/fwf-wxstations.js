function createPopupContent(feature) {

	// Initalise the container to hold the popup content
	var html = '<div class="table-title">';

	// Name the popup
    html += '<h3>WMO Station ' +feature.wmo+ '</h3></div>';

	// Name WMO Station
    html += '<table class="table-fill">';
	
	html += '<thead> <tr> <th class="text-left">Variable</th> <th class="text-left">Bias</th> <th class="text-left">Prearsons</th> <th class="text-left">' +feature.DateTime+'</th></tr> </thead>';
    
    html += '<tbody class="table-hover"><tr>'
    html += '<td class="text-left">FFMC</td><td class="text-left">' +feature.FFMC_b +'<td class="text-left">' +feature.FFMC_c +'</td> <td class="text-left">' +feature.FFMC+'</td></tr>';
    html += '<td class="text-left">DMC</td><td class="text-left">' +feature.DMC_b +'<td class="text-left">' +feature.DMC_c +'</td> <td class="text-left">' +feature.DMC+'</td></tr>';
    html += '<td class="text-left">DC</td><td class="text-left">' +feature.DC_b +'<td class="text-left">' +feature.DC_c +'</td> <td class="text-left">' +feature.DC+'</td></tr>';
    html += '<td class="text-left">ISI</td><td class="text-left">' +feature.ISI_b +'<td class="text-left">' +feature.ISI_c +'</td> <td class="text-left">' +feature.ISI+'</td></tr>';
    html += '<td class="text-left">BUI</td><td class="text-left">' +feature.BUI_b +'<td class="text-left">' +feature.BUI_c +'</td><td class="text-left">' +feature.BUI+'</td> </tr>';
    html += '<td class="text-left">FWI</td><td class="text-left">' +feature.FWI_b +'<td class="text-left">' +feature.FWI_c +'</td><td class="text-left">' +feature.FWI+'</td> </tr>';

    html += '<td class="text-left">WSP</td><td class="text-left">' +feature.WSP_b +'<td class="text-left">' +feature.WSP_c +'</td> <td class="text-left">' +feature.WS+'</td></tr>';
    html += '<td class="text-left">TEMP</td><td class="text-left">' +feature.TEMP_b +'<td class="text-left">' +feature.TEMP_c +'</td><td class="text-left">' +feature.TEMP+'</td> </tr>';
    html += '<td class="text-left">RH</td><td class="text-left">' +feature.RH_b +'<td class="text-left">' +feature.RH_c +'</td> <td class="text-left">' +feature.RH+'</td></tr>';
    html += '<td class="text-left">QPF</td><td class="text-left">' +feature.QPF_b +'<td class="text-left">' +feature.QPF_c +'</td> <td class="text-left">' +feature.PRECIP+'</td></tr>';

    
	return html;
}

var wx_station = L.layerGroup();

const customOptions =
{
'maxWidth': '500',
'className' : 'custom-popup'
}
console.log(wxstations);
fetch(wxstations).then(function(response){
    return response.json();
}).then(function(json){
    // console.log(json)

    
    for (var key of Object.keys(json)) {
        var wxs = json[key]
        var lat = json[key].lat;
        var lng = json[key].lng;
        // console.log(lat);
        // console.log(lng);

        var prearsons = json[key].prearsons;
        // 0.00-0.19: very weak
        // 0.20-0.39: weak
        // 0.40-0.59: moderate 
        // 0.60-0.79: strong
        // 0.80-1.00: very strong.
        // var colors = ['#ff0000', '#ff4040', '#ff8080', '#ffbfbf', '#ffffff', '#bfbfff', '#8080ff', '#4040ff', '#0000ff'];
        // var colors = ['#ff0000', '#ff6232', '#ffb462', '#bfec8e', '#80ffb4', '#40ecd4', '#00b4ec', '#4062fa', '#8000ff']
        // var colors = ['#54ff00', '#ff6b00', '#7e00ef', '#0cbe37', '#ffc500', '#df0089', '#0063b6', '#fbff00', '#ff0000']
        // var colors = ['#c51b7d', '#de77ae', '#f1b6da', '#fde0ef', '#f7f7f7', '#e6f5d0', '#b8e186', '#7fbc41', '#4d9221'];
        var colors = ['#8e0152', '#c82582', '#e285b8', '#f5c4e1', '#faeaf3', '#eef6e1', '#c7e89f', '#8cc450', '#539725', '#276419']
        // var colors = ['#0d0887', '#4c02a1', '#7e03a8', '#aa2395', '#cc4778', '#e66c5c', '#f89540', '#fdc527', '#f0f921']
        // var colors =  ['#ffff66', '#dfef66', '#bfdf66', '#9fcf66', '#80bf66', '#60af66', '#409f66', '#208f66', '#008066']
        // var colors =  ['#ffff00', '#ffdf20', '#ffbf40', '#ff9f60', '#ff8080', '#ff609f', '#ff40bf', '#ff20df', '#ff00ff']
        if (prearsons >= 0.8) {
                color = colors[9];
          } else if (prearsons < 0.8 && prearsons >= 0.6) {
                color = colors[8];
        } else if (prearsons < 0.6 && prearsons >= 0.4) {
                color = colors[7];
        } else if (prearsons < 0.4 && prearsons >= 0.2) {
                color = colors[6];
        } else if (prearsons < 0.2 && prearsons >= 0) {
                color = colors[5];
        } else if (prearsons < 0 && prearsons >= -0.2) {
                color = colors[4];
        } else if (prearsons < -0.2 && prearsons >= -0.4) {
                color = colors[3];
        } else if (prearsons < -0.4 && prearsons >= -0.6) {
                color = colors[2];
        }else if (prearsons < -0.6 && prearsons >= -0.8) {
                color = colors[1];
        }
           else {
            color = colors[0];
          }


        
        wx_station.addLayer(L.circle([lat, lng], {
            radius: 4000,
            color: color,
            fillColor: color,
            fillOpacity: 0.92
        }).bindPopup(createPopupContent(wxs)));
    }

    
});


