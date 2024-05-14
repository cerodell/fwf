// Initialize the map
var map = L.map('map').setView([51.0, -106.0], 4);


var CartoDB_Positron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
	subdomains: 'abcd',
	maxZoom: 20
}).addTo(map);

var currentlyDisplayedFireId = null;
var fireKmlLayer = null; // This will store the currently displayed KML layer



function showFirePerimeter() {
    var kmlUrl = `data/fires/fire_outlines-${currentlyDisplayedFireId}.kml`;
    if (fireKmlLayer) {
        // If the layer is already displayed, remove it
        map.removeLayer(fireKmlLayer);
        fireKmlLayer = null; // Reset the reference
    } else if (currentlyDisplayedFireId) {
        // Load and display the KML layer if not already displayed
        fireKmlLayer = omnivore.kml(kmlUrl)
            .on('ready', function() {
                map.fitBounds(fireKmlLayer.getBounds());
            })
            .on('error', function() {
                console.error('Error loading the KML file:', kmlUrl);
            })
            .addTo(map);
    } else {
        console.error("No fire selected for displaying perimeter.");
    }
}


var activeCircle = null; // This will store the currently active circle

// Fetch data and plot fires
fetch('data/ml-fires-info.json')
.then(response => response.json())
.then(data => {
    Object.values(data).forEach(fire => {
        let circle = L.circle([fire.lats, fire.lons], {
            radius: Math.sqrt(fire.area_ha / Math.PI) * 100,
            weight: 0.8,
            color: "black",
            fillColor: '#ffff73',
            fillOpacity: .5
        }).on('click', function () {
            if (activeCircle) {
                // Reset the previous active circle's color
                activeCircle.setStyle({
                    fillColor: '#ffff73',
                    color: 'black'
                });
            }
            // Set the new active circle
            activeCircle = circle;
            // Change the color of the new active circle
            circle.setStyle({
                fillColor: '#ff0000',  // Red for active
                color: 'red'  // Optional, changes the border color
            });
            displayTimeSeries(fire.fireID, fire);
        }).addTo(map);
    });
})
.catch(error => {
    console.error('Error loading fire data:', error);
});


function displayTimeSeries(fireId, fire) {
    document.getElementById('timeseries').style.display = 'block';
    currentlyDisplayedFireId = fireId;  // Update the variable with the current fire ID
    // Display static fire information
    var fireInfoDiv = document.getElementById('fireInfo');
    fireInfoDiv.innerHTML = `<h3>Fire Information</h3>
                             <strong>ID:</strong> ${fire.fireID}
                             <strong>Area (ha):</strong> ${fire.area_ha}
                             <strong>Latitude:</strong> ${fire.lats}
                             <strong>Longitude:</strong> ${fire.lons}`;
    fetchTimeSeriesData(fireId, document.getElementById('variableSelector').value);
}



function fetchTimeSeriesData(fireId, variable) {
  fetch(`data/fires/ml-fires-info-${fireId}.json`)
  .then(response => response.json())
  .then(data => {
      var trace1 = {
          x: data.local_datetime,
          y: data.FRP,
          name: 'FRP',
          type: 'scatter',
          yaxis: 'y1'
      };

      var trace2 = {
          x: data.local_datetime,
          y: data[variable],
          name: variable,
          type: 'scatter',
          yaxis: 'y2'
      };

      var layout = {
        //   title: `Fire Data Comparison`,
          xaxis: { title: 'Date' },
          yaxis: {
              title: 'FRP',
              titlefont: {color: '#1f77b4'},
              tickfont: {color: '#1f77b4'}
          },
          yaxis2: {
              title: variable,
              titlefont: {color: '#ff7f0e'},
              tickfont: {color: '#ff7f0e'},
              overlaying: 'y',
              side: 'right'
          }
      };

      Plotly.newPlot('plot', [trace1, trace2], layout);
  })
  .catch(error => {
      console.error('Error loading timeseries data:', error);
  });
}


function changeVariable() {
  if (currentlyDisplayedFireId) {
      fetchTimeSeriesData(currentlyDisplayedFireId, document.getElementById('variableSelector').value);
  } else {
      console.error("No fire selected for displaying data.");
  }
}

function closeTimeSeries() {
    document.getElementById('timeseries').style.display = 'none';
    if (fireKmlLayer) {
        map.removeLayer(fireKmlLayer);
        fireKmlLayer = null;
    }
}



// var firesLayer = omnivore.kml('data/fire_outlines.kml')
//     .on('ready', function() {
//         this.setStyle({color: "#ff8000"});
//     })
//     .on('click', function(e) {
//                     if (activeCircle) {
//                 // Reset the previous active circle's color
//                 activeCircle.setStyle({
//                     fillColor: '#ffff73',
//                     color: 'black'
//                 });
//             }
//             // Set the new active circle
//             activeCircle = circle;
//             // Change the color of the new active circle
//             circle.setStyle({
//                 fillColor: '#ff0000',  // Red for active
//                 color: 'red'  // Optional, changes the border color
//             });
//         // Accessing the clicked layer
//         var fireID = e.layer.feature.properties.name;
//         console.log(e);
//         console.log(fireID);


//         // Assuming the ID is stored as a property of the feature
//         // var fireID = clickedLayer.feature.properties.ID;

//         // Logging the ID to the console
//         // console.log(fireID);

//         // Optionally, call a function to display more data
//         displayTimeSeries(fireID);
//     })
//     .addTo(map);
// Add this function somewhere in your script
