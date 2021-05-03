function formatMapDate(e, t, r) {
    if (Date.parse(e) < Date.parse(t)) {
        var i = new Date(e),
            n = "" + i.getUTCHours(),
            a = "" + i.getUTCDate(),
            o = "" + (i.getUTCMonth() + 1),
            s = i.getUTCFullYear();
        o.length < 2 && (o = "0" + o), a.length < 2 && (a = "0" + a), (n = (n = 3 * Math.floor(parseInt(n) / 3)).toString()).length < 2 && (n = "0" + n);
        var h = [s, o, a].join("-");
        (h = [h, n].join("T")), (h += ":00:00Z");
    } else h = r;
    return h;
}
function formatPlotDate(e, t, r) {
    if (Date.parse(e) < Date.parse(t)) {
        var i = new Date(e),
            n = "" + i.getUTCHours(),
            a = "" + i.getUTCDate(),
            o = "" + (i.getUTCMonth() + 1),
            s = i.getUTCFullYear();
        o.length < 2 && (o = "0" + o), a.length < 2 && (a = "0" + a), n.length < 2 && (n = "0" + n);
        var h = [s, o, a].join("-");
        (h = [h, n].join("T")), (h += ":00:00Z");
    } else h = r;
    return h;
}
(L.TimeDimension.Layer.LayerGroup = L.TimeDimension.Layer.extend({
    initialize: function (e, t) {
        L.TimeDimension.Layer.prototype.initialize.call(this, e, t),
            (this._layers = {}),
            (this._defaultTime = 0),
            (this._timeCacheBackward = this.options.cacheBackward || this.options.cache || 0),
            (this._timeCacheForward = this.options.cacheForward || this.options.cache || 0),
            (this._getUrlFunction = this.options.getUrlFunction),
            (this._thisFileDir = this.options.getFileDir),
            (this._thisVar = this.options.getVar),
            (this._thisStyler = this.options.getStyler),
            this._baseLayer.on(
                "load",
                function () {
                    this._baseLayer.setLoaded(!0), this.fire("timeload", { time: this._defaultTime });
                }.bind(this)
            );
    },
    eachLayer: function (e, t) {
        for (var r in this._layers) this._layers.hasOwnProperty(r) && e.call(t, this._layers[r]);
        return L.TimeDimension.Layer.prototype.eachLayer.call(this, e, t);
    },
    _onNewTimeLoading: function (e) {
        var t = this._getLayerForTime(e.time);
        this._map.hasLayer(t) || this._map.addLayer(t);
    },
    isReady: function (e) {
        var t = this._getLayerForTime(e),
            r = this._map.getZoom();
        return !!(t.options.minZoom && r < t.options.minZoom) || !!(t.options.maxZoom && r > t.options.maxZoom) || void 0;
    },
    _update: function () {
        if (this._map) {
            var e = map.timeDimension.getCurrentTime(),
                t = this._getLayerForTime(e);
            null == this._currentLayer && ((this._currentLayer = t), this._showLayer(t, e)), this._map.hasLayer(t) ? this._showLayer(t, e) : (this._map.addLayer(t), this._showLayer(t, e));
        }
    },
    _unvalidateCache: function () {
        var e = this._timeDimension.getCurrentTime();
        for (var t in this._layers) e != t && this._layers.hasOwnProperty(t) && (this._layers[t].setLoaded(!1), this._layers[t].redraw());
    },
    _evictCachedTimes: function (e, t) {
        var r,
            i = this._getLoadedTimes(),
            n = String(this._currentTime),
            a = i.indexOf(n),
            o = [];
        t > -1 && (r = a - t) > 0 && ((o = i.splice(0, r)), this._removeLayers(o));
        e > -1 && ((a = i.indexOf(n)), (r = i.length - a - e - 1) > 0 && ((o = i.splice(a + e + 1, r)), this._removeLayers(o)));
    },
    _showLayer: function (e, t) {
        this._currentLayer && this._currentLayer !== e && this._currentLayer.hide(),
            e.show(),
            (this._currentLayer && this._currentLayer === e) ||
                ((this._currentLayer = e),
                (this._currentTime = t),
                console.log("Show layer with time: " + new Date(t).toISOString()),
                (UTCTimeMap = new Date(t).toISOString()),
                (UTCTimeMap = UTCTimeMap.slice(0, 19)),
                console.log(UTCTimeMap),
                this._evictCachedTimes(this._timeCacheForward, this._timeCacheBackward));
    },
    _getLayerForTime: function (e) {
        if (0 == e || e == this._defaultTime) return this._baseLayer;
        if (this._layers.hasOwnProperty(e)) return this._layers[e];
        var t = this._getUrlFunction(this._thisFileDir, e),
            r = L.layerGroup(),
            i = this._thisVar;
        return (
            console.log(i),
            "FFMC" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { FFMC: geo_json_styler18 } }).setZIndex(500));
                    }),
            "DMC" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { DMC: geo_json_styler18 } }).setZIndex(500));
                    }),
            "DC" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { DC: geo_json_styler18 } }).setZIndex(500));
                    }),
            "ISI" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { ISI: geo_json_styler18 } }).setZIndex(500));
                    }),
            "BUI" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { BUI: geo_json_styler18 } }).setZIndex(500));
                    }),
            "FWI" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { FWI: geo_json_styler18 } }).setZIndex(500));
                    }),
            "wsp" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { wsp: geo_json_styler_wsp } }).setZIndex(500));
                    }),
            "temp" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { temp: geo_json_styler_temp } }).setZIndex(500));
                    }),
            "rh" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { rh: geo_json_styler_rh } }).setZIndex(500));
                    }),
            "qpf" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { qpf: geo_json_styler_qpf } }).setZIndex(500));
                    }),
            "qpf_3h" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { qpf: geo_json_styler_qpf } }).setZIndex(500));
                    }),
            "snw" == this._thisVar &&
                fetch(t, { cache: "default" })
                    .then(function (e) {
                        return e.json();
                    })
                    .then(function (e) {
                        r.addLayer(L.vectorGrid.slicer(e, { minZoom: 2, maxZoom: 18, rendererFactory: L.canvas.tile, vectorTileLayerStyles: { snw: geo_json_styler_snw } }).setZIndex(500));
                    }),
            (this._layers[e] = r),
            r
        );
    },
    _getLoadedTimes: function () {
        var e = [];
        for (var t in this._layers) this._layers.hasOwnProperty(t) && e.push(t);
        return e.sort();
    },
    _removeLayers: function (e) {
        for (var t = 0, r = e.length; t < r; t++) this._map.removeLayer(this._layers[e[t]]), delete this._layers[e[t]];
    },
})),
    (L.timeDimension.layer.layerGroup = function (e, t) {
        return new L.TimeDimension.Layer.LayerGroup(e, t);
    }),
    L.LayerGroup.include({
        _visible: !0,
        _loaded: !1,
        _originalUpdate: L.LayerGroup.prototype._update,
        _update: function () {
            (!this._visible && this._loaded) || this._originalUpdate();
        },
        hide: function () {
            (this._visible = !1), this._image && this._image.style && (this._image.style.display = "none");
        },
        show: function () {
            (this._visible = !0), this._image && this._image.style && (this._image.style.display = "block");
        },
        getURL: function () {
            return this._url;
        },
    }),
    (pad2 = function (e) {
        return e < 10 ? "0" + e : e;
    }),
    (dateFileName = function (e) {
        return (YYYYMMDD = e.getUTCFullYear().toString()), (YYYYMMDD += pad2(e.getUTCMonth() + 1).toString()), (YYYYMMDD += pad2(e.getUTCDate()).toString()), YYYYMMDD;
    }),
    (dateTimeFileName = function (e) {
        return (YYYYMMDDhhmm = e.getUTCFullYear().toString()), (YYYYMMDDhhmm += pad2(e.getUTCMonth() + 1).toString()), (YYYYMMDDhhmm += pad2(e.getUTCDate()).toString()), (YYYYMMDDhhmm += pad2(e.getUTCHours()).toString()), YYYYMMDDhhmm;
    }),
    (getHourlyForecast = function (e, t) {
        var r = e.substring(0, e.lastIndexOf("/")),
            i = e.substring(e.lastIndexOf("/"), e.length - 16),
            n = dateTimeFileName(new Date(t));
        return (url = r + i + "-" + n + ".json"), console.log(url), url;
    }),
    (getDailyForecast = function (e, t) {
        var r = e.substring(0, e.lastIndexOf("/")),
            i = e.substring(e.lastIndexOf("/"), e.length - 14),
            n = dateFileName(new Date(t));
        return (url = r + i + "-" + n + ".json"), url;
    });
