function createPopupContent(feature) {



	// Initalise the container to hold the popup content
	// var html = '<div class="table-title" id="plot_table"  > <a href="https://cerodell.github.io/fwf-docs/index.html" target="_blank"><img class="icon" src="static/images/info.png" width="24" height="24"></a>   ';
    var html = '<iframe frameborder="0" seamless="seamless" width=600px height=400px \
    scrolling="no" src="//plot.ly/~mrmillky/1.embed?autosize=true&link=false"></iframe></div>'

    // Name the popup
    // html += '<tbody class="table-hover"><tr>'
    // C = document.getElementById('tester'),
    // var iframe = document.getElementById("command"); // Note the captialization!
    // console.log(test);
    // Plotly.newPlot(iframe, feature.ffmc_fc);

    // html += '<h3> WMO Station ' +feature.wmo+ ' </h3></div>';

	// // Name WMO Station
    // html += '<table class="table-fill">';
	
	// html += '<thead> <tr> <th class="text-left">Variable  </th> <th class="text-left">Bias  </th> <th class="text-left">Prearsons  </th> <th class="text-left">' +feature.DateTime+'      </th></tr> </thead>';
    
    // html += '<tbody class="table-hover"><tr>'
    // html += '<td class="text-left">FFMC</td><td class="text-left">' +feature.FFMC_b +'<td class="text-left">' +feature.FFMC_c +'</td> <td class="text-left">' +feature.FFMC+'</td></tr>';
    // html += '<td class="text-left">DMC</td><td class="text-left">' +feature.DMC_b +'<td class="text-left">' +feature.DMC_c +'</td> <td class="text-left">' +feature.DMC+'</td></tr>';
    // html += '<td class="text-left">DC</td><td class="text-left">' +feature.DC_b +'<td class="text-left">' +feature.DC_c +'</td> <td class="text-left">' +feature.DC+'</td></tr>';
    // html += '<td class="text-left">ISI</td><td class="text-left">' +feature.ISI_b +'<td class="text-left">' +feature.ISI_c +'</td> <td class="text-left">' +feature.ISI+'</td></tr>';
    // html += '<td class="text-left">BUI</td><td class="text-left">' +feature.BUI_b +'<td class="text-left">' +feature.BUI_c +'</td><td class="text-left">' +feature.BUI+'</td> </tr>';
    // html += '<td class="text-left">FWI</td><td class="text-left">' +feature.FWI_b +'<td class="text-left">' +feature.FWI_c +'</td><td class="text-left">' +feature.FWI+'</td> </tr>';

    // html += '<td class="text-left">WSP<br>(km/hr)</td><td class="text-left">' +feature.WSP_b +'<td class="text-left">' +feature.WSP_c +'</td> <td class="text-left">' +feature.WS+' (km/hr)</td></tr>';
    // html += '<td class="text-left">TEMP<br>(C)</td><td class="text-left">' +feature.TEMP_b +'<td class="text-left">' +feature.TEMP_c +'</td><td class="text-left">' +feature.TEMP+' (C)</td> </tr>';
    // html += '<td class="text-left">RH<br>(%)</td><td class="text-left">' +feature.RH_b +'<td class="text-left">' +feature.RH_c +'</td> <td class="text-left">' +feature.RH+' (%)</td></tr>';
    // html += '<td class="text-left">QPF<br>(mm)</td><td class="text-left">' +feature.QPF_b +'<td class="text-left">' +feature.QPF_c +'</td> <td class="text-left">' +feature.PRECIP+' (mm)</td></tr>';

    
    return html;


    // C = document.getElementById("plot_table");
    // Plotly.newPlot(C, feature.ffmc_fc);

}


var wx_station = L.layerGroup();



// ['time', 'time_obs', 'elev', 'id', 'lats', 'lons', 'name',
// 'prov', 'tz_correct', 'wmo', 'time_fch', 'time_fcd', 'dsr_fc',
// 'dsr_obs', 'dsr_pfc', 'ffmc_fc', 'ffmc_obs', 'ffmc_pfc', 
// 'rh_fc', 'rh_obs', 'rh_pfc', 'isi_fc', 'isi_obs', 'isi_pfc', 
// 'fwi_fc', 'fwi_obs', 'fwi_pfc', 'temp_fc', 'temp_obs', 'temp_pfc', 
// 'ws_fc', 'ws_obs', 'ws_pfc', 'wdir_fc', 'wdir_obs', 'wdir_pfc', 
// 'precip_fc', 'precip_obs', 'precip_pfc', 'dc_fc', 'dc_obs', 'dc_pfc',
// 'dmc_fc', 'dmc_obs', 'dmc_pfc', 'bui_fc', 'bui_obs', 'bui_pfc']

const customOptions =
{
'maxWidth': '500',
'className' : 'custom-popup'
}


// Promise.all([
//     fetch(wxstations).then(value => value.json()),
//     fetch(json_fwf).then(value => value.json())
//     ])
//     .then((value) => {
//         var wx = value[0]
//        console.log(JSON.parse(wx.lats))
//       //json response
//     })
//     .catch((err) => {
//         console.log(err);
//     });


