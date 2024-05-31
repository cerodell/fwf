///////////////////  MAP  ///////////////////
var map = L.map(
    "map",
    {
        center: [56.89589, -107.58885],
        // crs: L.CRS.EPSG3857,
        preferCanvas: true,
        zoom: 4,
        minZoom: 3,
        maxZoom: 18,
        maxBounds: [
        [-90, 360],
        [90,-360]
        ],
        zoomControl: true,
        preferCanvas: true,
        fullscreenControl: true,
    });

// L.control.scale({position:"bottomright"}).addTo(map),map.fullscreenControl.setPosition("topright");

var CartoDB_Positron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
	subdomains: 'abcd',
	maxZoom: 20
}).addTo(map);



var zoomHome=L.Control.zoomHome({position:"topright"});zoomHome.addTo(map);
var currentlyDisplayedFireId = null;
var fireKmlLayer = null; // This will store the currently displayed KML layer
//////////////////////////////////////////////



///////////////////  FIRES  ///////////////////

function showFirePerimeter() {
    var kmlUrl = `data/fires-v2/fire_outlines-${currentlyDisplayedFireId}.kml`;
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
fetch('data/ml-fires-info-v2.json')
.then(response => response.json())
.then(data => {
    Object.values(data).forEach(fire => {
        let fiilTYPE = fire.TYPE
        let fillColor = (fire.TYPE === 'test') ? '#679267' : '#ffff73';

        let circle = L.circle([fire.lats, fire.lons], {
            radius: Math.sqrt(fire.area_ha / Math.PI) * 100,
            weight: 0.8,
            color: "black",
            fillColor: fillColor,
            fillOpacity: .5
        }).on('click', function () {
            if (activeCircle) {
                // Reset the previous active circle's color based on its TYPE
                let previousFillColor = (activeCircle.fiilTYPE === 'test') ? '#679267' : '#ffff73';
                activeCircle.setStyle({
                    fillColor: previousFillColor,
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
        });

        // Attach the fire object to the circle for later use
        circle.fiilTYPE = fiilTYPE;
        circle.addTo(map);
    });
})
.catch(error => {
    console.error('Error loading fire data:', error);
});

//////////////////////////////////////////

var datasetMode = 'mean'; // Initial mode set to mean

function toggleDatasetMode() {
    datasetMode = (datasetMode === 'mean') ? 'sum' : 'mean';
    updateTitle(); // Update the title based on the new mode
    updatePlot(); // Refresh the plot with the new mode
}

function updateTitle() {
    var titleElement = document.getElementById('timeseries-title');
    titleElement.textContent = (datasetMode === 'mean') ? 'Mean Values' : 'Sum Values';
}

function updatePlot() {
    fetchTimeSeriesData(currentlyDisplayedFireId, currentlyDisplayedFireTYPE, document.getElementById('variableSelector').value, datasetMode);
}

function displayTimeSeries(fireId, fire) {
    document.getElementById('timeseries').style.display = 'block';
    currentlyDisplayedFireId = fireId;
    currentlyDisplayedFireTYPE = fire.TYPE;

    // Show/hide the toggleDataset button based on fire type
    var toggleDatasetButton = document.getElementById('toggleDataset');
    if (fire.TYPE === 'test') {
        toggleDatasetButton.style.display = 'inline';
    } else {
        toggleDatasetButton.style.display = 'none';
    }

    // Adjust the options in the variable selector based on the fire TYPE
    var variableSelector = document.getElementById('variableSelector');
    variableSelector.innerHTML = ''; // Clear existing options
    if (fire.TYPE === 'test') {
        variableSelector.innerHTML += '<option value="MODELED_FRP">Forecasted Fire Radiative Power</option>';
        variableSelector.innerHTML += '<option value="FWI">Fire Weather Index</option>';
        variableSelector.innerHTML += '<option value="HFI">Head Fire Intensity</option>';
        variableSelector.innerHTML += '<option value="FFMC">Fine Fuel Moisture Code</option>';
        variableSelector.innerHTML += '<option value="ISI">Initial Spread Index</option>';
        variableSelector.innerHTML += '<option value="BUI">Build up Index</option>';
        variableSelector.innerHTML += '<option value="WS">10m Wind Speed</option>';
        variableSelector.innerHTML += '<option value="WD">10m Wind Direction</option>';
        variableSelector.innerHTML += '<option value="TEMP">2m Temperature</option>';
        variableSelector.innerHTML += '<option value="RH">2m Relative Humidity</option>';
        variableSelector.innerHTML += '<option value="PRECIP">Precipitation mm</option>';
        variableSelector.innerHTML += '<option value="Live_Leaf">Live Leaf</option>';
        variableSelector.innerHTML += '<option value="Dead_Foliage">Dead Foliage</option>';
        variableSelector.innerHTML += '<option value="Live_Wood">Live Wood</option>';
        variableSelector.innerHTML += '<option value="Dead_Wood">Dead Wood</option>';
        variableSelector.innerHTML += '<option value="PM25">PM2.5</option>';
        variableSelector.innerHTML += '<option value="NDVI">Norm. Dif. Veg. Index</option>';
        variableSelector.innerHTML += '<option value="LAI">Leaf Area Index</option>';

        } else {
        variableSelector.innerHTML += '<option value="HFI">Head Fire Intensity</option>';
        variableSelector.innerHTML += '<option value="FWI">Fire Weather Index</option>';
        variableSelector.innerHTML += '<option value="FWI">Fire Weather Index</option>';
        variableSelector.innerHTML += '<option value="HFI">Head Fire Intensity</option>';
        variableSelector.innerHTML += '<option value="FFMC">Fine Fuel Moisture Code</option>';
        variableSelector.innerHTML += '<option value="ISI">Initial Spread Index</option>';
        variableSelector.innerHTML += '<option value="BUI">Build up Index</option>';
        variableSelector.innerHTML += '<option value="WS">10m Wind Speed</option>';
        variableSelector.innerHTML += '<option value="WD">10m Wind Direction</option>';
        variableSelector.innerHTML += '<option value="TEMP">2m Temperature</option>';
        variableSelector.innerHTML += '<option value="RH">2m Relative Humidity</option>';
        variableSelector.innerHTML += '<option value="PRECIP">Precipitation mm</option>';
        variableSelector.innerHTML += '<option value="Live_Leaf">Live Leaf</option>';
        variableSelector.innerHTML += '<option value="Dead_Foliage">Dead Foliage</option>';
        variableSelector.innerHTML += '<option value="Live_Wood">Live Wood</option>';
        variableSelector.innerHTML += '<option value="Dead_Wood">Dead Wood</option>';
        variableSelector.innerHTML += '<option value="PM25">PM2.5</option>';
        variableSelector.innerHTML += '<option value="NDVI">Norm. Dif. Veg. Index</option>';
        variableSelector.innerHTML += '<option value="LAI">Leaf Area Index</option>';    }

    // Display static fire information
    var fireInfoDiv = document.getElementById('fireInfo');
    fireInfoDiv.innerHTML = `<h3>Fire Information</h3>
                            <strong>ID:</strong> ${fire.fireID},
                            <strong>Area (ha):</strong> ${fire.area_ha},
                            <strong>Latitude:</strong> ${fire.lats},
                            <strong>Longitude:</strong> ${fire.lons},
                            <strong>Pearson Correlation:</strong> <span id="correlation"></span>`;

    // Set the initial title based on the current dataset mode
    updateTitle();
    fetchTimeSeriesData(fireId, fire.TYPE, document.getElementById('variableSelector').value, datasetMode);
}

function fetchTimeSeriesData(fireId, type, variable, mode) {
    fetch(`data/fires-v2/ml-${type}-${mode}-fires-info-${fireId}.json`)
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
            yaxis: (variable === 'MODELED_FRP') ? 'y1' : 'y2',
            line: {
                color: (variable === 'MODELED_FRP') ? '#DB3209' : '#ff7f0e'
            }
        };

        var layout = {
            xaxis: { title: 'Date' },
            yaxis: {
                title: 'FRP',
                titlefont: { color: '#1f77b4' },
                tickfont: { color: '#1f77b4' }
            },
            yaxis2: {
                title: variable,
                titlefont: { color: (variable === 'MODELED_FRP') ? '#DB3209' : '#ff7f0e' },
                tickfont: { color: (variable === 'MODELED_FRP') ? '#DB3209' : '#ff7f0e' },
                overlaying: 'y',
                side: 'right'
            }
        };

        Plotly.newPlot('plot', [trace1, trace2], layout);
        var frpValues = data.FRP;
        var variableValues = data[variable];

        var correlation = calculatePearsonCorrelation(frpValues, variableValues);
        document.getElementById('correlation').innerText = `${correlation.toFixed(2)}`;

        if (variable === 'MODELED_FRP') {
            var rmse = calculateRMSE(frpValues, variableValues);
            var mbe = calculateMBE(frpValues, variableValues);

            var fireInfoDiv = document.getElementById('fireInfo');
            // Clear existing RMSE and MBE values
            clearRmseMbe();

            // Append new RMSE and MBE values
            var rmseSpan = document.createElement('span');
            rmseSpan.id = 'rmse';
            rmseSpan.innerHTML = `, <strong>RMSE:</strong> ${rmse.toFixed(2)}`;
            fireInfoDiv.appendChild(rmseSpan);

            var mbeSpan = document.createElement('span');
            mbeSpan.id = 'mbe';
            mbeSpan.innerHTML = `, <strong>MBE:</strong> ${mbe.toFixed(2)}`;
            fireInfoDiv.appendChild(mbeSpan);
        } else {
            // Remove RMSE and MBE if the variable is not MODELED_FRP
            clearRmseMbe();
        }

    })
    .catch(error => {
        console.error('Error loading timeseries data:', error);
    });
}

function clearRmseMbe() {
    var rmseElement = document.getElementById('rmse');
    var mbeElement = document.getElementById('mbe');
    if (rmseElement) rmseElement.remove();
    if (mbeElement) mbeElement.remove();
}

function changeVariable() {
    if (currentlyDisplayedFireId) {
        fetchTimeSeriesData(currentlyDisplayedFireId, currentlyDisplayedFireTYPE, document.getElementById('variableSelector').value, datasetMode);
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




////////////////////////////////////////////////////////


///////////////////  Math Functions ///////////////////

function calculateRMSE(observed, modeled) {
    var sumOfSquares = 0;
    for (var i = 0; i < observed.length; i++) {
        var diff = observed[i] - modeled[i];
        sumOfSquares += diff * diff;
    }
    var meanSquare = sumOfSquares / observed.length;
    return Math.sqrt(meanSquare);
}

function calculateMBE(observed, modeled) {
    var sumOfErrors = 0;
    for (var i = 0; i < observed.length; i++) {
        var diff = observed[i] - modeled[i];
        sumOfErrors += diff;
    }
    return sumOfErrors / observed.length;
}

function calculatePearsonCorrelation(x, y) {
    var meanX = math.mean(x);
    var meanY = math.mean(y);

    var numerator = 0;
    var denominatorX = 0;
    var denominatorY = 0;

    for (var i = 0; i < x.length; i++) {
        var diffX = x[i] - meanX;
        var diffY = y[i] - meanY;
        numerator += diffX * diffY;
        denominatorX += diffX * diffX;
        denominatorY += diffY * diffY;
    }

    var denominator = Math.sqrt(denominatorX * denominatorY);
    if (denominator === 0) return 0;
    return numerator / denominator;
}
