function formatMapDate(date, endtime, starttime) {
    if(Date.parse(date) < Date.parse(endtime)){
    var d = new Date(date),
        hour = '' + d.getUTCHours(),
        day = '' + d.getUTCDate(),
        month = '' + (d.getUTCMonth() + 1),
        year = d.getUTCFullYear();
    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
    hour = 3.0*Math.floor(parseInt(hour)/3.0)
    hour = hour.toString()
    var UTCTimeMap = [year, month, day].join('-')
    UTCTimeMap = [UTCTimeMap,hour].join('T')
    UTCTimeMap = UTCTimeMap + ':00:00Z'
    }else{
    UTCTimeMap = starttime
    }
    return UTCTimeMap
}

function formatPlotDate(date, endtime, starttime) {
    if(Date.parse(date) < Date.parse(endtime)){
    var d = new Date(date),
        hour = '' + d.getUTCHours(),
        day = '' + d.getUTCDate(),
        month = '' + (d.getUTCMonth() + 1),
        year = d.getUTCFullYear();
    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
    var UTCTimePlot = [year, month, day].join('-')
    UTCTimePlot = [UTCTimePlot,hour].join('T')
    UTCTimePlot = UTCTimePlot + ':00:00Z'
    }else{
    UTCTimePlot = starttime
    }
    return UTCTimePlot
}



