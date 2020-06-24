/******************************************************
 * Map and Layer
 ******************************************************/

class MapWrapper {
    constructor() {
      this.map = undefined;
      this.osmLayer = undefined;
      this.legendControlLayer = undefined;
    }
  
    init(mapId) {
      this.initMap(mapId);
      this.initOpenStreetLayer();
      // this.initLegendControlLayer();
      this.map.setView(new L.LatLng(51.165, 10.451), 5);
      //this.map.setView(new L.LatLng(22.210928, 113.552971), 3);
    }
  
    initMap(mapId) {
      this.map = L.map(mapId, {
        zoom: 6,
        fullscreenControl: true,
        timeDimensionControl: true,
        timeDimensionControlOptions: {
          position: "bottomleft",
          autoPlay: false,
          timeSlider: true,
          loopButton: true,
          minSpeed: 1,
          speedStep: 0.5,
          maxSpeed: 15,
          timeSliderDragUpdate: true,
          playerOptions: {
            transitionTime: 100,
            loop: false,
            startOver: true
          }
        },
        timeDimension: true,
        timeDimensionOptions: {
          timeInterval: "2016-01-01/2040-01-01",
          period: "P1Y",
          currentTime: new Date("2016-01-01").getTime()
        }
      });
    }
  
    initOpenStreetLayer() {
      // create the tile layer with correct attribution
      // map provider list => http://leaflet-extras.github.io/leaflet-providers/preview/
      const osmUrl = "http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png";
      const osmAttrib =
        'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
      this.osmLayer = new L.TileLayer(osmUrl, {
        minZoom: 2,
        maxZoom: 16,
        attribution: osmAttrib
      });
      this.osmLayer.addTo(this.map);
    }
  
    initLegendControlLayer(container, content) {
      this.legendControlLayer = L.control({ position: "bottomright" });
      this.legendControlLayer.onAdd = function(map) {
        const div = L.DomUtil.create(
          "div",
          "info_legend",
          document.getElementById(container)
        );
        if (content) {
          div.innerHTML += content;
          return div;
        }
  
        div.innerHTML +=
          "" +
          "<div class='legend-title'>Power</div>" +
          "<div class='legend-scale'>" +
          "<ul class='legend-labels d-flex flex-column'>" +
          "<li><span style='background:#ff0000;'></span>1000</li>" +
          "<li><span style='background:#ff4a26;'></span>900</li>" +
          "<li><span style='background:#ff6b40;'></span>800</li>" +
          "<li><span style='background:#ff8659;'></span>700</li>" +
          "<li><span style='background:#ff9d70;'></span>600</li>" +
          "<li><span style='background:#ffb186;'></span>500</li>" +
          "<li><span style='background:#ffc69c;'></span>400</li>" +
          "<li><span style='background:#ffd9b3;'></span>300</li>" +
          "<li><span style='background:#ffedca;'></span>200</li>" +
          "<li><span style='background:#ffffe0;'></span>100</li>" +
          "</ul>" +
          "</div>";
  
        return div;
      };
      this.legendControlLayer.addTo(this.map);
    }
  
