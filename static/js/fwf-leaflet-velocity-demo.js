



fetch('wind-gbr.json', {cache: "default"}).then(function(response){
    return response.json();
}).then(function(json){
	var velocityLayer = L.velocityLayer({
		displayValues: true,
		displayOptions: {
			velocityType: 'GBR Wind',
			displayPosition: 'bottomleft',
			displayEmptyString: 'No wind data'
		},
		data: json,
		maxVelocity: 10
	}).addTo(map);
    
});


