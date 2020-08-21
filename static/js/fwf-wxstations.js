function createPopupContent(feature) {

	// Initalise the container to hold the popup content
	var html = '<div class="popup_content">';

	// Name the popup
    html += '<h2 class="popup_title">' + "Pearson's r value at </h2>"

	// Name WMO Station
    html += '<p class="wmo"> WMO Station ' +feature.wmo+ '</p>';
	
	html += '<div class="fwi_stats"><ul>';
    
    // FFMC
    html += '<li><span>FFMC: </span>' + feature.FFMC+ '</li>';
	// DMC
    html += '<li><span>DMC: </span>' + feature.DMC+ '</li>';
    // DC
    html += '<li><span>DC: </span>' + feature.DC+ '</li>';
	// ISI
    html += '<li><span>ISI: </span>' + feature.ISI+ '</li>';   
    // BUI
    html += '<li><span>BUI: </span>' + feature.BUI+ '</li>';
	// FWI
    html += '<li><span>FWI: </span>' + feature.FWI+ '</li>';

	html += '</ul></div>'; // End .fwi_stats

	html += '</div>'; // End .popup__content
	return html;
}











var wx_station = L.layerGroup()

const customOptions =
{
'maxWidth': '500',
'className' : 'custom-popup'
}

var wxstation = 'fwf-wxstation-2020081000.json'
fetch(wxstation).then(function(response){
    return response.json();
}).then(function(json){
    // console.log(json)

    
    for (var key of Object.keys(json)) {
        var wxs = json[key]
        var lat = json[key].lat;
        var lng = json[key].lng;

        // var FFMC = json[key].FFMC;
        // var DMC = json[key].DMC;
        // var DC = json[key].DC;
        // var ISI = json[key].ISI;
        // var BUI = json[key].BUI;
        // var FWI = json[key].FWI;
        // var WMO = json[key].wmo;

        // var popup = "<h1 style='font-size:20px;'><strong>Pearson's r value at</strong></h1> \
        //             WMO Station:  " + WMO + ' \
        //             <br>  FFMC:     ' + FFMC + '<br>  DMC: ' + DMC + '<br>  DC: ' + DC + 
        //             '<br>  ISI: ' + ISI + '<br>  BUI: ' + BUI + '<br>  FWI: ' + FWI 


        wx_station.addLayer(L.circle([lat, lng], 500, {
            color: 'black',
            fillColor: '#f03',
            fillOpacity: 0.3
        }).bindPopup(createPopupContent(wxs)));
    }

    
});


    // L.geoJSON(data, {
    //     style: function (feature) {
    //         return {color: feature.properties.color};
    //     }
    // }).bindPopup(function (layer) {
    //     return layer.feature.properties.description;
    // }).addTo(map)}