    addLayer(layer) {
      return this.map.addLayer(layer);
    }
  }
  
  L.TimeDimension.Layer.Power = L.TimeDimension.Layer.GeoJson.extend({
    _getFeatureBetweenDates: function(feature, minTime, maxTime) {
      var featureStringTimes = this._getFeatureTimes(feature);
      if (featureStringTimes.length === 0) {
        return feature;
      }
      var featureTimes = [];
      for (var i = 0, l = featureStringTimes.length; i < l; i++) {
        var time = featureStringTimes[i];
        if (typeof time == "string" || time instanceof String) {
          time = Date.parse(time.trim());
        }
        featureTimes.push(time);
      }
  
      if (featureTimes[0] > maxTime || featureTimes[l - 1] < minTime) {
        return null;
      }
  
      var time = this._timeDimension.getCurrentTime();
      var availableTimes = this._timeDimension.getAvailableTimes();
      //console.log(availableTimes.length)
      var index = availableTimes.indexOf(time);
  
      if (index <= -1) {
        return null;
      } else {
        if (feature.properties.power[index] != 0) {
          feature.properties.currentPower = feature.properties.power[index];
          feature.properties.color = this._getFeatureColor(
            feature,
            this._baseLayer.options
          );
          return feature;
        } else {
          return null;
        }
      }
      return feature;
    },
  
    _update: function() {
      L.TimeDimension.Layer.GeoJson.prototype._update.call(this);
  
      //this._currentLayer.setStyle(this._getFeatureStyle);
      this._currentLayer.bindTooltip(this._getFeatureTooltip);
  
      var self = this;
      var gridLayers = this._currentLayer._layers;
      var lastHoverLayer;
  
      for (var gridLayerId in gridLayers) {
        // currentLayer is the layerGroup
        // each grid is also considered as a layer
        gridLayers[gridLayerId].on({
          mouseover: function(evt) {
            // needs a deep copy to reset the style
            lastHoverLayer = $.extend(true, {}, evt.target);
            self._highlightFeature(evt.target);
          },
          mouseout: function(evt) {
            evt.target.setStyle(lastHoverLayer.options);
          }
          //click: zoomToFeature
        });
      }
    },
  
    _getFeatureColor: function(feature, options) {
      var bounds = options["classification"]["bounds"];
      var colors = options["classification"]["colors"];
  
      var currentPower = feature.properties.currentPower;
      var color = "";
  
      for (var i = 0; i < bounds.length; i++) {
        // [min max]
        if (currentPower <= bounds[i] && currentPower >= bounds[i + 1]) {
          color = colors[i];
          break;
        }
      }
  
      return color;
    },
  
    _getFeatureStyle: function(feature) {
      var styles = [
        "#ffffe0",
        "#ffedca",
        "#ffd9b3",
        "#ffc69c",
        "#ffb186",
        "#ff9d70",
        "#ff8659",
        "#ff6b40",
        "#ff4a26",
        "#ff0000"
      ];
  
      var color = undefined;
      var power = feature.properties.currentPower;
      if (power < 100) {
        color = styles[0];
      } else if (power >= 100 && power < 200) {
        color = styles[1];
      } else if (power >= 200 && power < 300) {
        color = styles[2];
      } else if (power >= 300 && power < 400) {
        color = styles[3];
      } else if (power >= 400 && power < 500) {
        color = styles[4];
      } else if (power >= 500 && power < 600) {
        color = styles[5];
      } else if (power >= 600 && power < 700) {
        color = styles[6];
      } else if (power >= 700 && power < 800) {
        color = styles[7];
      } else if (power >= 800 && power < 900) {
        color = styles[8];
      } else {
        color = styles[9];
      }
  
      return {
        weight: 2,
        opacity: 1,
        color: color,
        dashArray: "3",
        fillOpacity: 0.5
      };
    },
  
    _getFeatureTooltip: function(layer) {
      //return layer.feature.properties.currentPower + " " + "MW";
      var cellId = layer.feature.properties["cell_id"];
      var adminId = layer.feature.properties["adminlvl4_"];
      var power = layer.feature.properties.currentPower;
  
      return (
        '<table class="table table-striped table-bordered tooltip-table"><tbody><tr><th scope="row">cell id</th><td>' +
        cellId +
        '</td></tr><tr><th scope="row">admin id</th><td>' +
        adminId +
        '</td></tr><tr><th scope="row">power</th><td>' +
        power +
        " MW</td></tr></tbody></table>"
      );
    },
  
    _highlightFeature: function(layer) {
      layer.setStyle({
        weight: 5,
        color: "#666",
        dashArray: ""
        //fillOpacity: 0.7
      });
      if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
      }
    }
  });
  
  /******************************************************
   * Main Code
   ******************************************************/
  
  var cellFeatures = getGeojsonByCell();
  var adminUnitFeatures = getGeojsonByAdminUnit();
  
  updateGeojson(cellFeatures, adminUnitFeatures);
  
  //TODO needs user intereaction to switch one to another
  //TODO needs color selection and classification (gonna reverse the QGIS Categroized)
  var geofeatures = cellFeatures;
  //var geofeatures = adminUnitFeatures;
  var classification = getClassification(geofeatures, 10);
  var legendContent = getDynamicLegend(classification);
  
  var myMap = new MapWrapper();
  myMap.init("map");
  myMap.initLegendControlLayer("legend-container", legendContent);
  
  var geojsonLayer = L.geoJSON(geofeatures, {
    style: setDynamicStyle,
    classification: classification
  });
  
  var powerLayer = new L.TimeDimension.Layer.Power(geojsonLayer, {
    // updateTimeDimension: true,
    // updateTimeDimensionMode: 'replace',
    // addlastPoint: false,
    // duration: 'P1Y',
  });
  
  myMap.addLayer(powerLayer);
  myMap.map.flyToBounds(toLatLngBounds(d3.geoBounds(geofeatures)), {
    maxZoom: 7
  });
  
  /******************************************************
   * Helper Function for Fake Data
   ******************************************************/
  function setStyle(feature) {
    var styles = [
      "#ffffe0",
      "#ffedca",
      "#ffd9b3",
      "#ffc69c",
      "#ffb186",
      "#ff9d70",
      "#ff8659",
      "#ff6b40",
      "#ff4a26",
      "#ff0000"
    ];
  
    var color = undefined;
    var power = feature.properties.currentPower;
    if (power < 100) {
      color = styles[0];
    } else if (power >= 100 && power < 200) {
      color = styles[1];
    } else if (power >= 200 && power < 300) {
      color = styles[2];
    } else if (power >= 300 && power < 400) {
      color = styles[3];
    } else if (power >= 400 && power < 500) {
      color = styles[4];
    } else if (power >= 500 && power < 600) {
      color = styles[5];
    } else if (power >= 600 && power < 700) {
      color = styles[6];
    } else if (power >= 700 && power < 800) {
      color = styles[7];
    } else if (power >= 800 && power < 900) {
      color = styles[8];
    } else {
      color = styles[9];
    }
  
    return {
      weight: 2,
      opacity: 1,
      color: color,
      dashArray: "3",
      fillOpacity: 0.5
    };
  }
  
  function setDynamicStyle(feature) {
    return {
      weight: 2,
      opacity: 1,
      color: feature.properties.color,
      dashArray: "3",
      fillOpacity: 0.5
    };
  }
  
  function toLatLngBounds(d3GeoBounds) {
    // d3 is LngLat (southeast & northwest), LatLngBounds (northeast & southwest)
    var dst = [
      [d3GeoBounds[1][1], d3GeoBounds[0][0]],
      [d3GeoBounds[0][1], d3GeoBounds[1][0]]
    ];
  
    return L.latLngBounds(dst);
  }
  
  function createTimes(startYear, endYear) {
    var times = [];
    for (var i = startYear; i <= endYear; i++) {
      times.push(i.toString());
    }
    return times;
  }
  
  function createPower(length, min, max) {
    return Array.apply(null, Array(length)).map(function(item) {
      return createRandomNumer(min, max);
    });
  }
  
  function createRandomNumer(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
    //return (Math.random() * (max - min + 1) + min).toFixed(2);
  }
  
  function getGeojsonByCell() {
    return JSON.parse(
      '{"type":"FeatureCollection","totalFeatures":104,"features":[{"type":"Feature","id":"GEOCELLS-BELGIUM.1","geometry":{"type":"MultiPolygon","coordinates":[[[[3.9725969784827426,50.68230473407699],[3.9507285681537736,50.864457467578184],[4.239406244775241,50.87796155603962],[4.2601650205565,50.695758011546765],[3.9725969784827426,50.68230473407699]]]]},"geometry_name":"the_geom","properties":{"cell_id":11040,"v100":6.08,"k":2.21,"a":6.89,"adminlvl4_":1}},{"type":"Feature","id":"GEOCELLS-BELGIUM.2","geometry":{"type":"MultiPolygon","coordinates":[[[[4.2601650205565,50.695758011546765],[4.239406244775241,50.87796155603962],[4.528246075106862,50.89075775789844],[4.547893282178777,50.70850339296468],[4.2601650205565,50.695758011546765]]]]},"geometry_name":"the_geom","properties":{"cell_id":11188,"v100":5.91,"k":2.26,"a":6.7,"adminlvl4_":1}},{"type":"Feature","id":"GEOCELLS-BELGIUM.3","geometry":{"type":"MultiPolygon","coordinates":[[[[4.239406244775241,50.87796155603962],[4.218485786981648,51.060158297181204],[4.508445241523026,51.07300150969984],[4.528246075106862,50.89075775789844],[4.239406244775241,50.87796155603962]]]]},"geometry_name":"the_geom","properties":{"cell_id":11189,"v100":5.86,"k":2.23,"a":6.63,"adminlvl4_":1}},{"type":"Feature","id":"GEOCELLS-BELGIUM.4","geometry":{"type":"MultiPolygon","coordinates":[[[[3.9507285681537736,50.864457467578184],[3.9286894800569168,51.046603391742785],[4.218485786981648,51.060158297181204],[4.239406244775241,50.87796155603962],[3.9507285681537736,50.864457467578184]]]]},"geometry_name":"the_geom","properties":{"cell_id":11041,"v100":5.97,"k":2.26,"a":6.76,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.5","geometry":{"type":"MultiPolygon","coordinates":[[[[3.9286894800569168,51.046603391742785],[3.906478740678488,51.22873488065439],[4.197401245420235,51.24234060736009],[4.218485786981648,51.060158297181204],[3.9286894800569168,51.046603391742785]]]]},"geometry_name":"the_geom","properties":{"cell_id":11042,"v100":5.98,"k":2.24,"a":6.77,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.6","geometry":{"type":"MultiPolygon","coordinates":[[[[4.218485786981648,51.060158297181204],[4.197401245420235,51.24234060736009],[4.488489784474935,51.25523465184718],[4.508445241523026,51.07300150969984],[4.218485786981648,51.060158297181204]]]]},"geometry_name":"the_geom","properties":{"cell_id":11190,"v100":5.72,"k":2.3,"a":6.48,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.7","geometry":{"type":"MultiPolygon","coordinates":[[[[4.197401245420235,51.24234060736009],[4.17615161232024,51.42451230493234],[4.468377278727766,51.43745718623991],[4.488489784474935,51.25523465184718],[4.197401245420235,51.24234060736009]]]]},"geometry_name":"the_geom","properties":{"cell_id":11191,"v100":5.98,"k":2.29,"a":6.77,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.8","geometry":{"type":"MultiPolygon","coordinates":[[[[4.17615161232024,51.42451230493234],[4.154734473797748,51.606669577088184],[4.448106261267361,51.61966530107743],[4.468377278727766,51.43745718623991],[4.17615161232024,51.42451230493234]]]]},"geometry_name":"the_geom","properties":{"cell_id":11192,"v100":6.45,"k":2.19,"a":7.28,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.9","geometry":{"type":"MultiPolygon","coordinates":[[[[4.528246075106862,50.89075775789844],[4.508445241523026,51.07300150969984],[4.798560263829029,51.085136832087684],[4.817239062021159,50.90284605952743],[4.528246075106862,50.89075775789844]]]]},"geometry_name":"the_geom","properties":{"cell_id":11337,"v100":6.09,"k":2.17,"a":6.89,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.10","geometry":{"type":"MultiPolygon","coordinates":[[[[4.508445241523026,51.07300150969984],[4.488489784474935,51.25523465184718],[4.779734886424873,51.26741699997058],[4.798560263829029,51.085136832087684],[4.508445241523026,51.07300150969984]]]]},"geometry_name":"the_geom","properties":{"cell_id":11338,"v100":5.91,"k":2.22,"a":6.69,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.11","geometry":{"type":"MultiPolygon","coordinates":[[[[4.488489784474935,51.25523465184718],[4.468377278727766,51.43745718623991],[4.76076193126402,51.44968656663803],[4.779734886424873,51.26741699997058],[4.488489784474935,51.25523465184718]]]]},"geometry_name":"the_geom","properties":{"cell_id":11339,"v100":6.01,"k":2.27,"a":6.8,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.12","geometry":{"type":"MultiPolygon","coordinates":[[[[4.468377278727766,51.43745718623991],[4.448106261267361,51.61966530107743],[4.741638982846728,51.63194171912379],[4.76076193126402,51.44968656663803],[4.468377278727766,51.43745718623991]]]]},"geometry_name":"the_geom","properties":{"cell_id":11340,"v100":6.33,"k":2.23,"a":7.16,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.13","geometry":{"type":"MultiPolygon","coordinates":[[[[4.817239062021159,50.90284605952743],[4.798560263829029,51.085136832087684],[5.0888209164173555,51.09656043469818],[5.106376207891163,50.914226447134965],[4.817239062021159,50.90284605952743]]]]},"geometry_name":"the_geom","properties":{"cell_id":11485,"v100":6.08,"k":2.18,"a":6.89,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.14","geometry":{"type":"MultiPolygon","coordinates":[[[[4.798560263829029,51.085136832087684],[4.779734886424873,51.26741699997058],[5.071128042261177,51.27888382370678],[5.0888209164173555,51.09656043469818],[4.798560263829029,51.085136832087684]]]]},"geometry_name":"the_geom","properties":{"cell_id":11486,"v100":5.93,"k":2.22,"a":6.72,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.15","geometry":{"type":"MultiPolygon","coordinates":[[[[4.779734886424873,51.26741699997058],[4.76076193126402,51.44968656663803],[5.0532960988769,51.461200431827145],[5.071128042261177,51.27888382370678],[4.779734886424873,51.26741699997058]]]]},"geometry_name":"the_geom","properties":{"cell_id":11487,"v100":5.93,"k":2.29,"a":6.72,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.16","geometry":{"type":"MultiPolygon","coordinates":[[[[4.76076193126402,51.44968656663803],[4.741638982846728,51.63194171912379],[5.035323168379619,51.64349881694092],[5.0532960988769,51.461200431827145],[4.76076193126402,51.44968656663803]]]]},"geometry_name":"the_geom","properties":{"cell_id":11488,"v100":6.17,"k":2.27,"a":7,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.17","geometry":{"type":"MultiPolygon","coordinates":[[[[5.106376207891163,50.914226447134965],[5.0888209164173555,51.09656043469818],[5.379219629538621,51.10727230523486],[5.395649477415977,50.92489509310858],[5.106376207891163,50.914226447134965]]]]},"geometry_name":"the_geom","properties":{"cell_id":11633,"v100":5.9,"k":2.22,"a":6.69,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.18","geometry":{"type":"MultiPolygon","coordinates":[[[[5.0888209164173555,51.09656043469818],[5.071128042261177,51.27888382370678],[5.362660720092644,51.28963892447837],[5.379219629538621,51.10727230523486],[5.0888209164173555,51.09656043469818]]]]},"geometry_name":"the_geom","properties":{"cell_id":11634,"v100":5.92,"k":2.23,"a":6.71,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.19","geometry":{"type":"MultiPolygon","coordinates":[[[[5.071128042261177,51.27888382370678],[5.0532960988769,51.461200431827145],[5.345971273041479,51.471994953612835],[5.362660720092644,51.28963892447837],[5.071128042261177,51.27888382370678]]]]},"geometry_name":"the_geom","properties":{"cell_id":11635,"v100":5.91,"k":2.32,"a":6.71,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.20","geometry":{"type":"MultiPolygon","coordinates":[[[[5.0532960988769,51.461200431827145],[5.035323168379619,51.64349881694092],[5.32915029883929,51.65433658116946],[5.345971273041479,51.471994953612835],[5.0532960988769,51.461200431827145]]]]},"geometry_name":"the_geom","properties":{"cell_id":11636,"v100":6.1,"k":2.29,"a":6.92,"adminlvl4_":2}},{"type":"Feature","id":"GEOCELLS-BELGIUM.21","geometry":{"type":"MultiPolygon","coordinates":[[[[4.8357732304672885,50.72054467997195],[4.817239062021159,50.90284605952743],[5.106376207891163,50.914226447134965],[5.123795866972859,50.73188185877223],[4.8357732304672885,50.72054467997195]]]]},"geometry_name":"the_geom","properties":{"cell_id":11484,"v100":6.23,"k":2.14,"a":7.04,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.22","geometry":{"type":"MultiPolygon","coordinates":[[[[5.141080880568269,50.549530481034374],[5.123795866972859,50.73188185877223],[5.411952679642262,50.74251110121764],[5.428129759208383,50.560120325721826],[5.141080880568269,50.549530481034374]]]]},"geometry_name":"the_geom","properties":{"cell_id":11631,"v100":6.1,"k":2.12,"a":6.89,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.23","geometry":{"type":"MultiPolygon","coordinates":[[[[5.123795866972859,50.73188185877223],[5.106376207891163,50.914226447134965],[5.395649477415977,50.92489509310858],[5.411952679642262,50.74251110121764],[5.123795866972859,50.73188185877223]]]]},"geometry_name":"the_geom","properties":{"cell_id":11632,"v100":6,"k":2.16,"a":6.79,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.24","geometry":{"type":"MultiPolygon","coordinates":[[[[5.428129759208383,50.560120325721826],[5.411952679642262,50.74251110121764],[5.700235145033228,50.75243239374409],[5.715303294596349,50.5700060269191],[5.428129759208383,50.560120325721826]]]]},"geometry_name":"the_geom","properties":{"cell_id":11779,"v100":5.95,"k":2.17,"a":6.72,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.25","geometry":{"type":"MultiPolygon","coordinates":[[[[5.411952679642262,50.74251110121764],[5.395649477415977,50.92489509310858],[5.685050336791418,50.9348557986571],[5.700235145033228,50.75243239374409],[5.411952679642262,50.74251110121764]]]]},"geometry_name":"the_geom","properties":{"cell_id":11780,"v100":5.91,"k":2.16,"a":6.69,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.26","geometry":{"type":"MultiPolygon","coordinates":[[[[5.395649477415977,50.92489509310858],[5.379219629538621,51.10727230523486],[5.6697469295206995,51.11727242905283],[5.685050336791418,50.9348557986571],[5.395649477415977,50.92489509310858]]]]},"geometry_name":"the_geom","properties":{"cell_id":11781,"v100":5.88,"k":2.2,"a":6.67,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.27","geometry":{"type":"MultiPolygon","coordinates":[[[[5.379219629538621,51.10727230523486],[5.362660720092644,51.28963892447837],[5.654322982421711,51.29967847229187],[5.6697469295206995,51.11727242905283],[5.379219629538621,51.10727230523486]]]]},"geometry_name":"the_geom","properties":{"cell_id":11782,"v100":6.02,"k":2.22,"a":6.83,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.28","geometry":{"type":"MultiPolygon","coordinates":[[[[5.362660720092644,51.28963892447837],[5.345971273041479,51.471994953612835],[5.638777981785141,51.48207011736092],[5.654322982421711,51.29967847229187],[5.362660720092644,51.28963892447837]]]]},"geometry_name":"the_geom","properties":{"cell_id":11783,"v100":6.07,"k":2.27,"a":6.9,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.29","geometry":{"type":"MultiPolygon","coordinates":[[[[5.715303294596349,50.5700060269191],[5.700235145033228,50.75243239374409],[5.9886352039052735,50.76164953793316],[6.002592486122423,50.57918757035642],[5.715303294596349,50.5700060269191]]]]},"geometry_name":"the_geom","properties":{"cell_id":11927,"v100":6.29,"k":2.12,"a":7.09,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.30","geometry":{"type":"MultiPolygon","coordinates":[[[[5.700235145033228,50.75243239374409],[5.685050336791418,50.9348557986571],[5.974569786839182,50.944108549522426],[5.9886352039052735,50.76164953793316],[5.700235145033228,50.75243239374409]]]]},"geometry_name":"the_geom","properties":{"cell_id":11928,"v100":6.06,"k":2.15,"a":6.85,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.31","geometry":{"type":"MultiPolygon","coordinates":[[[[5.685050336791418,50.9348557986571],[5.6697469295206995,51.11727242905283],[5.960393817991361,51.12656079189132],[5.974569786839182,50.944108549522426],[5.685050336791418,50.9348557986571]]]]},"geometry_name":"the_geom","properties":{"cell_id":11929,"v100":5.91,"k":2.19,"a":6.71,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.32","geometry":{"type":"MultiPolygon","coordinates":[[[[5.6697469295206995,51.11727242905283],[5.654322982421711,51.29967847229187],[5.946107259265034,51.30900245455172],[5.960393817991361,51.12656079189132],[5.6697469295206995,51.11727242905283]]]]},"geometry_name":"the_geom","properties":{"cell_id":11930,"v100":6.01,"k":2.21,"a":6.84,"adminlvl4_":3}},{"type":"Feature","id":"GEOCELLS-BELGIUM.33","geometry":{"type":"MultiPolygon","coordinates":[[[[3.39797344385005,50.653293613844035],[3.3738918339656188,50.83533330976154],[3.662220841489773,50.85024931938826],[3.685196704316028,50.66815120188834],[3.39797344385005,50.653293613844035]]]]},"geometry_name":"the_geom","properties":{"cell_id":10744,"v100":6.15,"k":2.26,"a":6.97,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.34","geometry":{"type":"MultiPolygon","coordinates":[[[[3.3738918339656188,50.83533330976154],[3.3496229838888976,51.0173661861466],[3.6390657923846836,51.03233680738566],[3.662220841489773,50.85024931938826],[3.3738918339656188,50.83533330976154]]]]},"geometry_name":"the_geom","properties":{"cell_id":10745,"v100":6.22,"k":2.29,"a":7.06,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.35","geometry":{"type":"MultiPolygon","coordinates":[[[[3.3496229838888976,51.0173661861466],[3.32516473198389,51.199384615889336],[3.615730075750619,51.21441748382241],[3.6390657923846836,51.03233680738566],[3.3496229838888976,51.0173661861466]]]]},"geometry_name":"the_geom","properties":{"cell_id":10746,"v100":6.4,"k":2.31,"a":7.27,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.36","geometry":{"type":"MultiPolygon","coordinates":[[[[3.32516473198389,51.199384615889336],[3.3005144078171775,51.381392415681084],[3.592211301806947,51.396479906440334],[3.615730075750619,51.21441748382241],[3.32516473198389,51.199384615889336]]]]},"geometry_name":"the_geom","properties":{"cell_id":10747,"v100":6.85,"k":2.24,"a":7.76,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.37","geometry":{"type":"MultiPolygon","coordinates":[[[[3.685196704316028,50.66815120188834],[3.662220841489773,50.85024931938826],[3.9507285681537736,50.864457467578184],[3.9725969784827426,50.68230473407699],[3.685196704316028,50.66815120188834]]]]},"geometry_name":"the_geom","properties":{"cell_id":10892,"v100":6.3,"k":2.19,"a":7.13,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.38","geometry":{"type":"MultiPolygon","coordinates":[[[[3.662220841489773,50.85024931938826],[3.6390657923846836,51.03233680738566],[3.9286894800569168,51.046603391742785],[3.9507285681537736,50.864457467578184],[3.662220841489773,50.85024931938826]]]]},"geometry_name":"the_geom","properties":{"cell_id":10893,"v100":6.32,"k":2.21,"a":7.16,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.39","geometry":{"type":"MultiPolygon","coordinates":[[[[3.6390657923846836,51.03233680738566],[3.615730075750619,51.21441748382241],[3.906478740678488,51.22873488065439],[3.9286894800569168,51.046603391742785],[3.6390657923846836,51.03233680738566]]]]},"geometry_name":"the_geom","properties":{"cell_id":10894,"v100":6.35,"k":2.21,"a":7.18,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.40","geometry":{"type":"MultiPolygon","coordinates":[[[[3.615730075750619,51.21441748382241],[3.592211301806947,51.396479906440334],[3.884093450903631,51.4108519357629],[3.906478740678488,51.22873488065439],[3.615730075750619,51.21441748382241]]]]},"geometry_name":"the_geom","properties":{"cell_id":10895,"v100":6.56,"k":2.21,"a":7.41,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.41","geometry":{"type":"MultiPolygon","coordinates":[[[[3.906478740678488,51.22873488065439],[3.884093450903631,51.4108519357629],[4.17615161232024,51.42451230493234],[4.197401245420235,51.24234060736009],[3.906478740678488,51.22873488065439]]]]},"geometry_name":"the_geom","properties":{"cell_id":11043,"v100":6.26,"k":2.19,"a":7.06,"adminlvl4_":4}},{"type":"Feature","id":"GEOCELLS-BELGIUM.42","geometry":{"type":"MultiPolygon","coordinates":[[[[3.994297133405291,50.50014518923335],[3.9725969784827426,50.68230473407699],[4.2601650205565,50.695758011546765],[4.280764061672069,50.513547661230064],[3.994297133405291,50.50014518923335]]]]},"geometry_name":"the_geom","properties":{"cell_id":11039,"v100":6.22,"k":2.16,"a":7.04,"adminlvl4_":5}},{"type":"Feature","id":"GEOCELLS-BELGIUM.43","geometry":{"type":"MultiPolygon","coordinates":[[[[4.280764061672069,50.513547661230064],[4.2601650205565,50.695758011546765],[4.547893282178777,50.70850339296468],[4.567389275702394,50.52624222781981],[4.280764061672069,50.513547661230064]]]]},"geometry_name":"the_geom","properties":{"cell_id":11187,"v100":6.11,"k":2.19,"a":6.92,"adminlvl4_":5}},{"type":"Feature","id":"GEOCELLS-BELGIUM.44","geometry":{"type":"MultiPolygon","coordinates":[[[[4.547893282178777,50.70850339296468],[4.528246075106862,50.89075775789844],[4.817239062021159,50.90284605952743],[4.8357732304672885,50.72054467997195],[4.547893282178777,50.70850339296468]]]]},"geometry_name":"the_geom","properties":{"cell_id":11336,"v100":6.11,"k":2.21,"a":6.92,"adminlvl4_":5}},{"type":"Feature","id":"GEOCELLS-BELGIUM.45","geometry":{"type":"MultiPolygon","coordinates":[[[[4.8541642311815325,50.53823650532439],[4.8357732304672885,50.72054467997195],[5.123795866972859,50.73188185877223],[5.141080880568269,50.549530481034374],[4.8541642311815325,50.53823650532439]]]]},"geometry_name":"the_geom","properties":{"cell_id":11483,"v100":6.34,"k":2.1,"a":7.15,"adminlvl4_":5}},{"type":"Feature","id":"GEOCELLS-BELGIUM.46","geometry":{"type":"MultiPolygon","coordinates":[[[[2.5374478256753488,50.604508080839445],[2.510062973455171,50.78636112695867],[2.7978044994740014,50.80338920130075],[2.824090608551017,50.62147013368869],[2.5374478256753488,50.604508080839445]]]]},"geometry_name":"the_geom","properties":{"cell_id":10300,"v100":6.47,"k":2.15,"a":7.31,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.47","geometry":{"type":"MultiPolygon","coordinates":[[[[2.510062973455171,50.78636112695867],[2.4824653375064902,50.968203523191264],[2.771314124318399,50.98529762416802],[2.7978044994740014,50.80338920130075],[2.510062973455171,50.78636112695867]]]]},"geometry_name":"the_geom","properties":{"cell_id":10301,"v100":6.64,"k":2.23,"a":7.52,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.48","geometry":{"type":"MultiPolygon","coordinates":[[[[2.4824653375064902,50.968203523191264],[2.4546529751384534,51.150035272440576],[2.7446173016116107,51.16719540485568],[2.771314124318399,50.98529762416802],[2.4824653375064902,50.968203523191264]]]]},"geometry_name":"the_geom","properties":{"cell_id":10302,"v100":7.15,"k":2.21,"a":8.1,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.49","geometry":{"type":"MultiPolygon","coordinates":[[[[2.824090608551017,50.62147013368869],[2.7978044994740014,50.80338920130075],[3.085750292719318,50.81971326633546],[3.110935231394411,50.63773579677103],[2.824090608551017,50.62147013368869]]]]},"geometry_name":"the_geom","properties":{"cell_id":10448,"v100":6.2,"k":2.21,"a":7.01,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.50","geometry":{"type":"MultiPolygon","coordinates":[[[[2.7978044994740014,50.80338920130075],[2.771314124318399,50.98529762416802],[3.0603695954720633,51.00168391107814],[3.085750292719318,50.81971326633546],[2.7978044994740014,50.80338920130075]]]]},"geometry_name":"the_geom","properties":{"cell_id":10449,"v100":6.51,"k":2.21,"a":7.37,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.51","geometry":{"type":"MultiPolygon","coordinates":[[[[2.771314124318399,50.98529762416802],[2.7446173016116107,51.16719540485568],[3.034790730008086,51.18364391849403],[3.0603695954720633,51.00168391107814],[2.771314124318399,50.98529762416802]]]]},"geometry_name":"the_geom","properties":{"cell_id":10450,"v100":6.84,"k":2.27,"a":7.77,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.52","geometry":{"type":"MultiPolygon","coordinates":[[[[2.7446173016116107,51.16719540485568],[2.717711633062595,51.34907491609822],[3.0090117621734818,51.365589476583445],[3.034790730008086,51.18364391849403],[2.7446173016116107,51.16719540485568]]]]},"geometry_name":"the_geom","properties":{"cell_id":10451,"v100":7.52,"k":2.17,"a":8.52,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.53","geometry":{"type":"MultiPolygon","coordinates":[[[[3.110935231394411,50.63773579677103],[3.085750292719318,50.81971326633546],[3.3738918339656188,50.83533330976154],[3.39797344385005,50.653293613844035],[3.110935231394411,50.63773579677103]]]]},"geometry_name":"the_geom","properties":{"cell_id":10596,"v100":6,"k":2.29,"a":6.81,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.54","geometry":{"type":"MultiPolygon","coordinates":[[[[3.085750292719318,50.81971326633546],[3.0603695954720633,51.00168391107814],[3.3496229838888976,51.0173661861466],[3.3738918339656188,50.83533330976154],[3.085750292719318,50.81971326633546]]]]},"geometry_name":"the_geom","properties":{"cell_id":10597,"v100":6.25,"k":2.27,"a":7.09,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.55","geometry":{"type":"MultiPolygon","coordinates":[[[[3.0603695954720633,51.00168391107814],[3.034790730008086,51.18364391849403],[3.32516473198389,51.199384615889336],[3.3496229838888976,51.0173661861466],[3.0603695954720633,51.00168391107814]]]]},"geometry_name":"the_geom","properties":{"cell_id":10598,"v100":6.53,"k":2.32,"a":7.43,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.56","geometry":{"type":"MultiPolygon","coordinates":[[[[3.034790730008086,51.18364391849403],[3.0090117621734818,51.365589476583445],[3.3005144078171775,51.381392415681084],[3.32516473198389,51.199384615889336],[3.034790730008086,51.18364391849403]]]]},"geometry_name":"the_geom","properties":{"cell_id":10599,"v100":7.17,"k":2.19,"a":8.13,"adminlvl4_":6}},{"type":"Feature","id":"GEOCELLS-BELGIUM.57","geometry":{"type":"MultiPolygon","coordinates":[[[[4.567389275702394,50.52624222781981],[4.547893282178777,50.70850339296468],[4.8357732304672885,50.72054467997195],[4.8541642311815325,50.53823650532439],[4.567389275702394,50.52624222781981]]]]},"geometry_name":"the_geom","properties":{"cell_id":11335,"v100":6.19,"k":2.17,"a":7.01,"adminlvl4_":7}},{"type":"Feature","id":"GEOCELLS-BELGIUM.58","geometry":{"type":"MultiPolygon","coordinates":[[[[3.1359268524023425,50.455743870738196],[3.110935231394411,50.63773579677103],[3.39797344385005,50.653293613844035],[3.4218699963173926,50.471247095971954],[3.1359268524023425,50.455743870738196]]]]},"geometry_name":"the_geom","properties":{"cell_id":10595,"v100":5.97,"k":2.22,"a":6.76,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.59","geometry":{"type":"MultiPolygon","coordinates":[[[[3.4455834460756054,50.28918993882222],[3.4218699963173926,50.471247095971954],[3.7079960294369396,50.48604626784857],[3.7306207618785012,50.30393451470654],[3.4455834460756054,50.28918993882222]]]]},"geometry_name":"the_geom","properties":{"cell_id":10742,"v100":6.09,"k":2.21,"a":6.9,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.60","geometry":{"type":"MultiPolygon","coordinates":[[[[3.4218699963173926,50.471247095971954],[3.39797344385005,50.653293613844035],[3.685196704316028,50.66815120188834],[3.7079960294369396,50.48604626784857],[3.4218699963173926,50.471247095971954]]]]},"geometry_name":"the_geom","properties":{"cell_id":10743,"v100":6.07,"k":2.24,"a":6.88,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.61","geometry":{"type":"MultiPolygon","coordinates":[[[[3.7306207618785012,50.30393451470654],[3.7079960294369396,50.48604626784857],[3.994297133405291,50.50014518923335],[4.015830492289901,50.31798264470854],[3.7306207618785012,50.30393451470654]]]]},"geometry_name":"the_geom","properties":{"cell_id":10890,"v100":6.15,"k":2.21,"a":6.97,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.62","geometry":{"type":"MultiPolygon","coordinates":[[[[3.7079960294369396,50.48604626784857],[3.685196704316028,50.66815120188834],[3.9725969784827426,50.68230473407699],[3.994297133405291,50.50014518923335],[3.7079960294369396,50.48604626784857]]]]},"geometry_name":"the_geom","properties":{"cell_id":10891,"v100":6.16,"k":2.22,"a":6.98,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.63","geometry":{"type":"MultiPolygon","coordinates":[[[[4.079452119237695,49.77146936226997],[4.058406527193112,49.95364091951926],[4.341620305068973,49.96688719317801],[4.361597446318124,49.7846648516254],[4.079452119237695,49.77146936226997]]]]},"geometry_name":"the_geom","properties":{"cell_id":11035,"v100":5.9,"k":2.37,"a":6.7,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.64","geometry":{"type":"MultiPolygon","coordinates":[[[[4.058406527193112,49.95364091951926],[4.03719996277493,50.13581328440926],[4.321489763490684,50.14911034708391],[4.341620305068973,49.96688719317801],[4.058406527193112,49.95364091951926]]]]},"geometry_name":"the_geom","properties":{"cell_id":11036,"v100":6.01,"k":2.36,"a":6.83,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.65","geometry":{"type":"MultiPolygon","coordinates":[[[[4.03719996277493,50.13581328440926],[4.015830492289901,50.31798264470854],[4.301205314767396,50.331330502669225],[4.321489763490684,50.14911034708391],[4.03719996277493,50.13581328440926]]]]},"geometry_name":"the_geom","properties":{"cell_id":11037,"v100":6.25,"k":2.22,"a":7.08,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.66","geometry":{"type":"MultiPolygon","coordinates":[[[[4.015830492289901,50.31798264470854],[3.994297133405291,50.50014518923335],[4.280764061672069,50.513547661230064],[4.301205314767396,50.331330502669225],[4.015830492289901,50.31798264470854]]]]},"geometry_name":"the_geom","properties":{"cell_id":11038,"v100":6.33,"k":2.15,"a":7.16,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.67","geometry":{"type":"MultiPolygon","coordinates":[[[[4.361597446318124,49.7846648516254],[4.341620305068973,49.96688719317801],[4.62498652739979,49.979440792530255],[4.643894227070258,49.79717147332022],[4.361597446318124,49.7846648516254]]]]},"geometry_name":"the_geom","properties":{"cell_id":11183,"v100":5.91,"k":2.36,"a":6.7,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.68","geometry":{"type":"MultiPolygon","coordinates":[[[[4.341620305068973,49.96688719317801],[4.321489763490684,50.14911034708391],[4.605934427548672,50.16171093048364],[4.62498652739979,49.979440792530255],[4.341620305068973,49.96688719317801]]]]},"geometry_name":"the_geom","properties":{"cell_id":11184,"v100":5.95,"k":2.36,"a":6.76,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.69","geometry":{"type":"MultiPolygon","coordinates":[[[[4.321489763490684,50.14911034708391],[4.301205314767396,50.331330502669225],[4.586735992406713,50.34397807480952],[4.605934427548672,50.16171093048364],[4.321489763490684,50.14911034708391]]]]},"geometry_name":"the_geom","properties":{"cell_id":11185,"v100":6.16,"k":2.24,"a":6.98,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.70","geometry":{"type":"MultiPolygon","coordinates":[[[[4.301205314767396,50.331330502669225],[4.280764061672069,50.513547661230064],[4.567389275702394,50.52624222781981],[4.586735992406713,50.34397807480952],[4.301205314767396,50.331330502669225]]]]},"geometry_name":"the_geom","properties":{"cell_id":11186,"v100":6.31,"k":2.13,"a":7.13,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.71","geometry":{"type":"MultiPolygon","coordinates":[[[[4.605934427548672,50.16171093048364],[4.586735992406713,50.34397807480952],[4.872414477486676,50.355925348549036],[4.890524965416519,50.17361120626065],[4.605934427548672,50.16171093048364]]]]},"geometry_name":"the_geom","properties":{"cell_id":11333,"v100":6.13,"k":2.19,"a":6.92,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.72","geometry":{"type":"MultiPolygon","coordinates":[[[[4.586735992406713,50.34397807480952],[4.567389275702394,50.52624222781981],[4.8541642311815325,50.53823650532439],[4.872414477486676,50.355925348549036],[4.586735992406713,50.34397807480952]]]]},"geometry_name":"the_geom","properties":{"cell_id":11334,"v100":6.23,"k":2.14,"a":7.04,"adminlvl4_":8}},{"type":"Feature","id":"GEOCELLS-BELGIUM.73","geometry":{"type":"MultiPolygon","coordinates":[[[[4.872414477486676,50.355925348549036],[4.8541642311815325,50.53823650532439],[5.141080880568269,50.549530481034374],[5.158232711004421,50.367176125860944],[4.872414477486676,50.355925348549036]]]]},"geometry_name":"the_geom","properties":{"cell_id":11482,"v100":6.2,"k":2.14,"a":7,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.74","geometry":{"type":"MultiPolygon","coordinates":[[[[5.17525378267042,50.18481879157941],[5.158232711004421,50.367176125860944],[5.444182665908629,50.37772276448281],[5.4601123754595875,50.195326043662575],[5.17525378267042,50.18481879157941]]]]},"geometry_name":"the_geom","properties":{"cell_id":11629,"v100":6.31,"k":2.18,"a":7.12,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.75","geometry":{"type":"MultiPolygon","coordinates":[[[[5.158232711004421,50.367176125860944],[5.141080880568269,50.549530481034374],[5.428129759208383,50.560120325721826],[5.444182665908629,50.37772276448281],[5.158232711004421,50.367176125860944]]]]},"geometry_name":"the_geom","properties":{"cell_id":11630,"v100":6.1,"k":2.16,"a":6.89,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.76","geometry":{"type":"MultiPolygon","coordinates":[[[[5.4601123754595875,50.195326043662575],[5.444182665908629,50.37772276448281],[5.73025484375228,50.38757287913722],[5.745092207315905,50.20513676360954],[5.4601123754595875,50.195326043662575]]]]},"geometry_name":"the_geom","properties":{"cell_id":11777,"v100":6.35,"k":2.17,"a":7.15,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.77","geometry":{"type":"MultiPolygon","coordinates":[[[[5.444182665908629,50.37772276448281],[5.428129759208383,50.560120325721826],[5.715303294596349,50.5700060269191],[5.73025484375228,50.38757287913722],[5.444182665908629,50.37772276448281]]]]},"geometry_name":"the_geom","properties":{"cell_id":11778,"v100":6.06,"k":2.17,"a":6.84,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.78","geometry":{"type":"MultiPolygon","coordinates":[[[[5.759816372060405,50.022701491849034],[5.745092207315905,50.20513676360954],[6.030185714619861,50.21424712412474],[6.043824112109789,50.03177626921716],[5.759816372060405,50.022701491849034]]]]},"geometry_name":"the_geom","properties":{"cell_id":11924,"v100":6.28,"k":2.31,"a":7.08,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.79","geometry":{"type":"MultiPolygon","coordinates":[[[[5.745092207315905,50.20513676360954],[5.73025484375228,50.38757287913722],[6.016442168438094,50.39671882836348],[6.030185714619861,50.21424712412474],[5.745092207315905,50.20513676360954]]]]},"geometry_name":"the_geom","properties":{"cell_id":11925,"v100":6.4,"k":2.21,"a":7.21,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.80","geometry":{"type":"MultiPolygon","coordinates":[[[[5.73025484375228,50.38757287913722],[5.715303294596349,50.5700060269191],[6.002592486122423,50.57918757035642],[6.016442168438094,50.39671882836348],[5.73025484375228,50.38757287913722]]]]},"geometry_name":"the_geom","properties":{"cell_id":11926,"v100":6.3,"k":2.16,"a":7.09,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.81","geometry":{"type":"MultiPolygon","coordinates":[[[[6.043824112109789,50.03177626921716],[6.030185714619861,50.21424712412474],[6.31538389487124,50.22265711078107],[6.327936005323946,50.04015447988555],[6.043824112109789,50.03177626921716]]]]},"geometry_name":"the_geom","properties":{"cell_id":12072,"v100":6.09,"k":2.36,"a":6.88,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.82","geometry":{"type":"MultiPolygon","coordinates":[[[[6.030185714619861,50.21424712412474],[6.016442168438094,50.39671882836348],[6.3027351623424135,50.405160597179645],[6.31538389487124,50.22265711078107],[6.030185714619861,50.21424712412474]]]]},"geometry_name":"the_geom","properties":{"cell_id":12073,"v100":6.44,"k":2.34,"a":7.27,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.83","geometry":{"type":"MultiPolygon","coordinates":[[[[6.016442168438094,50.39671882836348],[6.002592486122423,50.57918757035642],[6.289988819624399,50.587661127440306],[6.3027351623424135,50.405160597179645],[6.016442168438094,50.39671882836348]]]]},"geometry_name":"the_geom","properties":{"cell_id":12074,"v100":6.66,"k":2.2,"a":7.5,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.84","geometry":{"type":"MultiPolygon","coordinates":[[[[6.002592486122423,50.57918757035642],[5.9886352039052735,50.76164953793316],[6.277143866940392,50.77015870462595],[6.289988819624399,50.587661127440306],[6.002592486122423,50.57918757035642]]]]},"geometry_name":"the_geom","properties":{"cell_id":12075,"v100":6.67,"k":2.09,"a":7.51,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.85","geometry":{"type":"MultiPolygon","coordinates":[[[[6.31538389487124,50.22265711078107],[6.3027351623424135,50.405160597179645],[6.589126239733829,50.41290198738175],[6.60067868580914,50.230370524796506],[6.31538389487124,50.22265711078107]]]]},"geometry_name":"the_geom","properties":{"cell_id":12221,"v100":6.42,"k":2.37,"a":7.25,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.86","geometry":{"type":"MultiPolygon","coordinates":[[[[6.3027351623424135,50.405160597179645],[6.289988819624399,50.587661127440306],[6.577484698874225,50.59543431471306],[6.589126239733829,50.41290198738175],[6.3027351623424135,50.405160597179645]]]]},"geometry_name":"the_geom","properties":{"cell_id":12222,"v100":6.71,"k":2.18,"a":7.55,"adminlvl4_":9}},{"type":"Feature","id":"GEOCELLS-BELGIUM.87","geometry":{"type":"MultiPolygon","coordinates":[[[[4.944034438362775,49.62666991391572],[4.926333480802072,49.80898158439645],[5.208907612045957,49.82010280191847],[5.225543301266981,49.63774795576482],[4.944034438362775,49.62666991391572]]]]},"geometry_name":"the_geom","properties":{"cell_id":11478,"v100":5.76,"k":2.35,"a":6.53,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.88","geometry":{"type":"MultiPolygon","coordinates":[[[[4.926333480802072,49.80898158439645],[4.908497155526494,49.9912978903246],[5.192144605092028,50.00246228902389],[5.208907612045957,49.82010280191847],[4.926333480802072,49.80898158439645]]]]},"geometry_name":"the_geom","properties":{"cell_id":11479,"v100":5.87,"k":2.36,"a":6.66,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.89","geometry":{"type":"MultiPolygon","coordinates":[[[[4.908497155526494,49.9912978903246],[4.890524965416519,50.17361120626065],[5.17525378267042,50.18481879157941],[5.192144605092028,50.00246228902389],[4.908497155526494,49.9912978903246]]]]},"geometry_name":"the_geom","properties":{"cell_id":11480,"v100":6.07,"k":2.24,"a":6.86,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.90","geometry":{"type":"MultiPolygon","coordinates":[[[[5.242054084359147,49.45540156355107],[5.225543301266981,49.63774795576482],[5.5071780089520495,49.648137083237856],[5.522630117036058,49.46574751252539],[5.242054084359147,49.45540156355107]]]]},"geometry_name":"the_geom","properties":{"cell_id":11625,"v100":5.5,"k":2.3,"a":6.23,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.91","geometry":{"type":"MultiPolygon","coordinates":[[[[5.225543301266981,49.63774795576482],[5.208907612045957,49.82010280191847],[5.491608580523109,49.83053129836173],[5.5071780089520495,49.648137083237856],[5.225543301266981,49.63774795576482]]]]},"geometry_name":"the_geom","properties":{"cell_id":11626,"v100":5.8,"k":2.36,"a":6.57,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.92","geometry":{"type":"MultiPolygon","coordinates":[[[[5.208907612045957,49.82010280191847],[5.192144605092028,50.00246228902389],[5.475920371483523,50.01292634588372],[5.491608580523109,49.83053129836173],[5.208907612045957,49.82010280191847]]]]},"geometry_name":"the_geom","properties":{"cell_id":11627,"v100":6.01,"k":2.38,"a":6.8,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.93","geometry":{"type":"MultiPolygon","coordinates":[[[[5.192144605092028,50.00246228902389],[5.17525378267042,50.18481879157941],[5.4601123754595875,50.195326043662575],[5.475920371483523,50.01292634588372],[5.192144605092028,50.00246228902389]]]]},"geometry_name":"the_geom","properties":{"cell_id":11628,"v100":6.2,"k":2.28,"a":7.01,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.94","geometry":{"type":"MultiPolygon","coordinates":[[[[5.522630117036058,49.46574751252539],[5.5071780089520495,49.648137083237856],[5.788930044196163,49.65783346813138],[5.803321998245664,49.475408339731814],[5.522630117036058,49.46574751252539]]]]},"geometry_name":"the_geom","properties":{"cell_id":11773,"v100":5.53,"k":2.3,"a":6.26,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.95","geometry":{"type":"MultiPolygon","coordinates":[[[[5.5071780089520495,49.648137083237856],[5.491608580523109,49.83053129836173],[5.774428335004634,49.840267060693],[5.788930044196163,49.65783346813138],[5.5071780089520495,49.648137083237856]]]]},"geometry_name":"the_geom","properties":{"cell_id":11774,"v100":5.8,"k":2.33,"a":6.56,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.96","geometry":{"type":"MultiPolygon","coordinates":[[[[5.491608580523109,49.83053129836173],[5.475920371483523,50.01292634588372],[5.759816372060405,50.022701491849034],[5.774428335004634,49.840267060693],[5.491608580523109,49.83053129836173]]]]},"geometry_name":"the_geom","properties":{"cell_id":11775,"v100":6.17,"k":2.32,"a":6.96,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.97","geometry":{"type":"MultiPolygon","coordinates":[[[[5.475920371483523,50.01292634588372],[5.4601123754595875,50.195326043662575],[5.745092207315905,50.20513676360954],[5.759816372060405,50.022701491849034],[5.475920371483523,50.01292634588372]]]]},"geometry_name":"the_geom","properties":{"cell_id":11776,"v100":6.35,"k":2.27,"a":7.16,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.98","geometry":{"type":"MultiPolygon","coordinates":[[[[5.803321998245664,49.475408339731814],[5.788930044196163,49.65783346813138],[6.070791344069181,49.66684091188406],[6.0841221613381515,49.48438021794568],[5.803321998245664,49.475408339731814]]]]},"geometry_name":"the_geom","properties":{"cell_id":11921,"v100":5.4,"k":2.25,"a":6.11,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.99","geometry":{"type":"MultiPolygon","coordinates":[[[[5.788930044196163,49.65783346813138],[5.774428335004634,49.840267060693],[6.057359310408956,49.84930626165391],[6.070791344069181,49.66684091188406],[5.788930044196163,49.65783346813138]]]]},"geometry_name":"the_geom","properties":{"cell_id":11922,"v100":5.5,"k":2.3,"a":6.21,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.100","geometry":{"type":"MultiPolygon","coordinates":[[[[5.774428335004634,49.840267060693],[5.759816372060405,50.022701491849034],[6.043824112109789,50.03177626921716],[6.057359310408956,49.84930626165391],[5.774428335004634,49.840267060693]]]]},"geometry_name":"the_geom","properties":{"cell_id":11923,"v100":5.9,"k":2.3,"a":6.66,"adminlvl4_":11}},{"type":"Feature","id":"GEOCELLS-BELGIUM.101","geometry":{"type":"MultiPolygon","coordinates":[[[[4.662658519972592,49.614902969487034],[4.643894227070258,49.79717147332022],[4.926333480802072,49.80898158439645],[4.944034438362775,49.62666991391572],[4.662658519972592,49.614902969487034]]]]},"geometry_name":"the_geom","properties":{"cell_id":11330,"v100":5.83,"k":2.32,"a":6.6,"adminlvl4_":12}},{"type":"Feature","id":"GEOCELLS-BELGIUM.102","geometry":{"type":"MultiPolygon","coordinates":[[[[4.643894227070258,49.79717147332022],[4.62498652739979,49.979440792530255],[4.908497155526494,49.9912978903246],[4.926333480802072,49.80898158439645],[4.643894227070258,49.79717147332022]]]]},"geometry_name":"the_geom","properties":{"cell_id":11331,"v100":5.92,"k":2.33,"a":6.72,"adminlvl4_":12}},{"type":"Feature","id":"GEOCELLS-BELGIUM.103","geometry":{"type":"MultiPolygon","coordinates":[[[[4.62498652739979,49.979440792530255],[4.605934427548672,50.16171093048364],[4.890524965416519,50.17361120626065],[4.908497155526494,49.9912978903246],[4.62498652739979,49.979440792530255]]]]},"geometry_name":"the_geom","properties":{"cell_id":11332,"v100":6.03,"k":2.25,"a":6.82,"adminlvl4_":12}},{"type":"Feature","id":"GEOCELLS-BELGIUM.104","geometry":{"type":"MultiPolygon","coordinates":[[[[4.890524965416519,50.17361120626065],[4.872414477486676,50.355925348549036],[5.158232711004421,50.367176125860944],[5.17525378267042,50.18481879157941],[4.890524965416519,50.17361120626065]]]]},"geometry_name":"the_geom","properties":{"cell_id":11481,"v100":6.15,"k":2.18,"a":6.94,"adminlvl4_":12}}],"crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:EPSG::4326"}}}'
    );
  }
  
  function getGeojsonByAdminUnit() {
    return JSON.parse(
      '{"type":"FeatureCollection","crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}},"features":[{"type":"Feature","properties":{"cell_id":11478,"v100":5.000000,"k":2.000000,"a":6.000000,"adminlvl4_":11},"geometry":{"type":"MultiPolygon","coordinates":[[[[4.944034438362775,49.62666991391572],[4.926333480802072,49.808981584396449],[4.908497155526494,49.991297890324603],[4.890524965416519,50.173611206260652],[5.17525378267042,50.18481879157941],[5.460112375459587,50.195326043662575],[5.745092207315905,50.205136763609538],[5.759816372060405,50.022701491849034],[6.043824112109789,50.031776269217161],[6.057359310408956,49.849306261653908],[6.070791344069181,49.666840911884059],[6.084122161338152,49.484380217945677],[5.803321998245664,49.475408339731814],[5.522630117036058,49.46574751252539],[5.242054084359147,49.455401563551071],[5.225543301266981,49.637747955764823],[4.944034438362775,49.62666991391572]]]]}},{"type":"Feature","properties":{"cell_id":11330,"v100":5.000000,"k":2.000000,"a":6.000000,"adminlvl4_":12},"geometry":{"type":"MultiPolygon","coordinates":[[[[4.662658519972592,49.614902969487034],[4.643894227070258,49.797171473320219],[4.62498652739979,49.979440792530255],[4.605934427548672,50.161710930483643],[4.890524965416519,50.173611206260652],[4.908497155526494,49.991297890324603],[4.926333480802072,49.808981584396449],[4.944034438362775,49.62666991391572],[4.662658519972592,49.614902969487034]]],[[[4.890524965416519,50.173611206260652],[4.872414477486676,50.355925348549036],[5.158232711004421,50.367176125860944],[5.17525378267042,50.18481879157941],[4.890524965416519,50.173611206260652]]]]}},{"type":"Feature","properties":{"cell_id":11040,"v100":6.000000,"k":2.000000,"a":6.000000,"adminlvl4_":1},"geometry":{"type":"MultiPolygon","coordinates":[[[[3.972596978482743,50.682304734076993],[3.950728568153774,50.864457467578184],[4.239406244775241,50.877961556039622],[4.218485786981648,51.060158297181204],[4.508445241523026,51.073001509699843],[4.528246075106862,50.890757757898442],[4.547893282178777,50.70850339296468],[4.2601650205565,50.695758011546765],[3.972596978482743,50.682304734076993]]]]}},{"type":"Feature","properties":{"cell_id":11484,"v100":6.000000,"k":2.000000,"a":7.000000,"adminlvl4_":3},"geometry":{"type":"MultiPolygon","coordinates":[[[[4.835773230467288,50.720544679971951],[4.817239062021159,50.902846059527427],[5.106376207891163,50.914226447134965],[5.395649477415977,50.924895093108582],[5.379219629538621,51.107272305234858],[5.362660720092644,51.289638924478368],[5.345971273041479,51.471994953612835],[5.638777981785141,51.482070117360919],[5.654322982421711,51.299678472291873],[5.946107259265034,51.309002454551717],[5.960393817991361,51.126560791891322],[5.974569786839182,50.944108549522426],[5.988635203905273,50.76164953793316],[6.002592486122423,50.579187570356417],[5.715303294596349,50.570006026919103],[5.428129759208383,50.560120325721826],[5.141080880568269,50.549530481034374],[5.123795866972859,50.731881858772233],[4.835773230467288,50.720544679971951]]]]}},{"type":"Feature","properties":{"cell_id":11041,"v100":5.000000,"k":2.000000,"a":6.000000,"adminlvl4_":2},"geometry":{"type":"MultiPolygon","coordinates":[[[[3.950728568153774,50.864457467578184],[3.928689480056917,51.046603391742785],[3.906478740678488,51.228734880654393],[4.197401245420235,51.242340607360092],[4.17615161232024,51.424512304932342],[4.154734473797748,51.606669577088184],[4.448106261267361,51.619665301077433],[4.741638982846728,51.631941719123787],[5.035323168379619,51.643498816940919],[5.32915029883929,51.65433658116946],[5.345971273041479,51.471994953612835],[5.362660720092644,51.289638924478368],[5.379219629538621,51.107272305234858],[5.395649477415977,50.924895093108582],[5.106376207891163,50.914226447134965],[4.817239062021159,50.902846059527427],[4.528246075106862,50.890757757898442],[4.508445241523026,51.073001509699843],[4.218485786981648,51.060158297181204],[4.239406244775241,50.877961556039622],[3.950728568153774,50.864457467578184]]]]}},{"type":"Feature","properties":{"cell_id":11039,"v100":6.000000,"k":2.000000,"a":7.000000,"adminlvl4_":5},"geometry":{"type":"MultiPolygon","coordinates":[[[[3.994297133405291,50.500145189233351],[3.972596978482743,50.682304734076993],[4.2601650205565,50.695758011546765],[4.547893282178777,50.70850339296468],[4.567389275702394,50.526242227819807],[4.280764061672069,50.513547661230064],[3.994297133405291,50.500145189233351]]],[[[4.547893282178777,50.70850339296468],[4.528246075106862,50.890757757898442],[4.817239062021159,50.902846059527427],[4.835773230467288,50.720544679971951],[4.547893282178777,50.70850339296468]]],[[[4.854164231181533,50.538236505324392],[4.835773230467288,50.720544679971951],[5.123795866972859,50.731881858772233],[5.141080880568269,50.549530481034374],[4.854164231181533,50.538236505324392]]]]}},{"type":"Feature","properties":{"cell_id":10744,"v100":6.000000,"k":2.000000,"a":6.000000,"adminlvl4_":4},"geometry":{"type":"MultiPolygon","coordinates":[[[[3.39797344385005,50.653293613844035],[3.373891833965619,50.835333309761538],[3.349622983888898,51.017366186146603],[3.32516473198389,51.199384615889336],[3.300514407817178,51.381392415681084],[3.592211301806947,51.396479906440334],[3.884093450903631,51.410851935762899],[4.17615161232024,51.424512304932342],[4.197401245420235,51.242340607360092],[3.906478740678488,51.228734880654393],[3.928689480056917,51.046603391742785],[3.950728568153774,50.864457467578184],[3.972596978482743,50.682304734076993],[3.685196704316028,50.668151201888342],[3.39797344385005,50.653293613844035]]]]}},{"type":"Feature","properties":{"cell_id":11335,"v100":6.000000,"k":2.000000,"a":7.000000,"adminlvl4_":7},"geometry":{"type":"MultiPolygon","coordinates":[[[[4.567389275702394,50.526242227819807],[4.547893282178777,50.70850339296468],[4.835773230467288,50.720544679971951],[4.854164231181533,50.538236505324392],[4.567389275702394,50.526242227819807]]]]}},{"type":"Feature","properties":{"cell_id":10300,"v100":6.000000,"k":2.000000,"a":7.000000,"adminlvl4_":6},"geometry":{"type":"MultiPolygon","coordinates":[[[[2.537447825675349,50.604508080839445],[2.510062973455171,50.786361126958667],[2.48246533750649,50.968203523191264],[2.454652975138453,51.150035272440576],[2.744617301611611,51.167195404855683],[2.717711633062595,51.349074916098218],[3.009011762173482,51.365589476583445],[3.300514407817178,51.381392415681084],[3.32516473198389,51.199384615889336],[3.349622983888898,51.017366186146603],[3.373891833965619,50.835333309761538],[3.39797344385005,50.653293613844035],[3.110935231394411,50.637735796771032],[2.824090608551017,50.621470133688689],[2.537447825675349,50.604508080839445]]]]}},{"type":"Feature","properties":{"cell_id":11482,"v100":6.000000,"k":2.000000,"a":7.000000,"adminlvl4_":9},"geometry":{"type":"MultiPolygon","coordinates":[[[[4.872414477486676,50.355925348549036],[4.854164231181533,50.538236505324392],[5.141080880568269,50.549530481034374],[5.428129759208383,50.560120325721826],[5.715303294596349,50.570006026919103],[6.002592486122423,50.579187570356417],[5.988635203905273,50.76164953793316],[6.277143866940392,50.770158704625949],[6.289988819624399,50.587661127440306],[6.577484698874225,50.59543431471306],[6.589126239733829,50.412901987381751],[6.60067868580914,50.230370524796506],[6.31538389487124,50.222657110781071],[6.327936005323946,50.040154479885551],[6.043824112109789,50.031776269217161],[5.759816372060405,50.022701491849034],[5.745092207315905,50.205136763609538],[5.460112375459587,50.195326043662575],[5.17525378267042,50.18481879157941],[5.158232711004421,50.367176125860944],[4.872414477486676,50.355925348549036]]]]}},{"type":"Feature","properties":{"cell_id":10595,"v100":5.000000,"k":2.000000,"a":6.000000,"adminlvl4_":8},"geometry":{"type":"MultiPolygon","coordinates":[[[[3.135926852402342,50.455743870738196],[3.110935231394411,50.637735796771032],[3.39797344385005,50.653293613844035],[3.685196704316028,50.668151201888342],[3.972596978482743,50.682304734076993],[3.994297133405291,50.500145189233351],[4.280764061672069,50.513547661230064],[4.567389275702394,50.526242227819807],[4.854164231181533,50.538236505324392],[4.872414477486676,50.355925348549036],[4.890524965416519,50.173611206260652],[4.605934427548672,50.161710930483643],[4.62498652739979,49.979440792530255],[4.643894227070258,49.797171473320219],[4.361597446318124,49.784664851625401],[4.079452119237695,49.771469362269968],[4.058406527193112,49.953640919519259],[4.03719996277493,50.135813284409259],[4.015830492289901,50.317982644708543],[3.730620761878501,50.30393451470654],[3.445583446075605,50.289189938822219],[3.421869996317393,50.471247095971954],[3.135926852402342,50.455743870738196]]]]}}]}'
    );
  }
  
  function updateGeojson(cellFeatures, adminUnitFeatures) {
    cellFeatures["features"].forEach(function(cell) {
      updateCellFeature(cell);
      // aggrate cell power by admin unit id
      adminUnitFeatures["features"].forEach(function(adminUnit) {
        updateAdminUnitFeature(cell, adminUnit);
      });
    });
  }
  
  /**
   * Update power and times to a single cell feature
   */
  function updateCellFeature(cell) {
    var times = createTimes(2016, 2040);
    cell["properties"]["times"] = times;
    cell["properties"]["power"] = createPower(times.length, 10, 1000.0);
  }
  
  /**
   * Update power and times to a single admin unit feature
   */
  function updateAdminUnitFeature(cell, adminUnit) {
    var adminUnitPower;
    var cellPower;
  
    // keep track the cell ids in admin unit
    if (!Array.isArray(adminUnit["properties"]["cell_id"])) {
      adminUnit["properties"]["cell_id"] = [];
    }
  
    // init an array attribute "times" if it not exists
    if (!adminUnit["properties"].hasOwnProperty("power")) {
      adminUnit["properties"]["times"] = cell["properties"]["times"];
    }
  
    // init a vectorize attribute "power" if it not exists
    if (!adminUnit["properties"].hasOwnProperty("power")) {
      adminUnitPower = Vector.Zero(cell["properties"]["power"].length);
      adminUnit["properties"]["power"] = adminUnitPower.elements;
    }
  
    if (
      adminUnit["properties"]["adminlvl4_"] === cell["properties"]["adminlvl4_"]
    ) {
      adminUnitPower = $V(adminUnit["properties"]["power"]).map(Number);
      cellPower = $V(cell["properties"]["power"]).map(Number);
      adminUnit["properties"]["power"] = adminUnitPower.add(cellPower).elements;
  
      adminUnit["properties"]["cell_id"].push(cell["properties"]["cell_id"]);
    }
  }
  
  function getClassification(cellFeatures, numOfClasses) {
    // remove data with 0 and concat them
    var arr = cellFeatures["features"].reduce(function(accumulator, current) {
      return accumulator.concat(
        current["properties"]["power"].filter(function(v) {
          return v !== 0;
        })
      );
    }, []);
  
    // var colors = chroma
    // .scale(chroma.brewer.YlOrRd)
    // .correctLightness()
    // .colors(numOfClasses, (format = "hex"))
    // .reverse();
    var colors;
    if (Math.min(...arr) < 0) {
      colors = chroma
        .scale(chroma.brewer.RdYlBu)
        .correctLightness()
        .colors();
    } else {
      colors = chroma
        .scale(chroma.brewer.YlOrRd)
        .correctLightness()
        .colors()
        .reverse();
    }
  
    var serie = new geostats(arr);
    serie.getJenks(colors.length);
  
    // for (let i = 0; i < serie.bounds.length; i++) {
    //   serie.bounds[i] = serie.bounds[i].toFixed(2);
    // }
    //serie.setRanges();
    // serie.doCount();
  
    var bounds = serie.bounds.reverse();
    var ranges = serie.ranges.reverse();
  
    return {
      bounds: bounds,
      ranges: ranges,
      colors: colors
    };
  }
  
  function getDynamicLegend(classfication) {
    var colors = classfication["colors"];
    var ranges = classfication["ranges"];
  
    var legends = colors.reduce(function(accumulator, currentVal, currentIdx) {
      // "<li><span style='background:#ff0000;'></span>0 - 1000</li>"
      return (
        accumulator +
        "<li><span style='background:" +
        currentVal +
        ";'></span>" +
        ranges[currentIdx] +
        "</li>"
      );
    }, "");
  
    var content =
      "" +
      "<div class='legend-title'>Power</div>" +
      "<div class='legend-scale'>" +
      "<ul class='legend-labels d-flex flex-column'>" +
      legends +
      "</ul>" +
      "</div>";
  
    return content;
  }
  /*
 * L.TimeDimension.Layer:  an abstract Layer that can be managed/synchronized with a TimeDimension.
 * The constructor recieves a layer (of any kind) and options.
 * Any children class should implement `_onNewTimeLoading`, `isReady` and `_update` functions
 * to react to time changes.
 */