wx_station.onAdd = function(){
fetch(wxstations).then(function(response){
    return response.json();
}).then(function(json){   
        var id = json.id;
        var wmo = JSON.parse(json.wmo);
        var lats = JSON.parse(json.lats);
        var lons = JSON.parse(json.lons);
        var elev = JSON.parse(json.elev);
        var name = json.name;
        var prov = json.prov;
        var tz_correct = JSON.parse(json.tz_correct);


        var dsr_fc = JSON.parse(json.dsr_fc);
        var dsr_pfc = JSON.parse(json.dsr_pfc);
        var dsr_obs = JSON.parse(json.dsr_obs);

        var ffmc_fc = JSON.parse(json.ffmc_fc);
        var ffmc_pfc = JSON.parse(json.ffmc_pfc);
        var ffmc_obs = JSON.parse(json.ffmc_obs);

        var rh_fc = JSON.parse(json.rh_fc);
        var rh_pfc = JSON.parse(json.rh_pfc);
        var rh_obs = JSON.parse(json.rh_obs);

        var isi_fc = JSON.parse(json.isi_fc);
        var isi_pfc = JSON.parse(json.isi_pfc);
        var isi_obs = JSON.parse(json.isi_obs);

        var fwi_fc = JSON.parse(json.fwi_fc);
        var fwi_pfc = JSON.parse(json.fwi_pfc);
        var fwi_obs = JSON.parse(json.fwi_obs);

        var temp_fc = JSON.parse(json.temp_fc);
        var temp_pfc = JSON.parse(json.temp_pfc);
        var temp_obs = JSON.parse(json.temp_obs);

        var ws_fc = JSON.parse(json.ws_fc);
        var ws_pfc = JSON.parse(json.ws_pfc);
        var ws_obs = JSON.parse(json.ws_obs);


        var wdir_fc = JSON.parse(json.wdir_fc);
        var wdir_pfc = JSON.parse(json.wdir_pfc);
        var wdir_obs = JSON.parse(json.wdir_obs);

        var precip_fc = JSON.parse(json.precip_fc);
        var precip_pfc = JSON.parse(json.precip_pfc);
        var precip_obs = JSON.parse(json.precip_obs);

        var dc_fc = JSON.parse(json.dc_fc);
        var dc_pfc = JSON.parse(json.dc_pfc);
        var dc_obs = JSON.parse(json.dc_obs);

        var dmc_fc = JSON.parse(json.dmc_fc);
        var dmc_pfc = JSON.parse(json.dmc_pfc);
        var dmc_obs = JSON.parse(json.dmc_obs);

        var bui_fc = JSON.parse(json.bui_fc);
        var bui_pfc = JSON.parse(json.bui_pfc);
        var bui_obs = JSON.parse(json.bui_obs);
        const arrayColumn = (arr, n) => arr.map(x => x[n]);

        for (index = 0; index < lats.length; ++index) {
            wmx = {'elev':elev[index], 'id':id[index], 'lats':lats[index], 'lons':lons[index], 'name':name[index],
            'prov':prov[index], 'tz_correct':tz_correct[index], 'wmo':wmo[index],'dsr_fc':arrayColumn(dsr_fc,index),
            'dsr_obs':arrayColumn(dsr_obs,index), 'dsr_pfc':arrayColumn(dsr_pfc,index), 'ffmc_fc':arrayColumn(ffmc_fc,index), 'ffmc_obs':arrayColumn(ffmc_obs,index), 'ffmc_pfc':arrayColumn(ffmc_pfc,index), 
            'rh_fc':arrayColumn(rh_fc,index), 'rh_obs':arrayColumn(rh_obs,index), 'rh_pfc':arrayColumn(rh_obs,index), 'isi_fc':arrayColumn(isi_fc,index), 'isi_obs':arrayColumn(isi_obs,index), 'isi_pfc':arrayColumn(isi_pfc,index), 
            'fwi_fc':arrayColumn(fwi_fc,index), 'fwi_obs':arrayColumn(fwi_obs,index), 'fwi_pfc':arrayColumn(fwi_pfc,index), 'temp_fc':arrayColumn(temp_fc,index), 'temp_obs':arrayColumn(temp_obs,index), 'temp_pfc':arrayColumn(temp_pfc,index), 
            'ws_fc':arrayColumn(ws_fc,index), 'ws_obs':arrayColumn(ws_obs,index), 'ws_pfc':arrayColumn(ws_pfc,index), 'wdir_fc':arrayColumn(wdir_fc,index), 'wdir_obs':arrayColumn(wdir_obs,index), 'wdir_pfc':arrayColumn(wdir_pfc,index), 
            'precip_fc':arrayColumn(precip_fc,index), 'precip_obs':arrayColumn(precip_obs,index), 'precip_pfc':arrayColumn(precip_pfc,index), 'dc_fc':arrayColumn(dc_fc,index), 'dc_obs':arrayColumn(dc_obs,index), 'dc_pfc':arrayColumn(dc_pfc,index),
            'dmc_fc':arrayColumn(dmc_fc,index), 'dmc_obs':arrayColumn(dmc_obs,index), 'dmc_pfc':arrayColumn(dmc_pfc,index), 'bui_fc':arrayColumn(bui_fc,index), 'bui_obs':arrayColumn(bui_obs,index), 'bui_pfc':arrayColumn(bui_pfc,index)
            }

        var colors = ['#ff6760', '#ffff73', '#63a75c']
        if (temp_obs[temp_obs.length - 1][index] != -99 && ffmc_obs[temp_obs.length - 1][index] != -99) {
            color = colors[2];
        } else if (temp_obs[temp_obs.length - 1][index] != -99 && ffmc_obs[temp_obs.length - 1][index] == -99) {
            color = colors[1];
        }else {
                color = colors[0];
              }

    
        wx_station.addLayer(L.circle([lats[index], lons[index]], {
            radius: 4000,
            color: color,
            fillColor: color,
            fillOpacity: 1
        }).bindPopup(createPopupContent(wmx)));
    }

    
});
};


