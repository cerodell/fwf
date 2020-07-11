
const fwflocation = L.marker();

function makeplots(json_dir) {
fetch(json_dir).then(function(response){
    return response.json();
  }).then(function(json){ 
  // console.log(json)      
  
    var y = parseInt(json.XLAT[0].length/2) - 20
    // console.log(y);
    var x = parseInt(json.XLAT.length/2) 
    // console.log(x);
    var lat  = json.XLAT[x][y]
    var long = json.XLONG[x][y]
    var time = json.Time
    var day  = json.Day

    fwflocation
      .setLatLng([lat,long])
      .addTo(map);
  
    var graphDiv = document.getElementById('plot_fwi')
        
    var ffmc = json.FFMC.map(function(value,index) { return value[x][y]; });
    // console.log(ffmc);
    var isi  = json.ISI.map(function(value,index) { return value[x][y]; });
    var fwi  = json.FWI.map(function(value,index) { return value[x][y]; });
    var dsr  = json.DSR.map(function(value,index) { return value[x][y]; });
  
    var dmc  = json.DMC.map(function(value,index) { return value[x][y]; });
    var dc   = json.DC.map(function(value,index) { return value[x][y]; });
    var bui  = json.BUI.map(function(value,index) { return value[x][y]; });
    var values = [["DMC", "DC", "BUI"], [dmc[0], dc[0], bui[0]], [dmc[1], dc[1], bui[1]]];
    // console.log(values);
  
    var ffmc =  {x: time, y: ffmc, type: 'scatter', line: {color: "ff8500"}, yaxis: 'y4', name: 'FFMC'};    
    var isi  =  {x: time, y: isi, type: 'scatter', line: {color: "9900cc"}, yaxis: 'y3', name: 'ISI'};    
    var fwi  =  {x: time, y: fwi, type: 'scatter', line: {color: "0052cc"}, yaxis: 'y2', name: 'FWI'};    
    var dsr  =  {x: time, y: dsr, type: 'scatter', line: {color: "CD2C0A"}, yaxis: 'y1', name: 'DSR'};    
  
    var headerColor = "6F737C"; 
    var rowEvenColor = "white";
    var rowOddColor = "white";
  
    var table = {type: 'table',header: {values: [["<b>Index/Code</b>"], [day[0]],[day[1]]],
                align: "center", line: {width: 1, color: '616161'}, fill: {color: headerColor},
                font: {family: "inherit", size: 12, color: "white"}},
                cells: {values: values, align: "center", line: {color: "616161", width: 1}, 
                fill: {color: [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]]},
                font: {family: "inherit", size: 11, color: ["616161"]}}, xaxis: 'x',yaxis: 'y',domain: {x: [0,1.0], y: [0.8,1.]}};
  
  
    var data = [table, ffmc, isi, fwi, dsr];
    var layout = {
      title: "Fire Weather Forecast <br> Lat: " + lat.toFixed(3) + ", Long: " + long.toFixed(3), 
      titlefont: {
      color: "#7f7f7f", 
      autosize: true
      }, 
      showlegend: false,
      yaxis4: {domain: [0.6, 0.8], title: {text: "FFMC" , font: {color: "ff8500"}}},
      yaxis3: {domain: [0.40, 0.6], title: {text: "ISI" , font: {color: "9900cc"}}},
      yaxis2: {domain: [.2, 0.40], title: {text: "FWI" , font: {color: "0052cc"}}},
      yaxis1: {domain: [0, 0.2], title: {text: "DSR" , font: {color: "CD2C0A"}}},
  
      xaxis: {title: "Date (UTC)"}
    };
  
    Plotly.newPlot(graphDiv, data, layout);
  
  
    var xlat  = json.XLAT
    var xlng = json.XLONG
    var listlat = [];
    var listlng = [];
  
    var dimensions = [ xlat.length, xlat[0].length ];
    // console.log(dimensions);
    var dimensions = [dimensions[1],dimensions[0]]
    // console.log(dimensions);
  
  
    for(var i = 0; i < xlat.length; i++)
    {
        listlat = listlat.concat(xlat[i]);
    }
  
    for(var i = 0; i < xlng.length; i++)
    {
        listlng = listlng.concat(xlng[i]);
    }
  
    var points = listlat.map(function(e, i) {
      return [e, listlng[i]];
    });
    
    const index = new KDBush(points);
    console.log(index);
    
    var note = "New Canada Wide Resolution loaded";
    console.log(note);
  
    // built_tree = 'built-kd-tree.json'
    // var testindex = JSON.parse($.getJSON({'url': built_tree, 'async': false}).responseText);
    // console.log(testindex.range);
  
    // var fwflocation = L.marker();
    function latLngPop(e) {
        // var marker = L.marker([e.latlng.lat.toFixed(4), e.latlng.lng.toFixed(4)]).addTo(map);

        fwflocation
            .setLatLng(e.latlng)
            .addTo(map);


        var p = [parseFloat(e.latlng.lat.toFixed(4)), parseFloat(e.latlng.lng.toFixed(4))] 
        console.log(p);
   
        const results0 = index.range(p[0], p[1], p[0]+0.5, p[1]+0.5).map(id => points[id]);
        console.log(results0);
  
        ll_diff = [];
        function diff(array, latlng){
         for(var i = 0; i < array.length; i++)
                {
              console.log(array[i][0]);
              console.log(latlng[0]);
        
              var first = Math.abs(array[i][0] - latlng[0])
              var second = Math.abs(array[i][1] - latlng[1])
              var sum = first + second
              console.log(sum);
              ll_diff.push(sum); 
                }
              }
         diff(results0, p)
         console.log(ll_diff);
        
        var ll_index = 0;
        var value = ll_diff[0];
        for (var i = 1; i < ll_diff.length; i++) {
          if (ll_diff[i] < value) {
            value = ll_diff[i];
            ll_index = i;
          }
        }
      console.log(ll_index);
  
  
        // var test = Math.abs(parseFloat(results0) - p)
        // console.log(intersection);
  
        const results = index.range(p[0], p[1], p[0]+0.5, p[1]+0.5);
        console.log(results);
  
  
        function ind2sub(sizes, index) {
          var cumprod = sizes.reduce(function (acc, n) { return acc.concat(acc[acc.length - 1] * n); }, [1]);
          return sizes.map(function (size, i) { return Math.floor(index / (cumprod[i])) % size; });
        }
  
        function ind2subNocheck(sizes, index, cumprod) {
          return sizes.map(function (size, i) { return Math.floor(index / (cumprod[i])) % size; });
        }
        function optimizeInd2sub(sizes) {
          var cumprod = sizes.reduce(function (acc, n) { return acc.concat(acc[acc.length - 1] * n); }, [1]);
          return function (index) { return ind2subNocheck(sizes, index, cumprod); };
        }
  
        f = optimizeInd2sub(dimensions)
  
        var yx = ind2sub(dimensions, results[ll_index], f(results[ll_index]))
  
        var x = yx[1]
        var y = yx[0] 
        var xy = [x,y]
        console.log(xy);
  
  
        var lat  = json.XLAT[x][y]
        var long = json.XLONG[x][y]
        var time = json.Time
        var day  = json.Day
      
        var graphDiv = document.getElementById('plot_fwi')
            
        var ffmc = json.FFMC.map(function(value,index) { return value[x][y]; });
        var isi  = json.ISI.map(function(value,index) { return value[x][y]; });
        var fwi  = json.FWI.map(function(value,index) { return value[x][y]; });
        var dsr  = json.DSR.map(function(value,index) { return value[x][y]; });
      
        var dmc  = json.DMC.map(function(value,index) { return value[x][y]; });
        var dc   = json.DC.map(function(value,index) { return value[x][y]; });
        var bui  = json.BUI.map(function(value,index) { return value[x][y]; });
        var values = [["DMC", "DC", "BUI"], [dmc[0], dc[0], bui[0]], [dmc[1], dc[1], bui[1]]];
        // console.log(values);
      
        var ffmc =  {x: time, y: ffmc, type: 'scatter', line: {color: "ff8500"}, yaxis: 'y4', name: 'FFMC'};    
        var isi  =  {x: time, y: isi, type: 'scatter', line: {color: "9900cc"}, yaxis: 'y3', name: 'ISI'};    
        var fwi  =  {x: time, y: fwi, type: 'scatter', line: {color: "0052cc"}, yaxis: 'y2', name: 'FWI'};    
        var dsr  =  {x: time, y: dsr, type: 'scatter', line: {color: "CD2C0A"}, yaxis: 'y1', name: 'DSR'};    
      
        var headerColor = "6F737C";
        var rowEvenColor = "white";
        var rowOddColor = "white";
      
        var table = {type: 'table',header: {values: [["<b>Index/Code</b>"], [day[0]],[day[1]]],
                    align: "center", line: {width: 1, color: '616161'}, fill: {color: headerColor},
                    font: {family: "inherit", size: 12, color: "white"}},
                    cells: {values: values, align: "center", line: {color: "616161", width: 1}, 
                    fill: {color: [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]]},
                    font: {family: "inherit", size: 11, color: ["616161"]}}, xaxis: 'x',yaxis: 'y',domain: {x: [0,1.0], y: [0.8,1.]}};
      
      
        var data = [table, ffmc, isi, fwi, dsr];
        var layout = {
          title: "Fire Weather Forecast <br> Lat: " + lat.toFixed(3) + ", Long: " + long.toFixed(3), 
          titlefont: {
          color: "#7f7f7f", 
          autosize: true
          }, 
          showlegend: false,
          yaxis4: {domain: [0.6, 0.8], title: {text: "FFMC" , font: {color: "ff8500"}}},
          yaxis3: {domain: [0.40, 0.6], title: {text: "ISI" , font: {color: "9900cc"}}},
          yaxis2: {domain: [.2, 0.40], title: {text: "FWI" , font: {color: "0052cc"}}},
          yaxis1: {domain: [0, 0.2], title: {text: "DSR" , font: {color: "CD2C0A"}}},
      
          xaxis: {title: "Date (UTC)"}
        };
    
          Plotly.react(graphDiv, data, layout);}
          map.on('click', latLngPop);
    
  
  });
  
  window.onresize = function () {
    Plotly.Plots.resize(plot_fwi);
  };}