L.TimeDimension.Layer = (L.Layer || L.Class).extend({

  includes: L.Mixin.Events,
  options: {
      opacity: 1,
      zIndex: 1
  },

  initialize: function(layer, options) {
      L.setOptions(this, options || {});
      this._map = null;
      this._baseLayer = layer;
      this._currentLayer = null;
      this._timeDimension = this.options.timeDimension || null;
  },

  addTo: function(map) {
      map.addLayer(this);
      return this;
  },

  onAdd: function(map) {
      this._map = map;
      if (!this._timeDimension && map.timeDimension) {
          this._timeDimension = map.timeDimension;
      }
      this._timeDimension.on("timeloading", this._onNewTimeLoading, this);
      this._timeDimension.on("timeload", this._update, this);
      this._timeDimension.registerSyncedLayer(this);
      this._update();
  },

  onRemove: function(map) {
      this._timeDimension.unregisterSyncedLayer(this);
      this._timeDimension.off("timeloading", this._onNewTimeLoading, this);
      this._timeDimension.off("timeload", this._update, this);
      this.eachLayer(map.removeLayer, map);
      this._map = null;
  },

  eachLayer: function(method, context) {
      method.call(context, this._baseLayer);
      return this;
  },

  setZIndex: function(zIndex) {
      this.options.zIndex = zIndex;
      if (this._baseLayer.setZIndex) {
          this._baseLayer.setZIndex(zIndex);
      }
      if (this._currentLayer && this._currentLayer.setZIndex) {
          this._currentLayer.setZIndex(zIndex);
      }
      return this;
  },

  setOpacity: function(opacity) {
      this.options.opacity = opacity;
      if (this._baseLayer.setOpacity) {
          this._baseLayer.setOpacity(opacity);
      }
      if (this._currentLayer && this._currentLayer.setOpacity) {
          this._currentLayer.setOpacity(opacity);
      }
      return this;
  },

  bringToBack: function() {
      if (!this._currentLayer) {
          return;
      }
      this._currentLayer.bringToBack();
      return this;
  },

  bringToFront: function() {
      if (!this._currentLayer) {
          return;
      }
      this._currentLayer.bringToFront();
      return this;
  },

  _onNewTimeLoading: function(ev) {
      // to be implemented for each type of layer
      this.fire('timeload', {
          time: ev.time
      });
      return;
  },

  isReady: function(time) {
      // to be implemented for each type of layer
      return true;
  },

  _update: function() {
      // to be implemented for each type of layer
      return true;
  },

  getBaseLayer: function() {
      return this._baseLayer;
  },

  getBounds: function() {
      var bounds = new L.LatLngBounds();
      if (this._currentLayer) {
          bounds.extend(this._currentLayer.getBounds ? this._currentLayer.getBounds() : this._currentLayer.getLatLng());
      }
      return bounds;
  }

});

L.timeDimension.layer = function(layer, options) {
  return new L.TimeDimension.Layer(layer, options);
};