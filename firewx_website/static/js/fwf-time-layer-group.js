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

    },

    eachLayer: function(method, context) {
        for (var prop in this._layers) {
            if (this._layers.hasOwnProperty(prop)) {
                method.call(context, this._layers[prop]);
            }
        }
        return L.TimeDimension.Layer.prototype.eachLayer.call(this, method, context);
    },


    _update: function() {
        if (!this._map)
            return;
        var time = map.timeDimension.getCurrentTime();
        var layer = this._getLayerForTime(time);
        if (this._currentLayer == null) {
            this._currentLayer = layer;
            // this._showLayer(layer, time);

        }
        if (!this._map.hasLayer(layer)) {
            this._map.addLayer(layer);
            this._showLayer(layer, time);

        } else {
            this._showLayer(layer, time);

        }
    },
    _showLayer: function(layer, time) {
        if (this._currentLayer && this._currentLayer !== layer) {
            this._currentLayer.hide();
            this._map.removeLayer(this._currentLayer);
        }
        layer.show();
        if (this._currentLayer && this._currentLayer === layer) {
            return;
        }
        this._currentLayer = layer;
        // Cache management
        var times = this._getLoadedTimes();
        var strTime = String(time);
        var index = times.indexOf(strTime);
        var remove = [];
        // remove times before current time
        if (this._timeCacheBackward > -1) {
            var objectsToRemove = index - this._timeCacheBackward;
            if (objectsToRemove > -1) {
                remove = times.splice(0, objectsToRemove);
                this._removeLayers(remove);
            }
        }
        if (this._timeCacheForward > -1) {
            index = times.indexOf(strTime);
            var objectsToRemove = times.length - index - this._timeCacheForward - 1;
            console.log(objectsToRemove);
            if (objectsToRemove > 0) {
                remove = times.splice(index + this._timeCacheForward + 1, objectsToRemove);
                this._removeLayers(remove);
            }
        }
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
        const varibale = this._thisVar;
        console.log(varibale);


            if (this._thisVar == 'FFMC'){
            fetch(url).then(function(response){
                return response.json();
            }).then(function(json){
                newLayer.addLayer(L.vectorGrid.slicer( json, {
                    minZoom: 2,
                    maxzoom: 10,
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles:{
                        'FFMC': geo_json_styler15
                            }
                        }
                    ).setZIndex(500)
                )
            })};

            if (this._thisVar == 'DMC'){
                fetch(url).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxzoom: 12,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'DMC': geo_json_styler15
                                }
                            }
                        ).setZIndex(500)
                    )
                })};

            
            if (this._thisVar == 'DC'){
                fetch(url).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxzoom: 12,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'DC': geo_json_styler15
                                }
                            }
                        ).setZIndex(500)
                    )
                })};

                
            if (this._thisVar == 'ISI'){
                fetch(url).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxzoom: 12,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'ISI': geo_json_styler15
                                }
                            }
                        ).setZIndex(500)
                    )
                })};

            
            if (this._thisVar == 'BUI'){
                fetch(url).then(function(response){
                    return response.json();
                }).then(function(json){
                    newLayer.addLayer(L.vectorGrid.slicer( json, {
                        minZoom: 2,
                        maxzoom: 12,
                        rendererFactory: L.canvas.tile,
                        vectorTileLayerStyles:{
                            'BUI': geo_json_styler15
                                }
                            }
                        ).setZIndex(500)
                    )
                })};
       

            
        if (this._thisVar == 'FWI'){
            fetch(url).then(function(response){
                return response.json();
            }).then(function(json){
                newLayer.addLayer(L.vectorGrid.slicer( json, {
                    minZoom: 2,
                    maxzoom: 10,
                    rendererFactory: L.canvas.tile,
                    vectorTileLayerStyles:{
                        'FWI': geo_json_styler15
                            }
                        }
                    ).setZIndex(500)
                )
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
            console.log(times[i]);
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
