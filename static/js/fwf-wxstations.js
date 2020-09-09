function createPopupContent(feature) {

	// Initalise the container to hold the popup content
	var html = '<div class="table-title"  > <a href="https://cerodell.github.io/fwf-docs/index.html" target="_blank"><img class="icon" src="static/images/info.png" width="24" height="24"></a>   ';

	// Name the popup
    html += '<h3> WMO Station ' +feature.wmo+ ' </h3></div>';

	// Name WMO Station
    html += '<table class="table-fill">';
	
	html += '<thead> <tr> <th class="text-left">Variable  </th> <th class="text-left">Bias  </th> <th class="text-left">Prearsons  </th> <th class="text-left">' +feature.DateTime+'      </th></tr> </thead>';
    
    html += '<tbody class="table-hover"><tr>'
    html += '<td class="text-left">FFMC</td><td class="text-left">' +feature.FFMC_b +'<td class="text-left">' +feature.FFMC_c +'</td> <td class="text-left">' +feature.FFMC+'</td></tr>';
    html += '<td class="text-left">DMC</td><td class="text-left">' +feature.DMC_b +'<td class="text-left">' +feature.DMC_c +'</td> <td class="text-left">' +feature.DMC+'</td></tr>';
    html += '<td class="text-left">DC</td><td class="text-left">' +feature.DC_b +'<td class="text-left">' +feature.DC_c +'</td> <td class="text-left">' +feature.DC+'</td></tr>';
    html += '<td class="text-left">ISI</td><td class="text-left">' +feature.ISI_b +'<td class="text-left">' +feature.ISI_c +'</td> <td class="text-left">' +feature.ISI+'</td></tr>';
    html += '<td class="text-left">BUI</td><td class="text-left">' +feature.BUI_b +'<td class="text-left">' +feature.BUI_c +'</td><td class="text-left">' +feature.BUI+'</td> </tr>';
    html += '<td class="text-left">FWI</td><td class="text-left">' +feature.FWI_b +'<td class="text-left">' +feature.FWI_c +'</td><td class="text-left">' +feature.FWI+'</td> </tr>';

    html += '<td class="text-left">WSP<br>(km/hr)</td><td class="text-left">' +feature.WSP_b +'<td class="text-left">' +feature.WSP_c +'</td> <td class="text-left">' +feature.WS+' (km/hr)</td></tr>';
    html += '<td class="text-left">TEMP<br>(C)</td><td class="text-left">' +feature.TEMP_b +'<td class="text-left">' +feature.TEMP_c +'</td><td class="text-left">' +feature.TEMP+' (C)</td> </tr>';
    html += '<td class="text-left">RH<br>(%)</td><td class="text-left">' +feature.RH_b +'<td class="text-left">' +feature.RH_c +'</td> <td class="text-left">' +feature.RH+' (%)</td></tr>';
    html += '<td class="text-left">QPF<br>(mm)</td><td class="text-left">' +feature.QPF_b +'<td class="text-left">' +feature.QPF_c +'</td> <td class="text-left">' +feature.PRECIP+' (mm)</td></tr>';

    
	return html;
}

var wx_station = L.layerGroup();

const customOptions =
{
'maxWidth': '500',
'className' : 'custom-popup'
}
fetch(wxstations).then(function(response){
    return response.json();
}).then(function(json){    
    for (var key of Object.keys(json)) {
        var wxs = json[key]
        var lat = json[key].lat;
        var lng = json[key].lng;
        var prearsons = json[key].prearsons;
        // 0.00-0.19: very weak
        // 0.20-0.39: weak
        // 0.40-0.59: moderate 
        // 0.60-0.79: strong
        // 0.80-1.00: very strong.
        var colors = ['#8e0152', '#c82582', '#e285b8', '#f5c4e1', '#faeaf3', '#eef6e1', '#c7e89f', '#8cc450', '#539725', '#276419']

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