L.TimeDimension.Layer.LayerGroup = L.TimeDimension.Layer.extend({
    initialize: function(layer, options) {
        L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
        this._layers = {};
        this._defaultTime = 0;
        this._timeCacheBackward = this.options.cacheBackward || this.options.cache || 0;
        this._timeCacheForward = this.options.cacheForward || this.options.cache || 0;
        this._getUrlFunction = this.options.getUrlFunction;
        this._thisFileDir = this.options.getFileDir;
        this._thisVar    = this.options.getVar;
        this._thisStyler    = this.options.getStyler;


        this._baseLayer.on('load', (function() {
            this._baseLayer.setLoaded(true);
            this.fire('timeload', {
                time: this._defaultTime
            });
        }).bind(this));

    },

    eachLayer: function(method, context) {
        for (var prop in this._layers) {
            if (this._layers.hasOwnProperty(prop)) {
                method.call(context, this._layers[prop]);
            }
        }
        return L.TimeDimension.Layer.prototype.eachLayer.call(this, method, context);
    },

        _onNewTimeLoading: function(ev) {
        var layer = this._getLayerForTime(ev.time);
        if (!this._map.hasLayer(layer)) {
            this._map.addLayer(layer);
        }
    },

    isReady: function(time) {
        var layer = this._getLayerForTime(time);
        var currentZoom = this._map.getZoom();
        if (layer.options.minZoom && currentZoom < layer.options.minZoom){
            return true;
        }
        if (layer.options.maxZoom && currentZoom > layer.options.maxZoom){
            return true;
        }
        return;
    },

    _update: function() {
        if (!this._map)
            return;
        var time = map.timeDimension.getCurrentTime();
        var layer = this._getLayerForTime(time);
        if (this._currentLayer == null) {
            this._currentLayer = layer;
            this._showLayer(layer, time);

        }
        if (!this._map.hasLayer(layer)) {
            this._map.addLayer(layer);
            this._showLayer(layer, time);

        } else {
            this._showLayer(layer, time);

        }
    },

    _unvalidateCache: function() {
        var time = this._timeDimension.getCurrentTime();
        for (var prop in this._layers) {
            if (time != prop && this._layers.hasOwnProperty(prop)) {
                this._layers[prop].setLoaded(false); // mark it as unloaded
                this._layers[prop].redraw();
            }
        }
    },

    _evictCachedTimes: function(keepforward, keepbackward) {
        // Cache management
        var times = this._getLoadedTimes();
        var strTime = String(this._currentTime);
        var index = times.indexOf(strTime);
        var remove = [];
        // remove times before current time
        if (keepbackward > -1) {
            var objectsToRemove = index - keepbackward;
            if (objectsToRemove > 0) {
                remove = times.splice(0, objectsToRemove);
                this._removeLayers(remove);
            }
        }
        if (keepforward > -1) {
            index = times.indexOf(strTime);
            var objectsToRemove = times.length - index - keepforward - 1;
            if (objectsToRemove > 0) {
                remove = times.splice(index + keepforward + 1, objectsToRemove);
                this._removeLayers(remove);
            }
        }
    },

    
    _showLayer: function(layer, time) {
        if (this._currentLayer && this._currentLayer !== layer) {
            this._currentLayer.hide();
        }
        layer.show();
        if (this._currentLayer && this._currentLayer === layer) {
            return;
        }
        this._currentLayer = layer;
        this._currentTime = time;
        console.log('Show layer with time: ' + new Date(time).toISOString());
        UTCTimeMap = new Date(time).toISOString();
        UTCTimeMap = UTCTimeMap.slice(0,19)
        console.log(UTCTimeMap);
        makeplotly(file_list.slice(-1)[0], point_list.slice(-1)[0], UTCTimeMap);
        this._evictCachedTimes(this._timeCacheForward, this._timeCacheBackward);
    },


    _getLayerForTime: function(time) {
        if (time == 0 || time == this._defaultTime) {
            return this._baseLayer;
        }
        if (this._layers.hasOwnProperty(time)) {
            return this._layers[time];
        }

        var url = this._getUrlFunction(this._thisFileDir, time);
        console.log(url);

        var newLayer = L.layerGroup();
        var varibale = this._thisVar;
        console.log(varibale);


            if (this._thisVar == 'FFMC'){
            fetch(url, {cache: "default"}).then(function(response){
                return response.json();
            }).then(function(json){
                newLayer.addLayer(L.vectorGrid.slicer( json, {
                    minZoom: 2,
                    maxZoom: 18,
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles:{
                        'FFMC': geo_json_styler18
                            }
                        }
                    ).setZIndex(500)
                )
            })};

            if (this._thisVar == 'DMC'){
                fetch(url, {cache: "default"}).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxZoom: 18,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'DMC': geo_json_styler18
                                }
                            }
                        ).setZIndex(500)
                    )
                })};

            
            if (this._thisVar == 'DC'){
                fetch(url, {cache: "default"}).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxZoom: 18,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'DC': geo_json_styler18
                                }
                            }
                        ).setZIndex(500)
                    )
                })};

                
            if (this._thisVar == 'ISI'){
                fetch(url, {cache: "default"}).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxZoom: 18,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'ISI': geo_json_styler18
                                }
                            }
                        ).setZIndex(500)
                    )
                })};

            
            if (this._thisVar == 'BUI'){
                fetch(url, {cache: "default"}).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxZoom: 18,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'BUI': geo_json_styler18
                                }
                            }
                        ).setZIndex(500)
                    )
                })};
       

            
        if (this._thisVar == 'FWI'){
            fetch(url, {cache: "default"}).then(function(response){
                return response.json();
            }).then(function(json){
                newLayer.addLayer(L.vectorGrid.slicer( json, {
                    minZoom: 2,
                    maxZoom: 18,
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles:{
                        'FWI': geo_json_styler18
                            }
                        }
                    ).setZIndex(500)
                )
            })};

        if (this._thisVar == 'wsp'){
            fetch(url, {cache: "default"}).then(function(response){
                return response.json();
            }).then(function(json){
                newLayer.addLayer(L.vectorGrid.slicer( json, {
                    minZoom: 2,
                    maxZoom: 18,
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles:{
                        'wsp': geo_json_styler_wsp
                            }
                        }
                    ).setZIndex(500)
                )
            })};

        if (this._thisVar == 'temp'){
            fetch(url, {cache: "default"}).then(function(response){
                return response.json();
            }).then(function(json){
                newLayer.addLayer(L.vectorGrid.slicer( json, {
                    minZoom: 2,
                    maxZoom: 18,
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles:{
                        'temp': geo_json_styler_temp
                            }
                        }
                    ).setZIndex(500)
                )
            })};

        if (this._thisVar == 'rh'){
            fetch(url, {cache: "default"}).then(function(response){
                return response.json();
            }).then(function(json){
                newLayer.addLayer(L.vectorGrid.slicer( json, {
                    minZoom: 2,
                    maxZoom: 18,
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles:{
                        'rh': geo_json_styler_rh
                            }
                        }
                    ).setZIndex(500)
                )
            })};

            if (this._thisVar == 'qpf'){
                fetch(url, {cache: "default"}).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxZoom: 18,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'qpf': geo_json_styler_qpf
                                }
                            }
                        ).setZIndex(500)
                    )
                })};
            if (this._thisVar == 'qpf_3h'){
                fetch(url, {cache: "default"}).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxZoom: 18,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'qpf': geo_json_styler_qpf
                                }
                            }
                        ).setZIndex(500));
                })};

            if (this._thisVar == 'snw'){
                fetch(url, {cache: "default"}).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxZoom: 18,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'snw': geo_json_styler_snw
                                }
                            }
                        ).setZIndex(500));
                })};

        
        this._layers[time] = newLayer;

        return newLayer;

    },

    _getLoadedTimes: function() {
        var result = [];
        for (var prop in this._layers) {
            if (this._layers.hasOwnProperty(prop)) {
                result.push(prop);
            }
        }
        return result.sort();
    },

    _removeLayers: function(times) {
        for (var i = 0, l = times.length; i < l; i++) {
            this._map.removeLayer(this._layers[times[i]]);
            // console.log(times[i]);
            delete this._layers[times[i]];
        }
    },

});


L.timeDimension.layer.layerGroup = function(layer, options) {
    return new L.TimeDimension.Layer.LayerGroup(layer, options);
};

L.LayerGroup.include({
    _visible: true,
    _loaded: false,

    _originalUpdate: L.LayerGroup.prototype._update,

    _update: function() {
        if (!this._visible && this._loaded) {
            return;
        }
        this._originalUpdate();
    },

    // setLoaded: function(loaded) {
    //     this._loaded = loaded;
    // },

    // isLoaded: function() {
    //     return this._loaded;
    // },

    hide: function() {
        this._visible = false;
        if (this._image && this._image.style)
            this._image.style.display = 'none';
    },

    show: function() {
        this._visible = true;
        if (this._image && this._image.style)
            this._image.style.display = 'block';
    },

    getURL: function() {
        return this._url;
    },

});

pad2 = function (n) {
    return n < 10 ? '0' + n : n;
};

dateFileName = function (time) {
    YYYYMMDD = time.getUTCFullYear().toString();
    YYYYMMDD += pad2(time.getUTCMonth() + 1).toString();
    YYYYMMDD += pad2(time.getUTCDate()).toString();
    return YYYYMMDD;
};

dateTimeFileName = function (time) {
    YYYYMMDDhhmm = time.getUTCFullYear().toString();
    YYYYMMDDhhmm += pad2(time.getUTCMonth() + 1).toString();
    YYYYMMDDhhmm += pad2(time.getUTCDate()).toString();
    YYYYMMDDhhmm += pad2(time.getUTCHours()).toString();
    // YYYYMMDDhhmm += pad2(time.getUTCMinutes()).toString();
    return YYYYMMDDhhmm;
};

getHourlyForecast = function(baseUrl, time) {
    var beginUrl = baseUrl.substring(0, baseUrl.lastIndexOf("/"));
    var initFileUrl = baseUrl.substring(baseUrl.lastIndexOf("/"), baseUrl.length - 16);
    var strTime = dateTimeFileName(new Date(time));
    url = beginUrl + initFileUrl + '-' + strTime + '.json';
    console.log(url);
    return url;
};

getDailyForecast = function(baseUrl, time) {
    var beginUrl = baseUrl.substring(0, baseUrl.lastIndexOf("/"));
    var initFileUrl = baseUrl.substring(baseUrl.lastIndexOf("/"), baseUrl.length - 14);
    var strTime = dateFileName(new Date(time));
    url = beginUrl + initFileUrl + '-' + strTime + '.json';
    return url;
};
