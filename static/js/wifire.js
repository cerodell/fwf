var WebView = function (e, t, i) {
    var a = e || location.hostname,
        r = t || location.port,
        n = a + (r ? ":" + r : "");
    (this._wsurl = (i ? "wss://" : "ws://") + n + "/kepler/ws-runwf"), (this._url = (i ? "https://" : "http://") + n), (this._reqid = 0), (this._reqHandlers = {}), (this._toSend = []);
};
(WebView.prototype = {
    close: function () {
        this._ws && (this._ws.close(), (this._ws = null));
    },
    getRun: function (e) {
        return new WebView.Run(this, e);
    },
    getUrl: function () {
        return this._url;
    },
    login: function () {
        var e = this;
        return this._makeRequest("login").done(function (t) {
            e.loginInfo = t;
        });
    },
    logout: function () {
        return this._makeRequest("logout");
    },
    run: function (e) {
        var t,
            i = JSON.parse(JSON.stringify(e));
        if (e.app_name && e.wf_name) this._error("Cannot run workflow and app in same request.");
        else {
            if (e.app_name || e.wf_name)
                return (
                    (i.reqid = this._reqid++),
                    delete i.reqType,
                    i.hasOwnProperty("prov") || (i.prov = !1),
                    i.hasOwnProperty("sync") || (i.sync = !0),
                    e.reqType && "POST" === e.reqType
                        ? e.wf_name
                            ? (t = this._makeRequest({ path: "kepler/runwf", type: "POST", args: i }))
                            : e.app_name && (t = this._makeRequest({ path: "app", type: "POST", args: i }))
                        : (this._ws || this._connect(), (t = new WebView.Handler()), this._ws && this._opened ? this._send(i, t) : this._toSend.push({ req: i, h: t })),
                    t
                );
            this._error("Must specify either app_name or wf_name");
        }
    },
    setPassword: function (e) {
        this._password = e;
    },
    setUsername: function (e) {
        this._username = e;
    },
    _connect: function () {
        if (window.WebSocket)
            if (this._wsurl) {
                this._ws = new WebSocket(this._wsurl);
                var e = this;
                (this._ws.onopen = function () {
                    for (e._opened = !0; e._toSend.length > 0; ) {
                        var t = e._toSend.shift();
                        e._send(t.req, t.h);
                    }
                }),
                    (this._ws.error = function (t) {
                        e.error(t);
                    }),
                    (this._ws.onmessage = function (t) {
                        e._recv(JSON.parse(t.data));
                    });
            } else this._error("URL not specified.");
        else this._error("Websocket not supported.");
        return this;
    },
    _error: function (e) {
        console.log("error " + e);
        var t = this._reqHandlers[e.reqid];
        delete this._reqHandlers[e.reqid], t._handleAlways(), t._handleFail(e);
    },
    _makeRequest: function (e) {
        var t,
            i,
            a,
            r,
            n = new XMLHttpRequest(),
            s = new WebView.Handler();
        return (
            "string" == typeof e ? (t = e) : ((t = e.path), (i = e.type), (a = e.args), (r = e.binary)),
            i || (i = "GET"),
            (n.onreadystatechange = function () {
                var e;
                4 === n.readyState &&
                    (200 === n.status
                        ? (s._handleAlways(), (e = r ? n.response : n.responseText ? JSON.parse(n.responseText) : null), s._handleDone(e))
                        : 0 !== n.status &&
                          200 !== n.status &&
                          (s._handleAlways(),
                          0 == n.responseText.indexOf("{") ? ((e = n.responseText ? JSON.parse(n.responseText) : null) && e.error ? s._handleFail(e.error) : s._handleFail(null)) : s._handleFail(n.responseText || n.statusText)));
            }),
            n.open(i, this._url + "/" + t, !0),
            (n.onerror = function () {
                s._handleAlways(), s._handleFail("Network error contacting server.");
            }),
            (n.withCredentials = !0),
            r && (n.responseType = "blob"),
            n.setRequestHeader("Authorization", "WebView " + btoa(this._username + ":" + this._password)),
            n.send(JSON.stringify(a)),
            s
        );
    },
    _recv: function (e) {
        var t = this._reqHandlers[e.reqid];
        delete this._reqHandlers[e.reqid], t._handleAlways(), e.error ? t._handleFail(e.error) : e.responses ? t._handleDone(e.responses) : t._handleDone(e);
    },
    _send: function (e, t) {
        (this._reqHandlers[e.reqid] = t), this._ws.send(JSON.stringify(e));
    },
}),
    (WebView.Handler = function () {
        (this._alwaysHandlers = []), (this._doneHandlers = []), (this._failHandlers = []);
    }),
    (WebView.Handler.prototype = {
        always: function (e) {
            return this._alwaysHandlers.push(e), this;
        },
        done: function (e) {
            return this._doneHandlers.push(e), this;
        },
        fail: function (e) {
            return this._failHandlers.push(e), this;
        },
        _callHandlers: function (e, t) {
            var i;
            for (i in e) e[i](t);
        },
        _handleAlways: function (e) {
            this._callHandlers(this._alwaysHandlers, e);
        },
        _handleDone: function (e) {
            this._callHandlers(this._doneHandlers, e);
        },
        _handleFail: function (e) {
            this._failHandlers.length > 0 ? this._callHandlers(this._failHandlers, e) : console.error("Unhandled error: " + e);
        },
    }),
    (WebView.Run = function (e, t) {
        (this._webview = e), (this._id = t);
    }),
    (WebView.Run.prototype = {
        id: function () {
            return this._id;
        },
        ro_bundle: function (e) {
            var t = e || "ro_bundle.zip",
                i = new WebView.Handler();
            return (
                this._makeRequest({ path: "roBundle", binary: !0 })
                    .always(function (e) {
                        i._handleAlways();
                    })
                    .fail(function (e) {
                        console.log("failed to get ro bundle: " + e), i._handleFail(e);
                    })
                    .done(function (e) {
                        download(e, t, "application/zip"), i._handleDone();
                    }),
                i
            );
        },
        _makeRequest: function (e) {
            return (e.path = "kepler/runs/" + this._id + "/" + e.path), this._webview._makeRequest(e);
        },
    }),
    (LoadJS = function () {
        this._done = {};
    }),
    (LoadJS.prototype = {
        load: function (e, t) {
            var i = this;
            e.constructor === Array
                ? this._loadFile(e[0], function () {
                      i._next(1, e, t);
                  })
                : this._loadFile(e, t);
        },
        _next: function (e, t, i) {
            var a = this;
            e == t.length - 1
                ? this._loadFile(t[e], i)
                : this._loadFile(t[e], function () {
                      a._next(e + 1, t, i);
                  });
        },
        _loadFile: function (e, t) {
            var i,
                a = this;
            this._done[e]
                ? t()
                : ((i = document.createElement("script")).setAttribute("src", e),
                  i.setAttribute("type", "text/javascript"),
                  (i.onload = function () {
                      (a._done[e] = !0), t();
                  }),
                  document.getElementsByTagName("head")[0].appendChild(i));
        },
    }),
    (function () {
        "use strict";
        (L.MapState = L.Class.extend({
            initialize: function (e, t) {
                var i = t || {},
                    a = this.load("mz") || i.zoom,
                    r = this.load("mcla") || i.lat,
                    n = this.load("mclo") || i.lng,
                    s = this;
                (this._map = e),
                    (this._layerControl = i.layerControl),
                    (this._ignoreLayer = null),
                    void 0 !== a && e.setZoom(a),
                    void 0 !== r && void 0 !== n && e.setView(L.latLng(r, n)),
                    e
                        .on("zoomend", function (t) {
                            s.save("mz", e.getZoom());
                        })
                        .on("moveend", function (t) {
                            var i = e.getCenter();
                            s.save("mcla", i.lat), s.save("mclo", i.lng);
                        })
                        .on("baselayerchange", function (e) {
                            s.save("mbl", e.name);
                        })
                        .on("overlayadd", function (e) {
                            (s._ignoreLayer && s._ignoreLayer(e)) || s.save("mol", e.name, { append: !0 });
                        })
                        .on("overlayremove", function (e) {
                            (s._ignoreLayer && s._ignoreLayer(e)) || s.save("mol", e.name, { remove: !0 });
                        });
            },
            getIgnoreLayer: function () {
                return this._ignoreLayer;
            },
            ignoreLayer: function (e) {
                return (this._ignoreLayer = e), this;
            },
            load: function (e) {
                return localStorage.getItem(e);
            },
            loadLayers: function (e) {
                var t = this.load("mbl") || e;
                this._addLayers(t), this._addLayers(this.load("mol"));
            },
            save: function (e, t, i) {
                var a, r, n;
                if (i) {
                    if (i.append)
                        if (null == (a = localStorage.getItem(e))) localStorage.setItem(e, t);
                        else {
                            for (n in (r = a.split(","))) if (r[n] == t) return;
                            localStorage.setItem(e, a + "," + t);
                        }
                    else if (i.remove && null != (a = localStorage.getItem(e))) {
                        for (n in (r = a.split(",")))
                            if (r[n] == t) {
                                r.splice(n, 1);
                                break;
                            }
                        0 == r.length ? localStorage.removeItem(e) : localStorage.setItem(e, r.toString());
                    }
                } else localStorage.setItem(e, t);
            },
            _addLayers: function (e) {
                var t, i, a;
                if (e && this._layerControl)
                    for (i in (t = e.split(",")))
                        for (a in this._layerControl._layers)
                            if (t[i] == this._layerControl._layers[a].name) {
                                this._map.addLayer(this._layerControl._layers[a].layer);
                                break;
                            }
            },
        })),
            (L.mapState = function (e, t) {
                return new L.MapState(e, t);
            }),
            "function" == typeof define && define.amd && define(L.MapState);
    })(),
    (L.CanvasOverlay = L.Class.extend({
        initialize: function (e, t) {
            (this._userDrawFunc = e), L.setOptions(this, t);
        },
        drawing: function (e) {
            return (this._userDrawFunc = e), this;
        },
        params: function (e) {
            return L.setOptions(this, e), this;
        },
        canvas: function () {
            return this._canvas;
        },
        redraw: function () {
            return this._frame || (this._frame = L.Util.requestAnimFrame(this._redraw, this)), this;
        },
        setOpacity: function (e) {
            return (this._canvas.getContext("2d").globalAlpha = e), this.redraw(), this;
        },
        onAdd: function (e) {
            (this._map = e), (this._canvas = L.DomUtil.create("canvas")), (this._canvas.id = L.stamp(this)), this.options.zIndex && (this._canvas.style.zIndex = this.options.zIndex);
            var t = this._map.getSize();
            (this._canvas.width = t.x), (this._canvas.height = t.y);
            var i = this._map.options.zoomAnimation && L.Browser.any3d;
            L.DomUtil.addClass(this._canvas, "leaflet-zoom-" + (i ? "animated" : "hide")),
                e._panes.overlayPane.appendChild(this._canvas),
                e.on("moveend", this._reset, this),
                e.on("resize", this._resize, this),
                e.options.zoomAnimation && L.Browser.any3d && e.on("zoomanim", this._animateZoom, this),
                this._reset();
        },
        onRemove: function (e) {
            e.getPanes().overlayPane.removeChild(this._canvas), e.off("moveend", this._reset, this), e.off("resize", this._resize, this), e.options.zoomAnimation && e.off("zoomanim", this._animateZoom, this), (this._canvas = null);
        },
        addTo: function (e) {
            return e.addLayer(this), this;
        },
        _resize: function (e) {
            (this._canvas.width = e.newSize.x), (this._canvas.height = e.newSize.y);
        },
        _reset: function () {
            var e = this._map.containerPointToLayerPoint([0, 0]);
            L.DomUtil.setPosition(this._canvas, e), this._redraw();
        },
        _redraw: function () {
            var e = this._map.getSize(),
                t = this._map.getBounds(),
                i = (180 * e.x) / (20037508.34 * (t.getEast() - t.getWest())),
                a = this._map.getZoom();
            this._userDrawFunc && this._userDrawFunc(this, { canvas: this._canvas, bounds: t, size: e, zoomScale: i, zoom: a, options: this.options }), (this._frame = null);
        },
        _animateZoom: function (e) {
            var t = this._map.getZoomScale(e.zoom),
                i = this._map._getCenterOffset(e.center)._multiplyBy(-t).subtract(this._map._getMapPanePos());
            this._canvas.style[L.DomUtil.TRANSFORM] = L.DomUtil.getTranslateString(i) + " scale(" + t + ")";
        },
    })),
    (L.canvasOverlay = function (e, t) {
        return new L.CanvasOverlay(e, t);
    }),
    (L.Control.Layers.TreeOpacity = L.Control.Layers.extend({
        addNestedOverlay: function (e, t, i) {
            var a,
                r = !1;
            if (!i) return this.addOverlay(e, t);
            for (a in this._layers) this._layers[a].name === i && (this._layers[a].children.push(this._addLayer(e, t, !0, !0)), (r = !0));
            if (!r) {
                var n = {};
                (n[t] = e), this._addLayer(n, i, !0);
            }
            return this._update(), this;
        },
        _addLayer: function (e, t, i, a) {
            var r,
                n,
                s = L.stamp(e);
            if (((this._layers[s] = { layer: e, name: t, overlay: i, children: [], child: a }), this.options.autoZIndex && e.setZIndex && (this._lastZIndex++, e.setZIndex(this._lastZIndex)), "function" != typeof e.onAdd))
                for (n in e) "_leaflet_id" !== n && ((r = this._addLayer(e[n], n, i, !0)), this._layers[s].children.push(r));
            return s;
        },
        _update: function () {
            if (this._container) {
                (this._baseLayersList.innerHTML = ""), (this._overlaysList.innerHTML = "");
                var e,
                    t,
                    i = !1,
                    a = !1;
                for (e in this._layers) {
                    for (j in ((t = this._layers[e]), (children = t.children.slice()), (t.children = []), children)) this._layers[children[j]] && t.children.push(children[j]);
                    t.child || this._addItem(t), (a = a || t.overlay), (i = i || !t.overlay);
                }
                this._separator.style.display = a && i ? "" : "none";
            }
        },
        _addItem: function (e) {
            var t, i, a, r;
            if (e.layer.onAdd || 0 != e.children.length) {
                (t = document.createElement("label")),
                    (a = this._map.hasLayer(e.layer)),
                    e.overlay
                        ? (((i = document.createElement("input")).type = "checkbox"),
                          (i.id = i.name = e.name),
                          e.children.length > 0 ? (i.className = "leaflet-control-layers-selector-parent") : (i.className = "leaflet-control-layers-selector"),
                          (i.defaultChecked = a),
                          this.options.opacity &&
                              e.layer.setOpacity &&
                              (((r = document.createElement("input")).type = "range"),
                              (r.min = 0),
                              (r.max = 1),
                              (r.step = 0.01),
                              e.layer.getOpacity ? (r.value = e.layer.getOpacity()) : (r.value = 1),
                              (r.oninput = r.onchange = function (t) {
                                  e.layer.setOpacity(this.value);
                              })))
                        : (i = this._createRadioElement("leaflet-base-layers", a)),
                    (i.layerId = L.stamp(e.layer)),
                    L.DomEvent.on(i, "click", this._onInputClick, this);
                var n = document.createElement("span");
                if (((n.innerHTML = " " + e.name), t.appendChild(i), e.overlay && e.children.length > 0)) {
                    var s = document.createElement("label");
                    (s.htmlFor = e.name), t.appendChild(s), (!L.Browser.ie && L.Browser.webkit) || ((s.style["background-position"] = "1px"), (s.style.padding = "0 5 0 0px"));
                }
                return t.appendChild(n), r && t.appendChild(r), (e.overlay ? this._overlaysList : this._baseLayersList).appendChild(t), t;
            }
        },
        _onInputClick: function () {
            var e,
                t,
                i,
                a = this._form.getElementsByTagName("input"),
                r = a.length;
            for (this._handlingClick = !0, e = 0; e < r; e++)
                if ((t = a[e]) && "range" != t.type)
                    if ((i = this._layers[t.layerId]).children.length > 0) {
                        var n,
                            s = t.parentNode.childNodes;
                        if (t.checked) {
                            var o = !1;
                            for (n in s)
                                if ("UL" === s[n].nodeName) {
                                    o = !0;
                                    break;
                                }
                            if (!o) {
                                var l = document.createElement("ul");
                                for (n in ((l.className = "leaflet-control-ul"), t.parentNode.appendChild(l), i.children)) {
                                    var d = this._layers[i.children[n]];
                                    if ("_leaflet_id" !== d.name) {
                                        var m = document.createElement("li"),
                                            c = this._addItem(d);
                                        m.appendChild(c), l.appendChild(m);
                                    }
                                }
                            }
                        } else
                            for (n in s)
                                if ("UL" === s[n].nodeName) {
                                    t.parentNode.removeChild(s[n]);
                                    break;
                                }
                    } else t.checked && !this._map.hasLayer(i.layer) ? this._map.addLayer(i.layer) : !t.checked && this._map.hasLayer(i.layer) && this._map.removeLayer(i.layer);
            (this._handlingClick = !1), this._refocusOnMap();
        },
    })),
    (L.control.layers.treeopacity = function (e, t, i) {
        return new L.Control.Layers.TreeOpacity(e, t, i);
    });
var Constants = {
        twoPI: 2 * Math.PI,
        MPS_TO_MPH: 2.236936,
        KM_TO_MI: 0.621371,
        MI_TO_FT: 5820,
        M_TO_FT: 3.28084,
        SQM_TO_ACRES: 24711e-8,
        sixtyMeterDiffLatLng: 3e-4,
        defaultFuel: "LANDFIRE FBFM13 30m 2014",
        urls: { pylaski: "https://firemap.sdsc.edu/pylaski/", ws: "wss://" + location.hostname + "/alerts", wms: "https://firemap.sdsc.edu/geoserver/wms", wfs: "https://firemap.sdsc.edu/geoserver/wfs" },
        webview: { host: null, port: 443 },
        wxChartColors: { airTemp: "olive", fuelTemp: "brown", humidity: "#009900", fuelMoisture: "#0000FF", windSpeed: "purple", windGust: "fuchsia", windDirection: "#B87333" },
        tz: moment.tz.guess(),
        chartOptions: { alignTicks: !1, spacingBottom: 1, spacingTop: 5, spacingLeft: 1, spacingRight: 10, marginTop: 30 },
        chartHeight: { big: 175, small: 20 },
        chartWidth: { max: 500 },
        chartXTickInterval: 18e5,
        zLayers: {
            forecast: -19,
            cameraPTZView: -18,
            animSat: -17,
            wxStation: -16,
            airQStation: -15,
            cameraStation: -14,
            realTimeWxStation: -13,
            fireLegend: -12,
            surfaceFuel: 1,
            vegetationType: 2,
            canopyCover: 3,
            census: 4,
            viewsheds: 5,
            roads: 17,
            histFire: 7,
            modisFire: 8,
            viirsFire: 9,
            smokePt: 10,
            redFlag: 15,
            activeFires: 16,
        },
        retina: !0,
        overlayConfig: {
            camOverlay: { position: "centerbottom" },
            fireInfoOverlay: { position: "centertop" },
            ensembleInfoOverlay: { position: "centerbottom" },
            setupPerimeterEnsembleOverlay: { position: "centertop" },
            fireWeather: { position: { top: 75, left: 50 } },
            fireAreaOverlay: { position: { top: 604, left: 50 } },
            historicalFiresControl: { position: "leftbottom" },
            aqTypeControl: { position: "leftbottom" },
            fuelLegend: { position: "leftbottom" },
            satelliteLegend: { position: "leftbottom" },
            wxHazWarnLegend: { position: "leftbottom" },
            wxTypeControl: { position: "leftbottom" },
            wxForecastTypeControl: { position: "leftbottom" },
            wxChartControl: { position: "righttop" },
            aqChartControl: { position: "righttop" },
            wxErrorZoomIn: { position: "leftbottom" },
            animControl: { position: "rightbottom" },
            goesGeoColor: { position: "leftcenter" },
            gibsControl: { position: "leftcenter" },
            cameraConfigOverlay: { position: "leftbottom" },
            importsFilterControl: { position: "leftbottom" },
            alertsOverlay: { position: "leftcenter" },
            forecastChartControl: { position: "righttop" },
        },
        closeButton: { backgroundColor: "#3498DB", color: "white", hover: { backgroundColor: "red" } },
        cameraButton: { backgroundColor: "#FF00FF", color: "white", hover: { backgroundColor: "green" } },
    },
    CanvasUtils = function () {
        (this.wxStationRadius = 12),
            (this.wxArrowLen = 55),
            (this.arrowOffset = 90 * L.LatLng.DEG_TO_RAD),
            (this._colormaps = { temperature: new ColorMap(0, 120, colormap({ colormap: "rainbow", nshades: 30, format: "hex" })), wind_speed: new ColorMap(0, 80, colormap({ colormap: "plasma", nshades: 15, format: "hex" })) });
    };
CanvasUtils.prototype = {
    clearCanvas: function (e) {
        e.canvas.getContext("2d").clearRect(0, 0, e.canvas.width, e.canvas.height);
    },
    drawStation: function (e) {
        var t = e.scale || 1;
        e.ctx.beginPath(), e.ctx.arc(e.center.x, e.center.y, this.wxStationRadius / t, 0, Constants.twoPI), (e.ctx.lineWidth = e.width || 2), e.scale && (e.ctx.lineWidth = e.ctx.lineWidth / t), e.ctx.stroke();
    },
    drawCloud: function (e) {
        var t = e.center.x,
            i = e.center.y,
            a = e.scale || 1;
        e.ctx.beginPath(),
            (e.ctx.strokeStyle = "black"),
            (e.ctx.lineWidth = e.width || 2),
            (e.ctx.fillStyle = "#ffffff"),
            e.ctx.moveTo(t - 2 / a, i),
            e.ctx.bezierCurveTo(t - 9.926 / a, i - 1.2 / a, t - 7.563 / a, i - 11.298 / a, t + 9.891 / a, i - 9.575 / a),
            e.ctx.bezierCurveTo(t + 10.768 / a, i - 12.933 / a, t + 21.761 / a, i - 12.388 / a, t + 21.689 / a, i - 9.575 / a),
            e.ctx.bezierCurveTo(t + 28.582 / a, i - 13.173 / a, t + 37.39 / a, i - 5.998 / a, t + 31.482 / a, i - 2.399 / a),
            e.ctx.bezierCurveTo(t + 38.572 / a, i - 0.654 / a, t + 31.393 / a, i + 8.746 / a, t + 25.574 / a, i + 7.175 / a),
            e.ctx.bezierCurveTo(t + 25.108 / a, i + 9.793 / a, t + 14.706 / a, i + 10.709 / a, t + 13.793 / a, i + 7.175 / a),
            e.ctx.bezierCurveTo(t + 7.903 / a, i + 10.949 / a, t - 12.737 / a, i + 5.147 / a, t - 2 / a, i),
            e.ctx.closePath(),
            e.ctx.fill(),
            e.ctx.stroke();
    },
    airQualityColor: function (e, t) {
        var i = Math.abs(255 - (255 * e) / 100);
        return { bg: "hsl(" + i + ",100%,50%)", fg: i < 200 ? "black" : "white" };
    },
    temperatureColor: function (e) {
        return { bg: this._colormaps.temperature.get(e), fg: "black" };
    },
    humidityColor: function (e) {
        return { bg: e <= 20 ? "hsl(35,100%," + (20 + 2 * e) + "%)" : "hsl(235,100%," + (100 - e / 2) + "%)", fg: "white" };
    },
    windSpeedColor: function (e) {
        return { bg: this._colormaps.wind_speed.get(e + 8), fg: e < 50 ? "#fff" : "#000" };
    },
    drawValue: function (e) {
        var t = e.ctx;
        if (null !== e.v) {
            var i;
            (t.fillStyle = e.color.bg), t.fill(), (t.font = "12px Arial"), (t.fillStyle = e.color.fg);
            var a = Math.round(e.v);
            (i = a >= 100 || a < 0 ? e.center.x - 10 : a >= 10 ? e.center.x - 7 : e.center.x - 3), e.scale || t.fillText(a, i, e.center.y + 5);
        } else (t.fillStyle = "white"), t.fill();
    },
    drawFloatValue: function (e) {
        var t,
            i = e.ctx;
        null !== e.v
            ? ((v = e.v.toString()),
              v.length > 5 && (v = e.v.toFixed(3).toString()),
              (i.fillStyle = e.color.bg),
              i.fill(),
              (i.font = "12px Arial"),
              (i.fillStyle = e.color.fg),
              (t = e.center.x),
              4 == v.length ? (t += 3) : 3 == v.length ? (t += 5) : 2 == v.length ? (t += 7) : 1 == v.length && (t += 9),
              i.fillText(v, t, e.center.y + 3))
            : ((i.fillStyle = e.color.bg), i.fill());
    },
    drawWindArrow: function (e) {
        var t = e.ctx,
            i = e.scale || 1;
        e.erase ? ((t.globalCompositeOperation = "destination-out"), (t.lineWidth = 3)) : ((t.globalCompositeOperation = "source-over"), (t.lineWidth = 2)), (t.strokeStyle = t.fillStyle = "black");
        var a = this.wxArrowLen / i;
        e.erase && a++, (e.dir = e.dir - 270);
        var r = e.center.x + Math.cos(e.dir * L.LatLng.DEG_TO_RAD) * a,
            n = e.center.y + Math.sin(e.dir * L.LatLng.DEG_TO_RAD) * a;
        t.beginPath(), t.moveTo(e.center.x, e.center.y), t.lineTo(r, n), t.stroke();
        var s = e.dir * L.LatLng.DEG_TO_RAD + this.arrowOffset;
        t.save(), t.beginPath(), t.translate(r, n), t.rotate(s), t.moveTo(0, 0), e.erase ? (t.lineTo(6, 12), t.lineTo(-6, 12)) : (t.lineTo(5, 10), t.lineTo(-5, 10)), t.closePath(), t.restore(), t.fill();
    },
    drawWindBarb: function (e) {
        var t = e.ctx;
        e.erase ? ((t.globalCompositeOperation = "destination-out"), (t.lineWidth = 3)) : ((t.globalCompositeOperation = "source-over"), (t.lineWidth = 2)), (t.strokeStyle = t.fillStyle = "black");
        var i = this.wxArrowLen;
        e.erase && i++, (e.dir = e.dir - 90);
        var a = e.center.x + Math.cos(e.dir * L.LatLng.DEG_TO_RAD) * i,
            r = e.center.y + Math.sin(e.dir * L.LatLng.DEG_TO_RAD) * i;
        t.beginPath(), t.moveTo(e.center.x, e.center.y), t.lineTo(a, r), t.stroke();
        var n = e.dir * L.LatLng.DEG_TO_RAD + this.arrowOffset;
        t.save(), t.beginPath(), t.translate(a, r), t.rotate(n), t.moveTo(0, 0), e.erase ? t.lineTo(6, 9) : t.lineTo(5, 8), t.stroke(), t.restore(), t.fill();
    },
};
var Utils = function () {};
Utils.prototype = {
    adjustIconsInButtons: function () {
        var e, t;
        if ((L.Browser.gecko || L.Browser.retina) && -1 == navigator.userAgent.indexOf("Android"))
            for (e = document.getElementsByClassName("easyButtonLg"), t = 0; t < e.length; t++)
                "MacIntel" === navigator.platform || (!L.Browser.retina && 0 !== navigator.platform.indexOf("Win") && 0 !== navigator.platform.indexOf("Linux")) ? (e[t].style.left = "-1.5px") : (e[t].style.left = "-3px"),
                    (e[t].style.position = "relative");
    },
    getClosestStation: function (e, t, i, a, r, n) {
        var s,
            o = [];
        if (e) {
            for (s in e.features)
                if (!r || r.call(n, e.features[s]))
                    if (e.features[s].geometry.centerPoint) {
                        if (t.containerPoint.distanceTo(e.features[s].geometry.centerPoint) < i) {
                            if (!a) return e.features[s];
                            o.push(s);
                        }
                    } else console.log("no centerPoint for: " + e.features[s].properties.description.name);
            return o;
        }
    },
    initChart: function (e) {
        var t = document.getElementById(e);
        return (t.innerHTML = ""), (t.style.width = window.innerWidth < Constants.chartWidth.max ? window.innerWidth : Constants.chartWidth.max), t;
    },
    showChart: function (e, t) {
        var i,
            a,
            r = [],
            n = [],
            s = !0;
        for (i in (t.singleYAxis && r.push({ title: null, labels: { format: "{value}" + e[0].units } }), t.hasOwnProperty("legend") && (s = t.legend), e)) {
            t.singleYAxis
                ? (void 0 !== e[i].max && (void 0 !== r[0].max ? (r[0].max = Math.max(r[0].max, e[i].max)) : (r[0].max = e[i].max)),
                  void 0 !== e[i].yTickInterval && (void 0 !== r[0].tickInterval ? (r[0].tickInterval = Math.min(r[0].tickInterval, e[i].yTickInterval)) : (r[0].tickInterval = e[i].yTickInterval)),
                  void 0 !== e[i].xTickInterval && (a = void 0 !== a ? Math.min(a, e[i].xTickInterval) : e[i].xTickInterval))
                : (r.push({ title: { text: e[i].title }, labels: { format: "{value}" + e[i].units }, opposite: 1 == i }),
                  void 0 !== e[i].max && (r[i].max = e[i].max),
                  void 0 !== e[i].yTickInterval && (r[i].tickInterval = e[i].yTickInterval),
                  void 0 !== e[i].xTickInterval && (a = e[i].xTickInterval));
            let s = { name: e[i].title, data: e[i].values, tooltip: { valueSuffix: " " + e[i].units }, color: e[i].color };
            e[i].legendItemClick && (s.events = { legendItemClick: e[i].legendItemClick }), n.push(s), t.singleYAxis || 1 != i || (n[i].yAxis = 1);
        }
        $("#" + t.id).highcharts({
            title: { text: t.title },
            chart: Constants.chartOptions,
            xAxis: { type: "datetime", tickInterval: a, gridLineWidth: 1 },
            yAxis: r,
            series: n,
            credits: { enabled: !1 },
            tooltip: { valueDecimals: 0 },
            legend: { enabled: s },
        });
    },
    getChartHeight: function (e, t, i, a) {
        var r = (window.innerHeight - document.getElementById(e).scrollHeight - a - (i - t) * Constants.chartHeight.small) / t;
        return r < Constants.chartHeight.big ? r : Constants.chartHeight.big;
    },
    createSlider: function (e) {
        var t,
            i = document.getElementById(e.id);
        t = !e.formatMap && ("number" != typeof e.start || "lower");
        var a = {
                to: function (t) {
                    return e.formatMap ? e.formatMap[Math.round(t)] : Number(t.toFixed(e.precision || 0));
                },
                from: function (e) {
                    return e.replace(",-", "");
                },
            },
            r = { start: e.start, step: e.step, range: e.range || { min: e.min, max: e.max }, connect: t, format: a };
        if (
            (e.formatMap
                ? (r.pips = {
                      mode: "steps",
                      format: a,
                      density: 100,
                      filter: function (e) {
                          return 1;
                      },
                  })
                : e.nopips || (r.pips = { mode: "range", density: 10 }),
            noUiSlider.create(i, r),
            e.textId)
        ) {
            i.noUiSlider.on("update", function (t, i) {
                var a,
                    r,
                    n = document.getElementById(e.textId[i]);
                if (e.textFormatMap) {
                    for (a in e.formatMap) if (e.formatMap[a] === t[i]) break;
                    r = e.textFormatMap[a];
                } else r = t[i];
                "DIV" === n.nodeName ? (n.innerHTML = r) : "INPUT" === n.nodeName && (n.value = r);
            });
            var n = document.getElementById(e.textId[0]);
            "INPUT" === n.nodeName &&
                ((n.max = e.max),
                (n.min = e.min),
                (n.step = e.step),
                (n.value = e.start),
                (n.onchange = function () {
                    i.noUiSlider.set(this.value);
                }));
        }
        return (
            e.onset &&
                i.noUiSlider.on("set", function (t, i) {
                    e.onset(t[i]);
                }),
            e.onupdate &&
                i.noUiSlider.on("update", function (t, i) {
                    e.onupdate(t[i]);
                }),
            i
        );
    },
    updateStatus: function (e, t) {
        var i = document.getElementById(e);
        "SPAN" === i.nodeName ? (i.textContent = t) : (i.innerHTML = t);
    },
    addToSelect: function (e, t, i) {
        var a = document.createElement("option");
        void 0 !== i ? ((a.text = t), (a.value = i)) : (a.text = a.value = t), e.add(a);
    },
    setVisibilityTimer: function (e, t, i, a) {
        let r = function () {
            if (document.hidden) window.clearTimeout(e.timer);
            else {
                let r = moment().diff(e.lastQueryTime, "seconds");
                r >= t
                    ? i.call(a)
                    : (window.clearTimeout(e.timer),
                      (e.timer = window.setTimeout(
                          function () {
                              i.call(a);
                          }.bind(a),
                          1e3 * (t - r)
                      )));
            }
        };
        return document.addEventListener("visibilitychange", r), r;
    },
    removeVisibilityTimer: function (e) {
        document.removeEventListener("visibilitychange", e);
    },
};
var _cameraStationsSingletonLayer,
    ColorMap = function (e, t, i) {
        (this._width = t - e), (this._min = e), (this._colors = i);
    };
(ColorMap.prototype = {
    get: function (e) {
        var t = Math.round(((e - this._min) / this._width) * this._colors.length);
        return this._colors[Math.max(0, Math.min(this._colors.length - 1, t))];
    },
}),
    (_CameraStations = function (e) {
        var t = this;
        (this._canvasUtils = new CanvasUtils()),
            (this._utils = new Utils()),
            (this._stations = null),
            (this._map = null),
            (this._minWxCircleDist = -1),
            (this._ajaxCameras = null),
            (this._overlay = e.overlay),
            (this._minStationZoom = 10),
            (this._numCamerasToShowWithView = 4),
            (this._enableAdvanced = !1),
            $(".ptzAdvanced").css("display", "none"),
            (this._openOverlays = {}),
            (this._openCameraIds = {}),
            (this._showingAllInView = !1);
        let i = JSON.parse(JSON.stringify(e));
        (e._context = this),
            (e.zIndex = Constants.zLayers.cameraStation),
            (this._layer = L.canvasOverlay(this._drawCanvasCameras, e)),
            (i._context = this),
            (i.zIndex = Constants.zLayers.cameraPTZView),
            (this._viewLayer = L.canvasOverlay(this._drawCanvasPTZViews, i)),
            (this._camUrls = {}),
            (this._cameraOffsets = { "Axis-Black": [1.066794831694608, -1.519389069789745], "Axis-NOAA": [-0.6597698340076192, -0.7920813979878558] }),
            (this._colors = { "coming soon": "#BBB477", sleeping: "#676767", ptz: "#FF00FF", fixed: "#D7837F" }),
            (document.getElementById("showPTZView").onchange = function () {
                (t._showPTZView = this.checked), t._showPTZView ? t._viewLayer.onAdd(t._map) : t._viewLayer.onRemove(t._map);
            }),
            (this._showPTZView = document.getElementById("showPTZView").checked),
            (document.getElementById("showPTZTarget").onchange = function () {
                (t._showPTZTarget = this.checked), t._layer.redraw();
            }),
            (this._showPTZTarget = document.getElementById("showPTZTarget").checked),
            (document.getElementById("ptzViewLocationButton").onclick = function () {
                t._showAllOnClickChanged();
            }),
            (this._queryFrequency = 60),
            (this._updateTimer = { timer: null, lastQueryTime: null }),
            (document.getElementById("ptzResetButton").onclick = function () {
                t._viewLocationMarker && (t._map.removeLayer(t._viewLocationMarker), (t._viewLocationMarker = null)), t._closeAllOverlays(), t.redraw();
            }),
            (this._imageLoadCache = 0),
            (this._reloadTime = { ptz: 32e3, fixed: 3e5 }),
            (this._viewLocationIcon = L.AwesomeMarkers.icon({ markerColor: "purple", icon: "bullseye", prefix: "fa" }));
    }),
    (_CameraStations.prototype = {
        setAdvanced: function (e) {
            (this._enableAdvanced = e), $(".ptzAdvanced").css("display", e ? "initial" : "none");
        },
        _showAllOnClickChanged: function () {
            if (((this._showAllPTZOnClick = !this._showAllPTZOnClick), this._map)) {
                let e = document.getElementById("ptzViewLocationButton").classList;
                this._showAllPTZOnClick
                    ? (this._map.on("click", this._clickShowAllPTZ, this),
                      L.DomUtil.addClass(this._map._container, "crosshair-cursor-enabled"),
                      e.add("selFireButton"),
                      this._viewLocationMarker && (this._map.removeLayer(this._viewLocationMarker), (this._viewLocationMarker = null)))
                    : (this._map.off("click", this._clickShowAllPTZ, this), L.DomUtil.removeClass(this._map._container, "crosshair-cursor-enabled"), e.remove("selFireButton"));
            }
        },
        _clickShowAllPTZ: function (e) {
            this.showCamerasViewingLatLng(e.latlng);
        },
        showCamerasViewingLatLng: function (e, t) {
            let i,
                a,
                r,
                n,
                s = this;
            if (!this._map) return t ? ((this._showCamerasAfterLoadLatLng = e), void t.addLayer(firemap.cameras)) : void console.log("error: unable to add camera layer to map");
            if (!this._enableAdvanced) return;
            (this._showAllPTZOnClick = !0),
                document.getElementById("ptzViewLocationButton").onclick(),
                this._closeAllOverlays(),
                L.DomUtil.removeClass(this._map._container, "crosshair-cursor-enabled"),
                (a = turf.helpers.point([e.lng, e.lat]));
            let o = [];
            for (i in this._stations.features)
                (n = this._stations.features[i].properties.description).ptz &&
                    !n._sleeping &&
                    ((r = turf.helpers.polygon([[n.fov_lft, n.fov_center, n.fov_rt, this._stations.features[i].geometry.coordinates, n.fov_lft]])), turf.booleanPointInPolygon.default(a, r) && o.push(i));
            for (
                o.sort(function (t, i) {
                    return (
                        L.latLng([s._stations.features[t].geometry.coordinates[1], s._stations.features[t].geometry.coordinates[0]]).distanceTo(e) -
                        L.latLng([s._stations.features[i].geometry.coordinates[1], s._stations.features[i].geometry.coordinates[0]]).distanceTo(e)
                    );
                }),
                    this._showingAllInView = !0,
                    i = 0;
                i < Math.min(this._numCamerasToShowWithView, o.length);
                i++
            )
                this._showSelectedCamera(o[i], !0);
            this._viewLocationMarker = L.marker(e, { icon: this._viewLocationIcon }).addTo(this._map);
        },
        onAdd: function (e) {
            (this._map = e),
                this._layer.onAdd(e),
                e.on("click", this._clickCameraStation, this),
                L.DomEvent.addListener(window, "storage", this._clickInCameraImage, this),
                window.setTimeout(
                    function () {
                        this._updateCameraCanvas(!0);
                    }.bind(this),
                    0
                ),
                this._showPTZView && this._viewLayer.onAdd(this._map),
                (this._visibilityFunction = this._utils.setVisibilityTimer(this._updateTimer, this._queryFrequency, this._updateCameraCanvas, this));
        },
        onRemove: function (e) {
            this._utils.removeVisibilityTimer(this._visibilityFunction),
                (this._visibilityFunction = null),
                this._updateTimer.timer && (clearTimeout(this._updateTimer.timer), (this._updateTimer.timer = null)),
                this._showPTZView && this._viewLayer.onRemove(this._map),
                this._ajaxCameras && (this._ajaxCameras.abort(), (this._ajaxCameras = null)),
                this._viewLocationMarker && (this._map.removeLayer(this._viewLocationMarker), (this._viewLocationMarker = null)),
                this._closeAllOverlays(),
                L.DomEvent.removeListener(window, "storage", this._clickInCameraImage),
                e.off("click", this._clickCameraStation, this),
                this._layer.onRemove(e),
                (this._map = null);
        },
        onUpdate: function (e, t) {
            t.hasOwnProperty("ptz") && (t.ptz ? (this._showPTZ = !0) : (this._showPTZ = !1)),
                t.hasOwnProperty("fixed") && (t.fixed ? (this._showFixed = !0) : (this._showFixed = !1)),
                null == this._map && (this._showPTZ || this._showFixed) ? this.onAdd(e) : null == this._map || this._showPTZ || this._showFixed ? this._layer && this.redraw() : this.onRemove(e);
        },
        redraw: function (e) {
            this._layer && this._layer.redraw(), !this._showPTZView || (void 0 !== e && !0 !== e) || this._viewLayer.redraw();
        },
        setCameraClickListener: function (e) {
            this._cameraClickListener = e;
        },
        _closeAllOverlays: function () {
            for (let e in this._openOverlays) this._closeThumbnail(e);
            this._showingAllInView = !1;
        },
        _clickInCameraImage: function (e) {
            var t,
                i,
                a,
                r,
                n,
                s,
                o,
                l,
                d = this,
                m = [];
            if (this._cameraClickListener && "camimg-click" === e.key)
                if (((t = JSON.parse(localStorage.getItem("camimg-click"))), this._camUrls[t[0].src]))
                    for (i in t)
                        (a = (t[i].x - Math.round(t[i].w / 2)) / t[i].factor),
                            (r = (-t[i].y + t[i].h - Math.round(t[i].h / 2)) / t[i].factor),
                            (n = t[i].w / 2 / t[i].factor / Math.tan((0.5 * this._camUrls[t[i].src].fov * Math.PI) / 180)),
                            (s = Math.atan(a / n)),
                            (o = Math.atan(r / n)),
                            (l = this._cameraOffsets[this._camUrls[t[i].src].id] ? this._cameraOffsets[this._camUrls[t[i].src].id] : [0, 0]),
                            $.ajax({
                                url:
                                    Constants.urls.pylaski +
                                    "app/geocam?lat=" +
                                    this._camUrls[t[i].src].lat +
                                    "&lon=" +
                                    this._camUrls[t[i].src].lon +
                                    "&elev=" +
                                    this._camUrls[t[i].src].elev +
                                    "&heading=" +
                                    (l[1] + this._camUrls[t[i].src].az_current + (180 * s) / Math.PI) +
                                    "&pitch=" +
                                    (l[0] + this._camUrls[t[i].src].tilt_current + (180 * o) / Math.PI),
                            })
                                .fail(function (e, t) {
                                    alert("Error getting coordinates: " + t);
                                })
                                .done(function (e) {
                                    if (e.lon && (m.push({ i: parseInt(e.id), latlng: [e.lat, e.lon] }), m.length == t.length))
                                        if (1 == m.length) d._cameraClickListener(L.marker(m[0].latlng));
                                        else {
                                            for (j in (m.sort(function (e, t) {
                                                return e.i - t.i;
                                            }),
                                            m))
                                                m[j] = m[j].latlng;
                                            d._cameraClickListener(L.polygon(m));
                                        }
                                });
                else console.error("no coordinates found for " + t[0].src);
        },
        _clickCameraStation: function (e) {
            var t,
                i,
                a,
                r = this._utils.getClosestStation(this._stations, e, this._minWxCircleDist, !0, this._showStation, this);
            if (((this._showingAllInView = !1), 1 == r.length)) this._showSelectedCamera(r[0]);
            else if (r.length > 1) {
                for (i = 0; i < r.length; i++) this._stations.features[r[i]].properties.description._sleeping && (r.splice(i, 1), i--);
                if (1 == r.length) return void this._showSelectedCamera(r[0]);
                for (i in (((t = document.getElementById("chooseCameras")).innerHTML = ""), r))
                    (a = this._stations.features[r[i]].properties.description.name),
                        this._stations.features[r[i]].properties.description.hasOwnProperty("az_current") ? (a += " (PTZ)") : (a += " (Fixed)"),
                        (t.innerHTML += '<button class="fireButton" onclick="firemap.cameras._showSelectedCamera(' + r[i] + ')">' + a + "</button><br/>");
                this._overlay.show("chooseCameraOverlay");
            }
        },
        _showSelectedCamera: function (e, t) {
            var i = this,
                a = this._stations.features[e];
            if (
                (this._overlay.close("chooseCameraOverlay"),
                this._enableAdvanced || this._closeAllOverlays(),
                a && a.hasOwnProperty("properties") && a.properties.hasOwnProperty("description") && a.properties.hasOwnProperty("latest-images"))
            ) {
                let _ = (this._selectedStation = a.properties.description._id);
                if ((this.redraw(), this._openOverlays[_])) return void this._overlay.show(this._openOverlays[_].id);
                (this._openOverlays[_] = { index: e }), (this._openCameraIds[e] = !0);
                let y = document.createElement("DIV");
                (this._openOverlays[_].id = y.id = this._selectedStation),
                    (y.className = "overlay draggable camOverlay"),
                    (y.onmouseover = function () {
                        (i._selectedStation = _), i.redraw();
                    }),
                    document.body.appendChild(y);
                let f = document.createElement("DIV");
                (f.className = "btn"),
                    (f.onclick = function () {
                        i._closeThumbnail(_);
                    }),
                    y.appendChild(f);
                let g = document.createElement("DIV");
                (g.className = "titleText"), (g.innerHTML = a.properties.description.name), y.appendChild(g);
                let v = document.createElement("DIV");
                y.appendChild(v);
                let w = new Spinner(),
                    L = document.createElement("TABLE");
                y.appendChild(L);
                let b = null;
                t && (b = { position: "lefttop", ignoreSavedPosition: !0 }), this._overlay.show(y.id, b);
                var r = a.properties["latest-images"],
                    n = "",
                    s = "",
                    o = 0,
                    l = !1,
                    d = !1,
                    m = function () {
                        let t = this;
                        w.stop(),
                            this.naturalHeight + this.naturalWidth === 0
                                ? ((L.innerHTML = '<tr><td colspan="2">Error loading image. Will try again.</td></tr>'),
                                  (i._openOverlays[_]._errorTimeoutId = window.setTimeout(function () {
                                      i._showSelectedCamera(e);
                                  }, 5e3)))
                                : i._openOverlays[_].reloadTimerId ||
                                  (i._openOverlays[_].reloadTimerId = window.setInterval(
                                      function () {
                                          let e;
                                          (e = t.src.indexOf("&cache=") > -1 ? t.src.split("&cache=")[0] : t.src), (e += "&cache=" + i._imageLoadCache++), (t.src = e);
                                      },
                                      a.properties.description.fov ? i._reloadTime.ptz : i._reloadTime.fixed
                                  ));
                    };
                for (var c in r) {
                    var u = r[c];
                    for (var h in u) {
                        if ("Coming soon" === u[h].image) {
                            l = !0;
                            break;
                        }
                        if ("color" === u[h].type) {
                            if (a.properties.description._sleeping) {
                                d = !0;
                                break;
                            }
                            1 === ++o && w.spin(v),
                                a.properties.description.hasOwnProperty("az_current")
                                    ? (n += "<td> Azimuth " + parseFloat(a.properties.description.az_current).toFixed(2) + "Â°</td>")
                                    : (n += "<td>" + u[h].direction.charAt(0).toUpperCase() + u[h].direction.slice(1) + "</td>");
                            var p = new Image();
                            (p.onload = p.onerror = p.onabort = m),
                                0 != u[h].thumbnail.indexOf("http") && (u[h].thumbnail = Constants.urls.pylaski + u[h].thumbnail),
                                0 != u[h].image.indexOf("http") && (u[h].image = Constants.urls.pylaski + u[h].image),
                                (p.src = u[h].thumbnail),
                                a.properties.description.fov
                                    ? ((s += '<td><a href="' + (Constants.camimg_html ? Constants.camimg_html : "camimg.html") + "?" + u[h].image + '" target="_blank"><img src="' + p.src + '" style="width:240px; height:135px"></a></td>'),
                                      (this._camUrls[u[h].image] = {
                                          lon: a.geometry.coordinates[0],
                                          lat: a.geometry.coordinates[1],
                                          elev: a.geometry.coordinates[2],
                                          fov: a.properties.description.fov,
                                          tilt_current: a.properties.description.tilt_current,
                                          zoom_current: a.properties.description.zoom_current,
                                          az_current: a.properties.description.az_current,
                                          id: a.properties.description.id,
                                      }))
                                    : (s += '<td><a href="camimg.html?' + u[h].image + '" target="_blank"><img src="' + p.src + '"></a></td>');
                        }
                    }
                }
                l
                    ? ((L.innerHTML = '<tr><td colspan="2">Camera coming soon.</td></tr>'), this._overlay.show(y.id))
                    : d
                    ? ((L.innerHTML = '<tr><td colspan="2">Camera is asleep.</td></tr>'), this._overlay.show(y.id))
                    : 0 === o
                    ? ((L.innerHTML = '<tr><td colspan="2">No images found.</td></tr>'), this._overlay.show(y.id))
                    : (L.innerHTML = "<tr>" + n + "</tr><tr>" + s + "</tr>");
            }
        },
        _closeThumbnail: function (e) {
            this._overlay.close(this._openOverlays[e].id),
                delete this._openCameraIds[this._openOverlays[e].index],
                this._openOverlays[e].reloadTimerId && (window.clearInterval(this._openOverlays[e].reloadTimerId), (this._openOverlays[e].reloadTimerId = null)),
                this._openOverlays[e].errorTimeoudId && (window.clearTimeout(this._openOverlays[e].reloadTimerId), (this._openOverlays[e].errorTimeoudId = null)),
                delete this._openOverlays[e],
                e === this._selectedStation && ((this._selectedStation = null), this.redraw());
        },
        _drawCanvasPTZViews: function (e, t) {
            var i = t.options._context;
            if (null !== t.canvas) {
                i._canvasUtils.clearCanvas(t);
                var a,
                    r,
                    n = i._map.getBounds(),
                    s = t.canvas.getContext("2d");
                if (i._stations && i._stations.features)
                    for (s.strokeStyle = "black", a = 0; a < i._stations.features.length; a++) {
                        var o = i._stations.features[a];
                        if (o.properties.hasOwnProperty("latest-images")) {
                            if (!((i._showStation(o) && n.contains([o.geometry.coordinates[1], o.geometry.coordinates[0]])) || i._openCameraIds[a])) continue;
                            (r = { ctx: s, center: i._map.latLngToContainerPoint(L.latLng([o.geometry.coordinates[1], o.geometry.coordinates[0]])), erase: !1 }), (o.geometry.centerPoint = r.center);
                            var l = o.geometry.centerPoint,
                                d = o.properties.description,
                                m = o.properties.description._id === i._selectedStation;
                            if (i._showPTZView && d.fov_center && d.fov_lft && d.fov_rt && (!i._showingAllInView || i._openCameraIds[a])) {
                                var c = i._map.latLngToContainerPoint(L.latLng([d.fov_center[1], d.fov_center[0]])),
                                    u = i._map.latLngToContainerPoint(L.latLng([d.fov_lft[1], d.fov_lft[0]])),
                                    h = i._map.latLngToContainerPoint(L.latLng([d.fov_rt[1], d.fov_rt[0]]));
                                s.beginPath(),
                                    s.moveTo(l.x, l.y),
                                    s.lineTo(u.x, u.y),
                                    s.bezierCurveTo(u.x, u.y, c.x, c.y, h.x, h.y),
                                    s.closePath(),
                                    i._selectedStation,
                                    (s.fillStyle = "rgba(0,0,255,0.075)"),
                                    s.fill(),
                                    m && ((s.lineWidth = 1), (s.strokeStyle = "black"), s.stroke());
                            }
                        } else console.log("camera with no latest-images: " + o.properties.description.name);
                    }
            }
        },
        _drawCanvasCameras: function (e, t) {
            var i,
                a,
                r = t.options._context;
            if (null !== t.canvas) {
                r._canvasUtils.clearCanvas(t);
                var n = r._map.getZoom(),
                    s = t.canvas.getContext("2d"),
                    o = r._map.getCenter(),
                    l = r._map.latLngToContainerPoint(o),
                    d = l.clone();
                if (((d.x += r._canvasUtils.wxStationRadius), (r._minWxCircleDist = l.distanceTo(d)), r._stations && r._stations.features))
                    for (i = 0; i < r._stations.features.length; i++) {
                        var m = r._stations.features[i];
                        if (m.properties.hasOwnProperty("latest-images")) {
                            if (!r._showStation(m)) continue;
                            (a = { ctx: s, center: r._map.latLngToContainerPoint(L.latLng([m.geometry.coordinates[1], m.geometry.coordinates[0]])), erase: !1 }), (m.geometry.centerPoint = a.center);
                            var c = m.geometry.centerPoint,
                                u = m.properties.description,
                                h = m.properties.description._id === r._selectedStation;
                            if (r._showPTZTarget && u.fov_center && (!r._showingAllInView || r._openCameraIds[i])) {
                                var p = r._map.latLngToContainerPoint(L.latLng([u.fov_center[1], u.fov_center[0]]));
                                s.beginPath(), s.moveTo(c.x, c.y), s.lineTo(p.x, p.y), s.closePath(), (s.strokeStyle = "rgba(255,0,255,0.5)"), (s.lineWidth = 2), s.stroke(), h && ((s.strokeStyle = "black"), s.stroke());
                            }
                            !r._showingAllInView || r._openCameraIds[i] ? (s.strokeStyle = "black") : (s.strokeStyle = "rgb(0, 0, 0, 0.1)"),
                                (a = { ctx: s, center: c }),
                                h && (a.width = 7),
                                n < r._minStationZoom && (a.scale = 1 + 0.5 * (r._minStationZoom - n)),
                                r._canvasUtils.drawStation(a),
                                "Coming soon" === m.properties["latest-images"][0][0].image
                                    ? (s.fillStyle = r._colors["coming soon"])
                                    : u._sleeping
                                    ? (s.fillStyle = r._colors.sleeping)
                                    : u.ptz
                                    ? (s.fillStyle = r._colors.ptz)
                                    : (s.fillStyle = r._colors.fixed),
                                r._showingAllInView && !r._openCameraIds[i] && (s.fillStyle += "2F"),
                                s.fill(),
                                n >= r._minStationZoom &&
                                    ((s.font = "12px FontAwesome"), !r._showingAllInView || r._openCameraIds[i] ? (s.fillStyle = "white") : (s.fillStyle = "rgb(255,255,255, 0.5)"), s.fillText("ï€°", c.x - 6.5, c.y + 4.5));
                        } else console.log("camera with no latest-images: " + m.properties.description.name);
                    }
            }
        },
        _getCameraLocations: function (e) {
            var t,
                i,
                a = this;
            document.hidden ||
                ((t = e ? "minLat=" + (i = this._map.getBounds()).getSouth() + "&maxLat=" + i.getNorth() + "&minLon=" + i.getWest() + "&maxLon=" + i.getEast() : "minLat=0&maxLat=90&minLon=-180&maxLon=0"),
                (a._ajaxCameras = $.ajax({ url: Constants.urls.pylaski + "stations?camera=only&selection=boundingBox&" + t, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "cameraStations", timeout: 1e4 })
                    .always(function () {
                        a._ajaxCameras = null;
                    })
                    .fail(function (e, t) {
                        "abort" !== t && alert("Error retrieving cameras: " + t);
                    })
                    .done(function (t) {
                        var i;
                        if (((a._updateTimer.lastQueryTime = moment()), e && a._getCameraLocations(), t && t.features)) {
                            for (i in t.features) {
                                let e = t.features[i];
                                e.properties.description.owner ? (e.properties.description._id = e.properties.description.name + " " + e.properties.description.owner) : (e.properties.description._id = e.properties.description.id),
                                    t.features[i].properties.description.hasOwnProperty("az_current") && !t.features[i].properties.description.hasOwnProperty("fov_center") && (t.features[i].properties.description._sleeping = !0);
                            }
                            t.features.sort(function (e, t) {
                                return e.properties.description.ptz ? -1 : 1;
                            }),
                                t.features.sort(function (e, t) {
                                    return e.properties.description._sleeping ? -1 : 1;
                                });
                        }
                        (a._stations = t), a.redraw(!e), !e && a._showCamerasAfterLoadLatLng && (a.showCamerasViewingLatLng(a._showCamerasAfterLoadLatLng), (a._showCamerasAfterLoadLatLng = null));
                    })));
        },
        _updateCameraCanvas: function (e) {
            this._map && (this._ajaxCameras && (this._ajaxCameras.abort(), (this._ajaxCameras = null)), this._getCameraLocations(e)),
                (this._updateTimer.timer = window.setTimeout(
                    function () {
                        this._updateCameraCanvas();
                    }.bind(this),
                    1e3 * this._queryFrequency
                ));
        },
        _showStation: function (e) {
            return (e.properties.description.ptz && this._showPTZ) || (!e.properties.description.hasOwnProperty("ptz") && this._showFixed);
        },
    }),
    (PTZCameraStations = function (e) {
        _cameraStationsSingletonLayer || (_cameraStationsSingletonLayer = new _CameraStations(e)), (this._options = e);
    }),
    (PTZCameraStations.prototype = {
        onAdd: function (e) {
            _cameraStationsSingletonLayer.onUpdate(e, { ptz: !0 }), this._options.overlay.show("cameraConfigOverlay");
        },
        onRemove: function (e) {
            _cameraStationsSingletonLayer.onUpdate(e, { ptz: !1 }), this._options.overlay.close("cameraConfigOverlay");
        },
        _showSelectedCamera: function (e) {
            _cameraStationsSingletonLayer._showSelectedCamera(e);
        },
        setCameraClickListener: function (e) {
            _cameraStationsSingletonLayer.setCameraClickListener(e);
        },
        showCamerasViewingLatLng: function (e, t) {
            _cameraStationsSingletonLayer.showCamerasViewingLatLng(e, t);
        },
        setAdvanced: function (e) {
            _cameraStationsSingletonLayer.setAdvanced(e);
        },
    }),
    (FixedCameraStations = function (e) {
        _cameraStationsSingletonLayer || (_cameraStationsSingletonLayer = new _CameraStations(e));
    }),
    (FixedCameraStations.prototype = {
        onAdd: function (e) {
            _cameraStationsSingletonLayer.onUpdate(e, { fixed: !0 });
        },
        onRemove: function (e) {
            _cameraStationsSingletonLayer.onUpdate(e, { fixed: !1 });
        },
    });
var CaltransCameras = function (e) {
    (this._canvasUtils = new CanvasUtils()),
        (this._utils = new Utils()),
        (this._stations = null),
        (this._map = null),
        (this._minWxCircleDist = -1),
        (this._ajaxCameras = null),
        (this._overlay = window.firemap.overlay),
        (this._minStationZoom = 10),
        (this._spinner = new Spinner()),
        e || (e = {}),
        (e._context = this),
        (e.zIndex = Constants.zLayers.cameraStation),
        (this._layer = L.canvasOverlay(this._drawCanvasCameras, e)),
        (this._colors = { caltrans: "#668899" }),
        (window.firemap.caltransCameras = this);
};
CaltransCameras.prototype = {
    onAdd: function (e) {
        (this._map = e),
            this._layer.onAdd(e),
            e.on("click", this._clickCameraStation, this),
            this._overlay.on("close", this._closeThumbnail, this),
            window.setTimeout(
                function () {
                    this._updateCameraCanvas(!0);
                }.bind(this),
                0
            );
    },
    onRemove: function (e) {
        this._ajaxCameras && (this._ajaxCameras.abort(), (this._ajaxCameras = null)), this._overlay.off("close", this._closeThumbnail, this), e.off("click", this._clickCameraStation, this), this._layer.onRemove(e), (this._map = null);
    },
    redraw: function () {
        this._layer.redraw();
    },
    _clickCameraStation: function (e) {
        var t,
            i,
            a,
            r = this._utils.getClosestStation(this._stations, e, this._minWxCircleDist, !0, this._showStation, this);
        if (1 == r.length) this._showSelectedCamera(r[0]);
        else if (r.length > 1) {
            if (1 == r.length) return void this._showSelectedCamera(r[0]);
            for (i in (((t = document.getElementById("chooseCameras")).innerHTML = ""), r))
                (a = this._stations.features[r[i]].properties.name), (t.innerHTML += '<button class="fireButton" onclick="firemap.caltransCameras._showSelectedCamera(' + r[i] + ')">' + a + "</button><br/>");
            this._overlay.show("chooseCameraOverlay");
        }
    },
    _showSelectedCamera: function (e) {
        var t = this._stations.features[e];
        if ((this._overlay.close("chooseCameraOverlay"), this._errorTimeoutId && window.clearInterval(this._errorTimeoutId), t && t.hasOwnProperty("properties"))) {
            (this._selectedStation = t.properties.name), this.redraw();
            var i = t.properties.name;
            if (t.properties.descriptio) {
                "none" !== $("#camOverlay").css("display") && $("#camOverlay table tr:gt(0)").remove(), (document.getElementById("camTitle").innerHTML = i);
                let e = /src="([^"]*)/g.exec(t.properties.descriptio)[1];
                $("#camOverlay table").append('<tr><td><a href="camimg.html?' + e + '" target="_blank"><img src="' + e + '" style="width:240px; height:135px" onerror="firemap.caltransCameras.loadError()"></a></td></tr>'),
                    this._overlay.show("camOverlay");
            }
        }
    },
    loadError: function () {
        $("#camOverlay table tr:gt(0)").remove(), $("#camOverlay table").append('<tr><td><img src="lib/images/camera-error.jpg" style="width:240px; height:135px"></td></tr>');
    },
    _closeThumbnail: function (e) {
        "camOverlay" === e.id && ($("#camOverlay table tr:gt(0)").remove(), (this._selectedStation = null), this.redraw());
    },
    _drawCanvasCameras: function (e, t) {
        var i,
            a,
            r = t.options._context;
        r._canvasUtils.clearCanvas(t);
        var n = r._map.getZoom(),
            s = t.canvas.getContext("2d"),
            o = r._map.getCenter(),
            l = r._map.latLngToContainerPoint(o),
            d = l.clone();
        if (((d.x += r._canvasUtils.wxStationRadius), (r._minWxCircleDist = l.distanceTo(d)), r._stations && r._stations.features))
            for (s.strokeStyle = "black", i = 0; i < r._stations.features.length; i++) {
                var m = r._stations.features[i];
                (a = { ctx: s, center: r._map.latLngToContainerPoint(L.latLng([m.geometry.coordinates[1], m.geometry.coordinates[0]])), erase: !1 }), (m.geometry.centerPoint = a.center);
                var c = m.geometry.centerPoint,
                    u = m.properties.name === r._selectedStation;
                (a = { ctx: s, center: c }),
                    u && (a.width = 7),
                    n < r._minStationZoom ? (a.scale = 1 + 0.7 * (r._minStationZoom - n)) : (a.scale = 1.3),
                    r._canvasUtils.drawStation(a),
                    (s.fillStyle = r._colors.caltrans),
                    s.fill(),
                    n >= r._minStationZoom && ((s.font = "11px FontAwesome"), (s.fillStyle = "white"), s.fillText("ï€°", c.x - 5.7, c.y + 3.5)),
                    u && ((s.lineWidth = 1), (s.strokeStyle = "black"), s.stroke());
            }
    },
    _getCameraLocations: function (e) {
        var t,
            i,
            a = this;
        (t = e ? "bbox=" + (i = this._map.getBounds()).getWest() + "," + i.getSouth() + "," + i.getEast() + "," + i.getNorth() + ",epsg:4326" : ""),
            (a._ajaxCameras = $.ajax({
                url: "https://swat.sdsc.edu/geoserver/wfs?service=wfs&version=2.0.0&outputFormat=application/json&request=GetFeature&typeNames=WIFIRE:caltrans_cameras&srsName=epsg:4326&" + t,
                type: "GET",
                dataType: "json",
                jsonp: "callback",
                jsonpCallback: "cameraStations",
                timeout: 1e4,
            })
                .always(function () {
                    a._ajaxCameras = null;
                })
                .fail(function (e, t) {
                    "abort" !== t && alert("Error retrieving cameras: " + t);
                })
                .done(function (t) {
                    e && a._getCameraLocations(), (a._stations = t), a.redraw();
                }));
    },
    _updateCameraCanvas: function (e) {
        this._map && (this._ajaxCameras && (this._ajaxCameras.abort(), (this._ajaxCameras = null)), this._getCameraLocations(e)),
            window.setTimeout(
                function () {
                    this._updateCameraCanvas();
                }.bind(this),
                6e5
            );
    },
    _showStation: function (e) {
        return !0;
    },
};
var WeatherStations = function (e, t) {
    (this._controls = e),
        (this._options = t),
        (this._canvasUtils = new CanvasUtils()),
        (this._utils = new Utils()),
        (this._stations = null),
        (this._map = null),
        (this._ajaxStations = null),
        (this._ajaxStationData = null),
        (this._minWxCircleDist = -1),
        (this._minStationZoom = 10),
        (this._shownCharts = {}),
        (this._stationNamePopup = L.popup({ autoPan: !1 })),
        (this._closestStationName = null),
        (t._context = this),
        (this._layer = L.canvasOverlay(this._updateWxCanvas, t));
    var i = this;
    let a = function () {
        Object.keys(i._shownCharts).length > 0 && i.resizeCharts();
    };
    window.addEventListener("resize", a), (document.getElementById("wxWindTab").onclick = document.getElementById("wxHumidTab").onclick = a), (this._queryFrequency = 300), (this._updateTimer = { timer: null, lastQueryTime: null });
};
WeatherStations.prototype = {
    onAdd: function (e) {
        (this._map = e),
            this._layer.onAdd(e),
            e.on("click", this._clickWxStation, this),
            this._options.overlay.on("close", this._closeChart, this),
            window.setTimeout(
                function () {
                    this._updateCanvasFromTimer(!0);
                }.bind(this),
                0
            ),
            (this._visibilityFunction = this._utils.setVisibilityTimer(this._updateTimer, this._queryFrequency, this._updateCanvasFromTimer, this));
    },
    onRemove: function (e) {
        this._utils.removeVisibilityTimer(this._visibilityFunction),
            (this._visibilityFunction = null),
            this._updateTimer.timer && (window.clearTimeout(this._updateTimer.timer), (this._updateTimer.timer = null)),
            this._ajaxStations && (this._ajaxStations.abort(), (this._ajaxStations = null)),
            this._options.overlay.off("close", this._closeChart),
            e.off("click", this._clickWxStation, this),
            this._layer.onRemove(e),
            (this._map = null),
            (document.getElementById("wxStatusControl").style.display = "none"),
            this._options.overlay.close(this._controls.wxTypeControl, { sharedOwner: "WeatherStations" });
    },
    redraw: function () {
        this._layer && this._layer.redraw();
    },
    _updateCanvasFromTimer: function (e) {
        this._map && (this._ajaxCameras && (this._ajaxCameras.abort(), (this._ajaxCameras = null)), this._getWxLocations(e)),
            (this._updateTimer.timer = window.setTimeout(
                function () {
                    this._updateCanvasFromTimer();
                }.bind(this),
                1e3 * this._queryFrequency
            ));
    },
    _updateWxCanvas: function (e, t) {
        var i = t.options._context;
        i._options.overlay.isShown(i._controls.wxTypeControl) || i._options.overlay.show(i._controls.wxTypeControl, { sharedOwner: "WeatherStations" }), i._canvasUtils.clearCanvas(t), i._drawWxCanvas(e, t);
    },
    setLayerTime: function (e) {
        (this._toTime = e), (this._fromTime = moment(e).subtract(20, "minutes")), this._layer.redraw();
    },
    setWeatherType: function (e) {
        this._controls.wxTypeSlider.noUiSlider.set(e);
    },
    _getWxLocations: function (e) {
        var t = this;
        document.getElementById("wxStatusControl").style.display = "block";
        var i = new Spinner({ left: "15px", scale: 0.5 }).spin(document.getElementById("wxSpinner")),
            a = Constants.urls.pylaski + "stations?selection=boundingBox";
        if (e) {
            let e = this._map.getBounds();
            a += "&minLat=" + e.getSouth() + "&maxLat=" + e.getNorth() + "&minLon=" + e.getWest() + "&maxLon=" + e.getEast();
        } else a += "&minLat=0&maxLat=90&minLon=-180&maxLon=0";
        this._toTime && (a += "&from=" + this._fromTime.format("YYYY-MM-DDTHH:mm:ssZ") + "&to=" + this._toTime.format("YYYY-MM-DDTHH:mm:ssZ")),
            (t._ajaxStations = $.ajax({ url: a, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "wxStations", timeout: 1e4 })
                .always(function () {
                    (t._ajaxStations = null), i.stop();
                })
                .fail(function (e, t) {
                    "abort" !== t && alert("Error retrieving measurements: " + t);
                })
                .done(function (i) {
                    (t._updateTimer.lastQueryTime = moment()), (t._stations = i), t._layer.redraw(), e && t._getWxLocations();
                }));
    },
    _drawWxCanvas: function (e, t) {
        var i = t.options._context;
        i._canvasUtils.clearCanvas(t);
        var a,
            r = i._controls.wxTypeSlider.noUiSlider.get(),
            n = i._map.getZoom(),
            s = i._map.getCenter(),
            o = i._map.latLngToContainerPoint(s),
            l = o.clone();
        if (((l.x += i._canvasUtils.wxStationRadius), (i._minWxCircleDist = o.distanceTo(l)), i._stations && i._stations.hasOwnProperty("features")))
            for (a in i._stations.features) {
                var d = i._stations.features[a],
                    m = { ctx: t.canvas.getContext("2d"), center: i._map.latLngToContainerPoint(L.latLng([d.geometry.coordinates[1], d.geometry.coordinates[0]])), erase: !1 };
                (d.geometry.centerPoint = m.center),
                    n < i._minStationZoom
                        ? (m.scale = 1 + 0.5 * (i._minStationZoom - n))
                        : !d.properties.hasOwnProperty("wind_direction") || ("Wind" !== r && "Gust" !== r) || ((m.dir = d.properties.wind_direction.value), i._canvasUtils.drawWindArrow(m)),
                    ("Mesowest" == d.properties.description.provider || d.properties.hasOwnProperty("temperature") || d.properties.hasOwnProperty("latest-images")) &&
                        (d.properties.hasOwnProperty("latest-images") ||
                            (d.properties.description.name === i._selectedStation && (m.width = 7),
                            (m.v = null),
                            (m.color = { bg: "white" }),
                            "Air Temperature" === r
                                ? (d.properties.hasOwnProperty("temperature") && d.properties.temperature.hasOwnProperty("units") && "F" === d.properties.temperature.units && (m.v = d.properties.temperature.value),
                                  (m.color = i._canvasUtils.temperatureColor(m.v)))
                                : "Humidity" === r
                                ? (d.properties.hasOwnProperty("relative_humidity") && d.properties.relative_humidity.hasOwnProperty("units") && "%" === d.properties.relative_humidity.units && (m.v = d.properties.relative_humidity.value),
                                  (m.color = i._canvasUtils.humidityColor(m.v)))
                                : "Wind" === r
                                ? (d.properties.hasOwnProperty("wind_speed") &&
                                      d.properties.wind_speed.hasOwnProperty("units") &&
                                      ("mps" === d.properties.wind_speed.units ? (m.v = d.properties.wind_speed.value * Constants.MPS_TO_MPH) : "mph" === d.properties.wind_speed.units && (m.v = d.properties.wind_speed.value)),
                                  (m.color = i._canvasUtils.windSpeedColor(m.v)))
                                : "Gust" === r
                                ? (d.properties.hasOwnProperty("wind_gust") &&
                                      d.properties.wind_gust.hasOwnProperty("units") &&
                                      ("mps" === d.properties.wind_gust.units ? (m.v = d.properties.wind_gust.value * Constants.MPS_TO_MPH) : "mph" === d.properties.wind_gust.units && (m.v = d.properties.wind_gust.value)),
                                  (m.color = i._canvasUtils.windSpeedColor(m.v)))
                                : "Fuel Moisture" === r &&
                                  (d.properties.hasOwnProperty("fm_dead_10") && d.properties.fm_dead_10.hasOwnProperty("units") && "gm" === d.properties.fm_dead_10.units && (m.v = d.properties.fm_dead_10.value),
                                  (m.color = i._canvasUtils.humidityColor(m.v))),
                            ("number" == typeof m.v || n >= i._minStationZoom) && (i._canvasUtils.drawStation(m), i._canvasUtils.drawValue(m))));
            }
    },
    _clickWxStation: function (e) {
        var t = this._utils.getClosestStation(this._stations, e, this._minWxCircleDist);
        if (t && t.hasOwnProperty("properties") && t.properties.hasOwnProperty("description")) {
            if (((this._selectedStation = t.properties.description.name), this.redraw(), this._chosenCallback))
                return this._chosenCallback(t), this._map.off("mousemove", this._showStationName, this), (this._chosenCallback = null), void (this._closestStationName = null);
            this._ajaxStationData && this._ajaxStationData.abort(), this._getWxStationData(t);
        }
    },
    _closeChart: function (e) {
        "wxChartControl" === e.id && ((this._selectedStation = null), this.redraw());
    },
    _getWxStationData: function (e) {
        var t,
            i = this,
            a = (title = e.properties.description.name);
        e.properties.description.hasOwnProperty("owner") && (title += " (" + e.properties.description.owner + ")");
        let r = document.querySelectorAll("#wxTitle");
        for (let e in r) r[e].innerHTML = title;
        var n = new Spinner().spin(),
            s = this._utils.initChart("wxTemperatureChart", this),
            o = this._utils.initChart("wxWindSpeedChart", this),
            l = this._utils.initChart("wxWindDirectionChart", this),
            d = this._utils.initChart("wxFuelMoistureHumidityChart", this);
        s.appendChild(n.el),
            this._options.overlay.isShown(this._controls.wxChartControl) || (this.resizeCharts(), this._options.overlay.show(this._controls.wxChartControl)),
            (t = this._toTime ? moment(this._toTime) : moment()),
            (this._ajaxStationData = $.ajax({
                url:
                    Constants.urls.pylaski +
                    "stations/data?selection=closestTo&lat=" +
                    e.geometry.coordinates[1] +
                    "&lon=" +
                    e.geometry.coordinates[0] +
                    "&observable=temperature&observable=relative_humidity&observable=wind_speed&observable=wind_gust&observable=wind_direction&observable=fm_dead_10&from=" +
                    moment(t).subtract(1, "days").format("YYYY-MM-DDTHH:mm:ssZ") +
                    "&to=" +
                    t.format("YYYY-MM-DDTHH:mm:ssZ"),
                type: "GET",
                dataType: "jsonp",
                jsonp: "callback",
                jsonpCallback: "wxData",
                timeout: 3e4,
            })
                .always(function () {
                    i._ajaxStationData = null;
                })
                .fail(function (e, t) {
                    "abort" !== t && (s.innerHTML = '<div style="text-align:center;">Error retrieving measurements: ' + t + ".</div>");
                })
                .done(function (e) {
                    if (e.hasOwnProperty("features")) {
                        if (e.features.length > 0) {
                            var t = e.features[0];
                            if (t.hasOwnProperty("properties")) {
                                if (a != t.properties.description.name) return void (s.innerHTML = '<div style="text-align:center;">No measurements found.</div>');
                                for (
                                    var r = t.properties,
                                        n = r.hasOwnProperty("timestamp") ? r.timestamp : null,
                                        m = r.hasOwnProperty("temperature") ? r.temperature : null,
                                        c = r.hasOwnProperty("relative_humidity") ? r.relative_humidity : null,
                                        u = r.hasOwnProperty("wind_speed") ? r.wind_speed : null,
                                        h = r.hasOwnProperty("wind_gust") ? r.wind_gust : null,
                                        p = r.hasOwnProperty("wind_direction") ? r.wind_direction : null,
                                        _ = r.hasOwnProperty("fm_dead_10") ? r.fm_dead_10 : null,
                                        y = r.hasOwnProperty("units") ? r.units : null,
                                        f = { temp: [], rh: [], ws: [], wg: [], wd: [], fm: [] },
                                        g = 0;
                                    g < n.length;
                                    g++
                                ) {
                                    var v = moment(n[g]).valueOf();
                                    if ((null !== m && f.temp.push([v, m[g]]), null !== c && f.rh.push([v, c[g]]), null !== u)) {
                                        var w = u[g];
                                        y && "mps" == y.wind_speed && (w *= Constants.MPS_TO_MPH), f.ws.push([v, w]);
                                    }
                                    if (null !== h) {
                                        var L = h[g];
                                        y && "mps" == y.wind_gust && (L *= Constants.MPS_TO_MPH), f.wg.push([v, L]);
                                    }
                                    null !== p && f.wd.push([v, p[g]]), null !== _ && f.fm.push([v, _[g]]);
                                }
                                var b = [];
                                (i._shownCharts = { wind: [], humid: [] }),
                                    null != m && i._shownCharts.humid.push("wxTemperatureChart"),
                                    (null == u && null == h) || i._shownCharts.wind.push("wxWindSpeedChart"),
                                    null != p && i._shownCharts.wind.push("wxWindDirectionChart"),
                                    (null == _ && null == c) || i._shownCharts.humid.push("wxFuelMoistureHumidityChart");
                                var S,
                                    x = Constants.chartHeight.big + "px";
                                if (
                                    (null === m
                                        ? (s.innerHTML = '<div style="text-align:center;">No temperature measurements.</div>')
                                        : ((b = []),
                                          null !== m && b.push({ title: "Air Temperature", units: "F", values: f.temp, yTickInterval: 5, xTickInterval: Constants.chartXTickInterval, color: Constants.wxChartColors.airTemp }),
                                          (s.style.height = x),
                                          i._utils.showChart(b, { id: "wxTemperatureChart", title: "Temperature" })),
                                    null === u && null === h
                                        ? (o.innerHTML = '<div style="text-align:center;">No wind speed measurements.</div>')
                                        : ((b = []),
                                          null !== u
                                              ? b.push({ title: "Speed", units: "mph", values: f.ws, ytickInterval: 10, xTickInterval: Constants.chartXTickInterval, color: Constants.wxChartColors.windSpeed })
                                              : null !== h && b.push({ title: "Gust", units: "mph", values: f.wg, yTickInterval: 10, xTickInterval: Constants.chartXTickInterval, color: Constants.wxChartColors.windGust }),
                                          null !== h && null !== u && b.push({ title: "Gust", units: "mph", values: f.wg, yTickInterval: 10, xTickInterval: Constants.chartXTickInterval, color: Constants.wxChartColors.windGust }),
                                          (o.style.height = x),
                                          i._utils.showChart(b, { id: "wxWindSpeedChart", title: "Speed/Gust", singleYAxis: !0 })),
                                    null === p
                                        ? (l.innerHTML = '<div style="text-align:center;">No wind direction measurements.</div>')
                                        : ((b = []).push({ title: "Direction", units: "", values: f.wd, color: Constants.wxChartColors.windDirection, max: 360, yTickInterval: 90, xTickInterval: Constants.chartXTickInterval }),
                                          (l.style.height = x),
                                          i._utils.showChart(b, { id: "wxWindDirectionChart", title: "Direction" })),
                                    null === _ && null === c)
                                )
                                    d.innerHTML = '<div style="text-align:center;">No fuel moisture or relative humidity measurements.</div>';
                                else
                                    (b = []),
                                        null !== c && b.push({ title: "Relative Humidity", units: "%", values: f.rh, color: Constants.wxChartColors.humidity, max: 100, yTickInterval: 10, xTickInterval: Constants.chartXTickInterval }),
                                        null !== _ && b.push({ title: "Fuel Moisture", units: "gm", values: f.fm, color: Constants.wxChartColors.fuelMoisture, yTickInterval: 10, xTickInterval: Constants.chartXTickInterval }),
                                        (S = null !== c && null !== _ ? "Humidity & Fuel Moisture" : null !== c ? "Humidity" : "Fuel Moisture"),
                                        (d.style.height = x),
                                        i._utils.showChart(b, { id: "wxFuelMoistureHumidityChart", title: S });
                            }
                        }
                        i.resizeCharts();
                    } else s.innerHTML = '<div style="text-align:center;">No measurements found.</div>';
                }));
    },
    resizeCharts: function () {
        var e,
            t,
            i = document.getElementById("wxChartControl"),
            a = document.getElementById("wxTitle"),
            r = document.getElementById("wxTemperatureChart"),
            n = document.getElementById("wxWindSpeedChart"),
            s = document.getElementById("wxWindDirectionChart"),
            o = document.getElementById("wxFuelMoistureHumidityChart"),
            l = window.innerWidth - 30,
            d = l < Constants.chartWidth.max ? l : Constants.chartWidth.max;
        let m;
        if (
            ((i.style.width = a.style.width = r.style.width = n.style.width = s.style.width = o.style.width = d + "px"),
            $(".tab__content").css("width", d + "px"),
            (m = document.getElementById("wxWindTab").checked ? "wind" : "humid"),
            this._shownCharts[m])
        ) {
            for (t in ((e = this._utils.getChartHeight("wxTitle", this._shownCharts[m].length, 2, 30)), this._shownCharts[m])) document.getElementById(this._shownCharts[m][t]).style.height = e + "px";
            (e = 2 * e + 20), $("#wxTabs").css("height", e + "px"), (i.style.height = 35 + e + "px");
        } else i.style.height = "100px";
    },
    chooseStation: function (e, t) {
        (this._chosenCallback = e), (this._chosenObservables = t), this._map.on("mousemove", this._showStationName, this);
    },
    _showStationName: function (e) {
        var t,
            i,
            a = this._utils.getClosestStation(this._stations, e, this._minWxCircleDist),
            r = [];
        if (a && a.hasOwnProperty("properties") && a.properties.hasOwnProperty("description") && (!this._closestStationName || this._closestStationName != a.properties.description.name)) {
            if (((t = "<div style='text-align:center; font-weight:bold; font-size:14px'>"), (t += a.properties.description.name), (t += "</div>"), this._chosenObservables))
                for (i in this._chosenObservables) a.properties[this._chosenObservables[i]] || r.push(this._chosenObservables[i]);
            else a.properties.temperature || r.push("temperature"), a.properties.relative_humidity || r.push("relative humidity"), a.properties.wind_direction || r.push("wind direction"), a.properties.wind_speed || r.push("wind speed");
            r.length > 0 && (t += "<div style='color: red; font-size: 12px; font-weight:bold;'>No measurements for: " + r.join(", ") + "</div>"),
                this._stationNamePopup.setLatLng([a.geometry.coordinates[1], a.geometry.coordinates[0]]).setContent(t).openOn(this._map),
                (this._closestStationName = a.properties.description.name);
        }
    },
};
var RealTimeWeatherStations = function (e, t) {
    (this._controls = e),
        (this._options = t),
        (this._wssURL = "wss://firemap.sdsc.edu/livewx"),
        (this._canvasUtils = new CanvasUtils()),
        (this._map = null),
        this._socket,
        (this._stations = {}),
        (this._minStationZoom = 10),
        (t._context = this),
        (this._layer = L.canvasOverlay(this._updateRealTimeWxCanvas, t));
};
RealTimeWeatherStations.prototype = {
    onAdd: function (e) {
        (this._map = e), this._layer.onAdd(e), this._options.overlay.show(this._controls.wxTypeControl, { sharedOwner: "RealTimeWeatherStations" });
        let t = this;
        (this._visibilityChange = function () {
            document.hidden ? t._socket && (t._socket.close(), (t._socket = null)) : t._layer.redraw();
        }),
            document.addEventListener("visibilitychange", this._visibilityChange);
    },
    onRemove: function (e) {
        this._layer.onRemove(e),
            (this._map = null),
            this._options.overlay.close(this._controls.wxTypeControl, { sharedOwner: "RealTimeWeatherStations" }),
            this._socket && (this._socket.close(), (this._socket = null)),
            document.removeEventListener("visibilitychange", this._visibilityChange),
            (this._visibilityChangeListener = null);
    },
    _drawRealTimeWxCanvas: function (e, t) {
        var i = t.options._context;
        (zoom = i._map.getZoom()), (c = i._map.getCenter()), (p = i._map.latLngToContainerPoint(c)), (p2 = p.clone()), (p2.x += i._canvasUtils._wxStationRadius);
        var a = { ctx: t.canvas.getContext("2d"), center: i._map.latLngToContainerPoint(e.latlng) };
        zoom < i._minStationZoom && (a.scale = 1 + 0.5 * (i._minStationZoom - zoom)),
            e.data.winddirection &&
                (e.data.drawnWindDirection && ((a.erase = !0), (a.dir = e.data.drawnWindDirection), i._canvasUtils.drawWindArrow(a)),
                (a.erase = !1),
                (a.dir = e.data.winddirection),
                i._canvasUtils.drawWindArrow(a),
                (e.data.drawnWindDirection = e.data.winddirection)),
            i._canvasUtils.drawStation(a);
        var r = i._controls.wxTypeSlider.noUiSlider.get();
        "Air Temperature" === r
            ? ((a.v = e.data.temperature), (a.color = i._canvasUtils.temperatureColor(a.v)))
            : "Humidity" === r
            ? ((a.v = e.data.humidity), (a.color = i._canvasUtils.humidityColor(a.v)))
            : "Wind" === r
            ? ((a.v = e.data.windspeed * Constants.MPS_TO_MPH), (a.color = i._canvasUtils.windSpeedColor(a.v)))
            : "Gust" === r
            ? ((a.v = e.data.windgust * Constants.MPS_TO_MPH), (a.color = i._canvasUtils.windSpeedColor(a.v)))
            : ((a.v = null), (a.color = { bg: "white" })),
            i._canvasUtils.drawValue(a);
    },
    _updateRealTimeWxCanvas: function (e, t) {
        var i = t.options._context;
        if (i._socket) {
            if (i._stations) for (var a in (i._canvasUtils.clearCanvas(t), i._stations)) a.data && a.data.drawnWindDirection && (a.data.drawnWindDirection = null);
        } else
            (i._socket = new WebSocket(i._wssURL)),
                (i._socket.error = function (e) {
                    console.log("rt wx ws error: " + e);
                }),
                (i._socket.onopen = function (e) {
                    i._socket.send("start");
                }),
                (i._socket.onmessage = function (e) {
                    var a = JSON.parse(e.data);
                    if (a) {
                        var r = a.Name,
                            n = i._stations[r];
                        if (
                            (n ||
                                (((n = {}).latlng = new L.LatLng(parseFloat(a.lat), parseFloat(a.lng))),
                                (n.name = a.Name),
                                (n.data = { humidity: null, temperature: null, windspeed: null, windgust: null, winddirection: null }),
                                (i._stations[r] = n)),
                            a.hasOwnProperty("Ta"))
                        ) {
                            var s = a.Ta.split("."),
                                o = parseFloat(s[0]);
                            n.data.temperature = 1.8 * o + 32;
                        }
                        if (a.hasOwnProperty("Ua")) {
                            var l = a.Ua.split("P");
                            n.data.humidity = parseFloat(l[0]);
                        }
                        a.hasOwnProperty("Dm") && (n.data.winddirection = parseFloat(a.Dm.split("D")[0])),
                            a.hasOwnProperty("Sm") && (n.data.windspeed = parseFloat(a.Sm.split("D")[0])),
                            a.hasOwnProperty("Sx") && (n.data.windgust = parseFloat(a.Sx.split("D")[0])),
                            i._map.getBounds().contains(n.latlng) && i._drawRealTimeWxCanvas(n, t);
                    }
                });
    },
};
var AirQualityStations = function (e, t) {
    (this._controls = e),
        (this._options = t),
        (this._canvasUtils = new CanvasUtils()),
        (this._utils = new Utils()),
        (this._stations = null),
        (this._map = null),
        (this._minStationCircleDist = -1),
        (this._minStationZoom = 10),
        (this._ajaxStations = null),
        (this._ajaxStationData = null),
        (this._shownCharts = []),
        (this._aqTypes = {
            "PM2.5": { obs: "pm_2_5", max: 100, units: "ug/m3" },
            PM10: { obs: "pm_10", max: 250, units: "ug/m3" },
            NO2: { obs: "nitrogen_dioxide", max: 0.6, units: "ppm" },
            SO2: { obs: "sulfur_dioxide", max: 0.2, units: "ppm" },
            Ozone: { obs: "ozone", max: 0.15, units: "ppm" },
            CO: { obs: "carbon_monoxide", max: 9.8, units: "ppm" },
            "Black Carbon": { obs: "black_carbon", max: 2.67, units: "ug/m3" },
        }),
        (t._context = this),
        (this._layer = L.canvasOverlay(this._updateCanvas, t));
    var i = this;
    window.addEventListener("resize", function () {
        i._shownCharts.length > 0 && i.resizeCharts();
    });
};
AirQualityStations.prototype = {
    onAdd: function (e) {
        (this._map = e), this._layer.onAdd(e), e.on("click", this._clickStation, this), this._options.overlay.show(this._controls.aqTypeControl), this._options.overlay.on("close", this._closeChart, this);
    },
    onRemove: function (e) {
        this._options.overlay.off("close", this._closeChart, this),
            e.off("click", this._clickStation, this),
            this._layer.onRemove(e),
            (this._map = null),
            (document.getElementById("wxStatusControl").style.display = "none"),
            this._options.overlay.close(this._controls.aqTypeControl);
    },
    redraw: function () {
        this._layer && ((this._redrawNoQuery = !0), this._layer.redraw());
    },
    _updateCanvas: function (e, t) {
        var i = t.options._context;
        i._canvasUtils.clearCanvas(t), i._redrawNoQuery ? (i._drawCanvas(e, t), (i._redrawNoQuery = !1)) : (i._ajaxStations && (i._ajaxStations.abort(), (i._ajaxStations = null)), i._getStationLocations(e, t));
    },
    _getStationLocations: function (e, t) {
        var i = t.options._context;
        document.getElementById("wxStatusControl").style.display = "block";
        var a = new Spinner({ left: "15px", scale: 0.5 }).spin(document.getElementById("wxSpinner")),
            r = i._map.getBounds(),
            n = Constants.urls.pylaski + "stations?selection=boundingBox&minLat=" + r.getSouth() + "&maxLat=" + r.getNorth() + "&minLon=" + r.getWest() + "&maxLon=" + r.getEast() + "&camera=false&obsgroup=airq&observables=any";
        i._ajaxStations = $.ajax({ url: n, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "aqStations", timeout: 1e4 })
            .always(function () {
                (i._ajaxStations = null), a.stop();
            })
            .fail(function (e, t) {
                "abort" !== t && alert("Error retrieving measurements: " + t);
            })
            .done(function (a) {
                (i._stations = a), i._drawCanvas(e, t);
            });
    },
    _drawCanvas: function (e, t) {
        var i,
            a,
            r = t.options._context,
            n = r._map.getZoom(),
            s = r._controls.aqTypeSlider.noUiSlider.get(),
            o = r._aqTypes[s];
        r._canvasUtils.clearCanvas(t);
        var l = r._map.getCenter(),
            d = r._map.latLngToContainerPoint(l),
            m = d.clone();
        if (((m.x += r._canvasUtils.wxStationRadius), (r._minStationCircleDist = d.distanceTo(m) + 8), r._stations && r._stations.hasOwnProperty("features")))
            for (var c in r._stations.features) {
                var u = r._stations.features[c];
                if ((u.geometry.hasOwnProperty("centerPoint") || (u.geometry.centerPoint = r._map.latLngToContainerPoint(L.latLng([u.geometry.coordinates[1], u.geometry.coordinates[0]]))), u.properties.hasOwnProperty(o.obs)))
                    if ((i = u.properties[o.obs]).hasOwnProperty("units"))
                        if (u.properties[o.obs].units != o.units) console.log("units mismatch: expecting " + o.units + ", but received:" + i.units);
                        else {
                            var h = { ctx: t.canvas.getContext("2d"), center: u.geometry.centerPoint, erase: !1 };
                            n < r._minStationZoom && (h.scale = 1 + 0.5 * (r._minStationZoom - n)),
                                u.properties.description.name === r._selectedStation && (h.width = 7),
                                r._canvasUtils.drawCloud(h),
                                (h.v = null),
                                (h.color = { bg: "white" }),
                                (a = i.value),
                                n < r._minStationZoom ? (h.v = null) : ((h.v = a), h.v.length > 4 && (h.v = h.v.substring(0, 4))),
                                a > o.max && (a = o.max),
                                (h.color = r._canvasUtils.airQualityColor((100 * a) / o.max)),
                                r._canvasUtils.drawFloatValue(h);
                        }
                    else console.log("missing units for " + o.obs);
            }
    },
    _clickStation: function (e) {
        var t = this._utils.getClosestStation(this._stations, e, this._minStationCircleDist);
        t &&
            t.hasOwnProperty("properties") &&
            t.properties.hasOwnProperty("description") &&
            ((this._selectedStation = t.properties.description.name), this.redraw(), this._ajaxStationData && (this._ajaxStationData.abort(), (this._ajaxStationData = null)), this._getStationData(t));
    },
    _closeChart: function (e) {
        "aqChartControl" === e.id && ((this._selectedStation = null), this.redraw());
    },
    _getStationData: function (e) {
        var t = this,
            i = e.properties.description.name;
        e.properties.description.owner && (i += " (" + e.properties.description.owner + ")"), (document.getElementById("aqTitle").innerHTML = i);
        var a = new Spinner().spin(),
            r = t._utils.initChart("aqPMChart", t),
            n = t._utils.initChart("aqNO2SO2Chart", t),
            s = t._utils.initChart("aqO3COChart", t);
        this._options.overlay.isShown(this._controls.aqChartControl) || (this._options.overlay.show(this._controls.aqChartControl), this.resizeCharts()),
            r.appendChild(a.el),
            (t._ajaxStationData = $.ajax({
                url:
                    Constants.urls.pylaski +
                    "stations/data?selection=closestTo&lat=" +
                    e.geometry.coordinates[1] +
                    "&lon=" +
                    e.geometry.coordinates[0] +
                    "&obsgroup=airq&from=" +
                    moment().subtract(1, "day").format("YYYY-MM-DDTHH:mm:ssZ") +
                    "&to=" +
                    moment().format("YYYY-MM-DDTHH:mm:ssZ"),
                type: "GET",
                dataType: "jsonp",
                jsonp: "callback",
                jsonpCallback: "aqData",
                timeout: 3e4,
            })
                .always(function () {
                    t._ajaxStationData, a.stop();
                })
                .fail(function (e, t) {
                    "abort" !== t && (r.innerHTML = '<div style="text-align:center;">Error retrieving measurements: ' + t + ".</div>");
                })
                .done(function (e) {
                    if (e.hasOwnProperty("features")) {
                        if (e.features.length > 0) {
                            var i = e.features[0];
                            if (i.hasOwnProperty("properties")) {
                                var a,
                                    o,
                                    l = i.properties,
                                    d = l.timestamp,
                                    m = [l.pm_2_5, l.pm_10, l.nitrogen_dioxide, l.sulfur_dioxide, l.ozone, l.carbon_monoxide, l.black_carbon],
                                    c = [[], [], [], [], [], [], []];
                                for (a in d) {
                                    var u = moment(d[a]).valueOf();
                                    for (o in c) m[o] && !isNaN(m[o][a]) && c[o].push([u, m[o][a]]);
                                }
                                var h = [];
                                (t._shownCharts = []),
                                    (c[0].length || c[1].length) && t._shownCharts.push("aqPMChart"),
                                    (c[2].length || c[3].length) && t._shownCharts.push("aqNO2SO2Chart"),
                                    (c[4].length || c[5].length) && t._shownCharts.push("aqO3COChart");
                                var p = t._utils.getChartHeight("aqTitle", t._shownCharts.length, 3, 20);
                                m[0] || m[1]
                                    ? ((h = []),
                                      m[0] && h.push({ title: "PM 2.5", units: t._aqTypes["PM2.5"].units, values: c[0], color: "blue" }),
                                      m[1] && h.push({ title: "PM 10", units: t._aqTypes.PM10.units, values: c[1], color: "green" }),
                                      (r.style.height = p),
                                      t._utils.showChart(h, { id: "aqPMChart", title: "Particulate Matter" }))
                                    : (r.innerHTML = '<div style="text-align:center;">No particulate matter measurements.</div>'),
                                    m[2] || m[3]
                                        ? ((h = []),
                                          m[2] && h.push({ title: "Nitrogen Dioxide", units: t._aqTypes.NO2.units, values: c[2], color: "blue" }),
                                          m[3] && h.push({ title: "Sulfur Dioxide", units: t._aqTypes.SO2.units, values: c[3], color: "green" }),
                                          (n.style.height = p),
                                          t._utils.showChart(h, { id: "aqNO2SO2Chart", title: "Nitrogen Dioxide and Sulfur Dioxide" }))
                                        : (n.innerHTML = '<div style="text-align:center;">No NO2 or SO2 measurements.</div>'),
                                    m[4] || m[5]
                                        ? ((h = []),
                                          m[4] && h.push({ title: "Ozone", units: t._aqTypes.Ozone.units, values: c[4], color: "blue" }),
                                          m[5] && h.push({ title: "Carbon Monoxide", units: t._aqTypes.CO.units, values: c[5], color: "green" }),
                                          (s.style.height = p),
                                          t._utils.showChart(h, { id: "aqO3COChart", title: "Ozone and Carbon Monoxide" }))
                                        : (s.innerHTML = '<div style="text-align:center;">No ozone or carbon monoxide measurements.</div>');
                            }
                        }
                        t.resizeCharts();
                    } else r.innerHTML = '<div style="text-align:center;">No measurements found.</div>';
                }));
    },
    resizeCharts: function () {
        var e = document.getElementById("aqTitle"),
            t = document.getElementById("aqPMChart"),
            a = document.getElementById("aqNO2SO2Chart"),
            r = document.getElementById("aqO3COChart"),
            n = document.getElementById("aqChartControl"),
            s = this._utils.getChartHeight("aqTitle", this._shownCharts.length, 3, 20);
        for (i in ((windowWidth = window.innerWidth - 20),
        (newWidth = windowWidth < Constants.chartWidth.max ? windowWidth : Constants.chartWidth.max),
        i,
        (newWidth = n.offsetWidth < newWidth ? n.offsetWidth : newWidth),
        (e.style.width = t.style.width = a.style.width = r.style.width = newWidth + "px"),
        this._shownCharts))
            document.getElementById(this._shownCharts[i]).style.height = s + "px";
    },
};
var HistoricalFires = function (e) {
    var t = this,
        i = new Date().getFullYear();
    (this._options = e),
        (this._hFires = e.hFires || { minYr: 2006, maxYr: i, minAc: 1e3, maxAc: 6e5 }),
        (this._histFiresYearSlider = e.utils.createSlider({
            id: "histFiresYear",
            start: [this._hFires.minYr, this._hFires.maxYr],
            step: 1,
            min: 1878,
            max: i,
            textId: ["startYearVal", "endYearVal"],
            range: { min: 1878, "50%": 1990, max: i },
        })),
        this._histFiresYearSlider.noUiSlider.on("set", function () {
            t._updateFiresLayer();
        }),
        (this._histFiresAcreSlider = e.utils.createSlider({ id: "histFiresAcre", start: [this._hFires.minAc, this._hFires.maxAc], step: 1e3, min: 0, max: 6e5, textId: ["startAcreVal", "endAcreVal"], range: { min: 0, max: 6e5 } })),
        this._histFiresAcreSlider.noUiSlider.on("set", function () {
            t._updateFiresLayer();
        }),
        (this._cause_codes = [
            "Lightning",
            "Equipment Use",
            "Smoking",
            "Campfire",
            "Debris",
            "Railroad",
            "Arson",
            "Playing with Fire",
            "Miscellaneous",
            "Vehicle",
            "Power Line",
            "Firefighter Training",
            "Non-Firefighter Training",
            "Unknown/Unidentified",
            "Structure",
            "Aircraft",
            "Volcanic",
            "Escaped Prescribed Burn",
            "Illegal Alien Campfire",
        ]),
        (this._layer = L.tileLayer.betterWms(e.wmsURL || Constants.urls.wms, {
            layers: "WIFIRE:view_historical_fires",
            format: "image/png8",
            transparent: !0,
            version: "1.1.0",
            attribution: 'Historical Fires Courtesy of <a href="http://www.geomac.gov">GeoMAC</a> and <a href="http://frap.cdf.ca.gov/">CAL FIRE</a>',
            jsonpCallback: "getJsonHistFires",
            cql_filter: "year between " + this._hFires.minYr + " and " + this._hFires.maxYr + " and acres between " + this._hFires.minAc + " and " + this._hFires.maxAc,
            zIndex: e.zIndex || Constants.zLayers.histFire,
            title: function (e) {
                var t = (e.fire_name || "Unknown") + " (" + e.year + ")";
                return delete e.fire_name, t;
            },
            updateProperties: function (e, i) {
                var a;
                (e.acres && (e.acres = e.acres.toFixed(0)), e.cause && (e.cause = t._cause_codes[e.cause - 1]), e.inciwebid && (e.inciwebid = "https://inciweb.nwcg.gov/incident/" + e.inciwebid), e.year >= 2001 && e.acres >= 2e4) &&
                    (e.perimeter_timestamp ? (a = e.perimeter_timestamp) : e.alarm_date ? (a = e.alarm_date) : console.log("WARNING: unknown date for fire."),
                    a && (e._FOOTER = '<button class="fireButton" id="gibsFireButton" onclick="firemap.showNASAGIBS(\'' + a + "', " + i.latlng.lat + ", " + i.latlng.lng + ')">Satellite Imagery</button>'));
                delete e.year;
            },
            boldNames: ["acres"],
            detectRetina: e.hasOwnProperty("retina") ? e.retina : Constants.retina,
        }));
};
HistoricalFires.prototype = {
    onAdd: function (e) {
        (this._map = e), this._layer.onAdd(e), this._options.overlay.show("historicalFiresControl");
    },
    onRemove: function (e) {
        this._layer.onRemove(e), (this._map = null), this._options.overlay.close("historicalFiresControl");
    },
    setOpacity: function (e) {
        this._layer.setOpacity(e);
    },
    _updateFiresLayer: function () {
        var e = this._histFiresYearSlider.noUiSlider.get(),
            t = this._histFiresAcreSlider.noUiSlider.get();
        this._layer.setParams({ cql_filter: "year between " + e[0] + " and " + e[1] + "and acres between " + t[0] + " and " + t[1] });
    },
};
var LandfireFuel = function (e) {
    var t = this;
    (this._options = e),
        (this._fuelModelNames = [
            "",
            "Short Grass",
            "Timber Grass",
            "Tall Grass",
            "Chaparral",
            "Brush",
            "Dormant Brush",
            "Southern Rough",
            "Compact Timber Litter",
            "Hardwood Litter",
            "Timber Understory",
            "Light Slash",
            "Medium Slash",
            "Heavy Slash",
        ]),
        (this._fuelModelNames[91] = "Urban"),
        (this._fuelModelNames[92] = "Snow/Ice"),
        (this._fuelModelNames[93] = "Agricultural"),
        (this._fuelModelNames[98] = "Water"),
        (this._fuelModelNames[99] = "Barren or No Data"),
        (this._layer = L.tileLayer.betterWms(Constants.urls.wms, {
            layers: "WIFIRE:conus-fuel-" + (e.year || 2014),
            jsonpCallback: "getJsonSurfaceFuel",
            format: "image/png8",
            transparent: !0,
            version: "1.1.0",
            attribution: 'Surface Fuels Courtesy of <a href="http://landfire.gov">USGS Landfire Program</a>',
            zIndex: e.zIndex || Constants.zLayers.surfaceFuel,
            detectRetina: e.hasOwnProperty("retina") ? e.retina : Constants.retina,
            title: "Surface Fuel",
            tiled: !0,
            updateProperties: function (e, i) {
                (e["FM" + e.GRAY_INDEX] = t._fuelModelNames[e.GRAY_INDEX]),
                    delete e.GRAY_INDEX,
                    (e._FOOTER = '<a target="_blank" href="fuel-vegtype.html?z=' + t._map.getZoom() + "&c=" + i.latlng.lat + "," + i.latlng.lng + '">Compare to vegetation types.</a>');
            },
        }));
};
LandfireFuel.prototype = {
    onAdd: function (e) {
        (this._map = e), this._layer.onAdd(e), this._options.overlay.show("fuelLegend");
    },
    onRemove: function (e) {
        this._layer.onRemove(e), (this._map = null), this._options.overlay.close("fuelLegend");
    },
    setOpacity: function (e) {
        this._layer.setOpacity(e);
    },
};
var LandfireVegetation = function (e) {
    var t = this;
    e || (e = {}),
        (this._options = e),
        (this._layer = L.tileLayer.betterWms(Constants.urls.wms, {
            layers: "WIFIRE:conus-evt-" + (e.year || 2014),
            jsonpCallback: "getJsonEvt",
            format: "image/png8",
            transparent: !0,
            version: "1.1.0",
            attribution: 'Vegetation Type Courtesy of <a href="http://landfire.gov">USGS Landfire Program</a>',
            zIndex: Constants.zLayers.vegetationType,
            detectRetina: e.hasOwnProperty("retina") ? e.retina : Constants.retina,
            title: "Vegetation Type",
            tiled: !0,
            updateProperties: function (e, i) {
                (e[e.GRAY_INDEX] = t._vegetationTypes[e.GRAY_INDEX] || e.GRAY_INDEX),
                    delete e.GRAY_INDEX,
                    (e._FOOTER = '<a target="_blank" href="fuel-vegtype.html?z=' + t._map.getZoom() + "&c=" + i.latlng.lat + "," + i.latlng.lng + '">Compare to surface fuels.</a>');
            },
        }));
};
LandfireVegetation.prototype = {
    onAdd: function (e) {
        var t = this;
        (this._map = e),
            this._layer.onAdd(e),
            $.ajax("/lib/data/evt.json")
                .fail(function (e, t) {
                    console.log("Error retrieving vegetation types: " + e + " " + t);
                })
                .done(function (e) {
                    t._vegetationTypes = e;
                });
    },
    onRemove: function (e) {
        this._layer.onRemove(e), (this._map = null), (this._vegetationTypes = null);
    },
    setOpacity: function (e) {
        this._layer.setOpacity(e);
    },
};
var SatelliteDetections = function (e) {
    (this._canvasUtils = new CanvasUtils()),
        (this._utils = new Utils()),
        (this._overlay = e.overlay),
        (e._context = this),
        (this._layer = L.canvasOverlay(this._drawCanvasSingleColor, e)),
        (this._const = { twelveHours: 43200, oneDay: 86400, twoDays: 172800, threeDays: 259200, fourDays: 345600, sevenDays: 604800 }),
        (this._maxFeatures = 3e4),
        (this._minModisConfidence = 70),
        (this._wfsTimeout = 6e4),
        (this._textBoxTimestampFormat = "YYYY-MM-DD"),
        (this._statusTimestampFormat = "YYYY-MM-DD HH:mm:ss");
    var t,
        i,
        a = [
            { name: "" },
            { name: "Santa Rosa, CA, 2017", start: moment("2017-10-08", this._textBoxTimestampFormat), stop: moment("2017-10-25", this._textBoxTimestampFormat), center: [38.48692, -122.62141], zoom: 9 },
            { name: "Blue Cut, CA, 2016", start: moment("2016-08-16", this._textBoxTimestampFormat), stop: moment("2016-08-23", this._textBoxTimestampFormat), center: [34.31409, -117.47646], zoom: 12 },
            { name: "Pioneer, ID, 2016", start: moment("2016-07-16", this._textBoxTimestampFormat), stop: moment("2016-09-22", this._textBoxTimestampFormat), center: [44.07081, -115.67093], zoom: 10, speed: 3 },
            { name: "Rey, CA, 2016", start: moment("2016-08-17", this._textBoxTimestampFormat), stop: moment("2016-09-01", this._textBoxTimestampFormat), center: [34.58673, -119.72488], zoom: 12 },
            { name: "Sand, CA, 2016", start: moment("2016-07-22", this._textBoxTimestampFormat), stop: moment("2016-08-01", this._textBoxTimestampFormat), center: [34.3501, -118.34713], zoom: 12 },
            { name: "Soberanes, CA, 2016", start: moment("2016-07-22", this._textBoxTimestampFormat), stop: moment("2016-09-30", this._textBoxTimestampFormat), center: [36.28884, -121.69006], zoom: 11, speed: 6 },
            { name: "Okonogan Complex, WA, 2015", start: moment("2015-08-14", this._textBoxTimestampFormat), stop: moment("2015-09-30", this._textBoxTimestampFormat), center: [48.39091, -119.24561], zoom: 8, speed: 12 },
            { name: "River Complex, CA, 2015", start: moment("2015-07-30", this._textBoxTimestampFormat), stop: moment("2015-11-01", this._textBoxTimestampFormat), center: [40.59414, -123.28857], zoom: 9, speed: 12 },
            { name: "Rough, CA, 2015", start: moment("2015-07-30", this._textBoxTimestampFormat), stop: moment("2015-11-07", this._textBoxTimestampFormat), center: [36.82413, -118.86108], zoom: 10, speed: 12 },
            { name: "Happy Camp Complex, CA, 2014", start: moment("2014-08-13", this._textBoxTimestampFormat), stop: moment("2014-11-01", this._textBoxTimestampFormat), center: [41.59131, -123.03589], zoom: 10, speed: 6 },
            { name: "San Diego Firestorm, CA, 2014", start: moment("2014-05-09", this._textBoxTimestampFormat), stop: moment("2014-05-20", this._textBoxTimestampFormat), center: [33.25276, -117.27013], zoom: 11 },
            { name: "2015-present", start: moment("2015-01-01", this._textBoxTimestampFormat), stop: moment(), speed: 24 },
        ],
        r = this,
        n = document.getElementById("animFire");
    for (t in a) ((i = document.createElement("option")).value = i.innerHTML = a[t].name), n.appendChild(i);
    (n.onchange = function () {
        var e, t;
        for (e in a)
            a[e].name === this.value &&
                ((t = a[e]),
                (document.getElementById("animStart").value = t.start.format(r._textBoxTimestampFormat)),
                (document.getElementById("animStop").value = t.stop.format(r._textBoxTimestampFormat)),
                (document.getElementById("animSpeed").value = t.speed || 1),
                r._map && r._map.panTo(t.center).setZoom(t.zoom));
    }),
        (document.getElementById("animDownloadButton").disabled = document.getElementById("animBackwardButton").disabled = document.getElementById("animPlayButton").disabled = document.getElementById(
            "animStopButton"
        ).disabled = document.getElementById("animForwardButton").disabled = !0),
        L.DomEvent.addListener(document.getElementById("animDownloadButton"), "click", this.download, this),
        L.DomEvent.addListener(document.getElementById("animBackwardButton"), "click", this.stepBackward, this),
        L.DomEvent.addListener(document.getElementById("animPlayButton"), "click", this.play, this),
        L.DomEvent.addListener(document.getElementById("animStopButton"), "click", this.stop, this),
        L.DomEvent.addListener(document.getElementById("animForwardButton"), "click", this.stepForward, this),
        L.DomEvent.addListener(document.getElementById("animStart"), "change", this._inputsChanged, this),
        L.DomEvent.addListener(document.getElementById("animStop"), "change", this._inputsChanged, this),
        L.DomEvent.addListener(document.getElementById("animSpeed"), "change", this._inputsChanged, this),
        L.DomEvent.addListener(document.getElementById("animStart"), "keyup", this._inputsChanged, this),
        L.DomEvent.addListener(document.getElementById("animStop"), "keyup", this._inputsChanged, this),
        L.DomEvent.addListener(document.getElementById("animSpeed"), "keyup", this._inputsChanged, this),
        (this._off = document.createElement("canvas")),
        (this._slider = r._utils.createSlider({ id: "satAnimSlider", start: 0, step: 1, min: 0, max: 100 }));
};
SatelliteDetections.prototype = {
    onAdd: function (e) {
        (this._map = e), this._layer.onAdd(e), this._overlay.show("animControl");
        var t = this;
        e.on("moveend", function (e) {
            t._calculateSize(), t._calculateCenters(), (document.getElementById("animDownloadButton").disabled = !1);
        }),
            this._inputsChanged();
    },
    onRemove: function (e) {
        this._animId && cancelAnimFrame(this._animId),
            this._overlay.close("animControl"),
            this._map.eachLayer(function (e) {
                e !== this && e.setLayerTime && e.setLayerTime(null);
            }),
            this._layer.onRemove(e),
            (this._map = null);
    },
    download: function () {
        var e = this,
            t = document.getElementById("animStatusText");
        this._layer.redraw(),
            (t.innerHTML = "Downloading"),
            (document.getElementById("animDownloadButton").disabled = !0),
            (this._start = moment(document.getElementById("animStart").value, this._textBoxTimestampFormat)),
            (this._stop = moment(document.getElementById("animStop").value, this._textBoxTimestampFormat)),
            (this._cur = null),
            (this._data = null),
            this._getModisData(this._start, this._stop, function () {
                console.log(e._data),
                    e._calculateCenters(),
                    e._slider && e._slider.noUiSlider.destroy(),
                    (e._slider = e._utils.createSlider({ id: "satAnimSlider", start: 0, step: 1, min: 0, max: e._stop.diff(e._start, "hours") })),
                    e._slider.noUiSlider.on("slide", function () {
                        var t;
                        e.settingLayerTime || ((t = moment(e._start).add(e._slider.noUiSlider.get(), "hours")), (e.settingLayerTime = !0), e.setLayerTime(t), (e.settingLayerTime = !1));
                    }),
                    e._slider.noUiSlider.on("set", function () {
                        var t;
                        e.settingLayerTime ||
                            ((t = moment(e._start).add(e._slider.noUiSlider.get(), "hours")),
                            moment().isDST() ? t.isDST() || t.subtract(1, "hours") : t.isDST() && t.add(1, "hours"),
                            e._map.eachLayer(function (i) {
                                i !== e && i.setLayerTime && i.setLayerTime(t);
                            }));
                    }),
                    (t.innerHTML = "Done"),
                    (document.getElementById("animPlayButton").disabled = document.getElementById("animForwardButton").disabled = !1),
                    (document.getElementById("animBackwardButton").disabled = !0);
            });
    },
    setLayerTime: function (e) {
        (this._cur = e),
            (document.getElementById("animStatusText").innerHTML = this._cur.format(this._statusTimestampFormat)),
            this._layer.redraw(),
            this._settingLayerTime || ((this._settingLayerTime = !0), this._slider.noUiSlider.set(this._cur.diff(this._start, "hours")), (this._settingLayerTime = !1)),
            this._cur.isSameOrBefore(this._start)
                ? (document.getElementById("animBackwardButton").disabled = !0)
                : this._cur.isSameOrAfter(this._stop)
                ? (document.getElementById("animForwardButton").disabled = !0)
                : (document.getElementById("animBackwardButton").disabled = document.getElementById("animForwardButton").disabled = !1);
    },
    play: function () {
        (document.getElementById("animPlayButton").disabled = document.getElementById("animBackwardButton").disabled = document.getElementById("animForwardButton").disabled = !0),
            (document.getElementById("animStopButton").disabled = !1),
            this._lockMap(),
            (this._inc = document.getElementById("animSpeed").value),
            (this._cur && !this._cur.isSameOrAfter(this._stop)) || (this._layer._canvas.getContext("2d").clearRect(0, 0, this._layer._canvas.width, this._layer._canvas.height), (this._cur = moment(this._start)), this._calculateSize()),
            (this._stopPlaying = !1),
            (this._dd = Date.now()),
            (this._animId = L.Util.requestAnimFrame(this._animate, this, !0, !1));
    },
    stop: function () {
        (this._stopPlaying = !0), this._unlockMap();
    },
    stepBackward: function () {
        var e = moment(this._cur).subtract(1, "hours");
        e.isSameOrBefore(this._start) && ((document.getElementById("animBackwardButton").disabled = !0), (e = moment(this._start))), this.setLayerTime(e);
    },
    stepForward: function () {
        var e = moment(this._cur || this._start).add(1, "hours");
        e.isSameOrAfter(this._stop) && ((document.getElementById("animForwardButton").disabled = document.getElementById("animPlayButton").disabled = !0), (this._cur = moment(e))),
            (document.getElementById("animBackwardButton").disabled = !1),
            this.setLayerTime(e);
    },
    _inputsChanged: function () {
        var e = document.getElementById("animStart").value,
            t = document.getElementById("animStop").value,
            i = document.getElementById("animSpeed").value,
            a = document.getElementById("animStatusText");
        (document.getElementById("animBackwardButton").disabled = document.getElementById("animPlayButton").disabled = document.getElementById("animForwardButton").disabled = !0),
            e
                ? t
                    ? i
                        ? e.match(/^\d{4}\-\d\d\-\d\d$/)
                            ? t.match(/^\d{4}\-\d\d\-\d\d$/)
                                ? i.match(/^\d+$/)
                                    ? ((a.innerHTML = "Ready to download."), (document.getElementById("animDownloadButton").disabled = !1))
                                    : (a.innerHTML = "Speed should be a number.")
                                : (a.innerHTML = "Stop date should be YYYY-MM-DD.")
                            : (a.innerHTML = "Start date should be YYYY-MM-DD.")
                        : (a.innerHTML = "Speed should be a number.")
                    : (a.innerHTML = "Stop date should be YYYY-MM-DD.")
                : (a.innerHTML = "Start date should be YYYY-MM-DD.");
    },
    _calculateCenters: function () {
        var e;
        if (this._data) for (e in this._data.features) this._data.features[e].center = this._map.latLngToContainerPoint(L.latLng(this._data.features[e].geometry.coordinates[1], this._data.features[e].geometry.coordinates[0]));
    },
    _calculateSize: function () {
        var e = (40075016.686 * Math.abs(Math.cos((this._map.getCenter().lat * Math.PI) / 180))) / Math.pow(2, this._map.getZoom() + 8);
        this._radius = 1e3 / e;
        var t = ["gold", "orangered", "red", "black", "gray"];
        (this._diameter = 2 * this._radius), (this._canvas = document.createElement("canvas")), (this._canvas.width = this._diameter * t.length), (this._canvas.height = this._diameter);
        var a = this._canvas.getContext("2d");
        for (i in t) (a.fillStyle = t[i]), a.beginPath(), a.arc(i * this._diameter + this._radius, this._radius, this._radius, 0, 2 * Math.PI), a.closePath(), a.fill();
    },
    _animate: function (e, t) {
        this._stopPlaying
            ? ((document.getElementById("animPlayButton").disabled = document.getElementById("animBackwardButton").disabled = document.getElementById("animForwardButton").disabled = !1),
              (document.getElementById("animStopButton").disabled = !0),
              (this._settingLayerTime = !0),
              this._slider.noUiSlider.set(this._cur.diff(this._start, "hours")),
              (this._settingLayerTime = !1),
              (this._animId = null),
              (this._drawStartIndex = null))
            : ((document.getElementById("animStatusText").innerHTML = this._cur.format(this._statusTimestampFormat)),
              this._layer._redraw(),
              (this._cur = this._cur.add(this._inc, "hours")),
              this._cur.isBefore(this._stop)
                  ? (this._animId = L.Util.requestAnimFrame(this._animate, this, !0, !1))
                  : (console.log(Date.now() - this._dd),
                    (this._animId = null),
                    (this._drawStartIndex = null),
                    (document.getElementById("animBackwardButton").disabled = document.getElementById("animPlayButton").disabled = !1),
                    (document.getElementById("animForwardButton").disabled = document.getElementById("animStopButton").disabled = !0),
                    (this._settingLayerTime = !0),
                    this._slider.noUiSlider.set(this._cur.diff(this._start, "hours")),
                    (this._settingLayerTime = !1),
                    this._unlockMap()));
    },
    _drawCanvasSingleColor: function (e, t) {
        var i = t.options._context;
        if (i._cur) {
            var a = i._drawStartIndex || 0;
            i._animId || (i._canvasUtils.clearCanvas(t), (a = 0));
            var r = t.canvas.getContext("2d"),
                n = i._cur.unix();
            i._radius;
            for (r.fillStyle = "red"; a < i._data.features.length; ) {
                var s = i._data.features[a];
                if (s.properties.epoch_time > n) break;
                r.fillRect(s.center.x, s.center.y, i._diameter, i._diameter), i._animId && (i._drawStartIndex = a), a++;
            }
        } else i._canvasUtils.clearCanvas(t);
    },
    _drawCanvas: function (e, t) {
        var i = t.options._context;
        if (i._cur) {
            var a = i._drawStartIndex || 0;
            i._animId || (i._canvasUtils.clearCanvas(t), (a = 0));
            var r = t.canvas.getContext("2d"),
                n = i._cur.unix();
            for (i._radius; a < i._data.features.length; ) {
                var s = i._data.features[a],
                    o = s.properties.epoch_time;
                if (o > n) break;
                r.beginPath(), r.arc(s.center.x, s.center.y, i._radius, 0, Constants.twoPI);
                var l = n - o;
                l < i._const.twelveHours
                    ? (r.fillStyle = "gold")
                    : l < i._const.oneDay
                    ? (r.fillStyle = "orangered")
                    : l < i._const.twoDays
                    ? (r.fillStyle = "red")
                    : l < i._const.threeDays
                    ? (r.fillStyle = "black")
                    : ((r.fillStyle = "gray"), i._animId && (i._drawStartIndex = a)),
                    r.fill(),
                    a++;
            }
        } else i._canvasUtils.clearCanvas(t);
    },
    _getModisData: function (e, t, i) {
        var a = this;
        this._getModisBefore2009(e, t, function () {
            a._getModisBetween2009_2016(e, t, function () {
                a._getModisAfter2016(e, t, i);
            });
        });
    },
    _getModisBefore2009: function (e, t, a) {
        var r = this,
            n =
                "https://firemap.sdsc.edu:8443/geoserver/WIFIRE/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=WIFIRE:modis_2001_2008&maxFeatures=" +
                this._maxFeatures +
                "&cql_filter=date > '" +
                e.format("M/D/YY") +
                " 12:00 AM'  and date < '" +
                t.format("M/D/YY") +
                " 12:00 AM' and bbox(geom, " +
                this._map.getBounds().toBBoxString() +
                ") and confidence >= " +
                this._minModisConfidence +
                "&sortBy=date&propertyname=geom,jdate,utc&outputFormat=text/javascript&format_options=callback:asdasd";
        e.isAfter("2008-12-31")
            ? a.apply(this)
            : $.ajax({ url: n, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "asdasd", timeout: this._wfsTimeout })
                  .fail(function (e, t) {
                      "abort" !== t && alert("Error retrieving satellite detections: " + t);
                  })
                  .done(function (e) {
                      var n;
                      for (i in e.features)
                          (n = moment(e.features[i].properties.jdate + " " + (e.features[i].properties.utc < 1e3 ? "0" + e.features[i].properties.utc : e.features[i].properties.utc), "YYYYDDD HHmm")),
                              (e.features[i].properties.epoch_time = n.unix());
                      r._data ? r._data.features.push.apply(r._data.features, e.features) : (r._data = e), !e.totalFeatures || e.totalFeatures < r._maxFeatures ? a.apply(r) : r._getModisBefore2009(n.clone(), t, a);
                  });
    },
    _getModisBetween2009_2016: function (e, t, a) {
        var r = this,
            n =
                "https://firemap.sdsc.edu:8443/geoserver/WIFIRE/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=WIFIRE:modis_2009_2016&maxFeatures=" +
                this._maxFeatures +
                "&cql_filter=date > '" +
                e.format("M/D/YY") +
                " 12:00 AM'  and date < '" +
                t.format("M/D/YY") +
                " 12:00 AM' and bbox(geom, " +
                this._map.getBounds().toBBoxString() +
                ") and conf >= " +
                this._minModisConfidence +
                "&sortBy=date&propertyname=geom,date,gmt&outputFormat=text/javascript&format_options=callback:asdasd";
        e.isAfter("2016-12-31") || t.isBefore("2009-01-01")
            ? a.apply(this)
            : $.ajax({ url: n, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "asdasd", timeout: this._wfsTimeout })
                  .fail(function (e, t) {
                      "abort" !== t && alert("Error retrieving satellite detections: " + t);
                  })
                  .done(function (e) {
                      var n;
                      for (i in e.features)
                          (n = moment(e.features[i].properties.date + (e.features[i].properties.gmt < 1e3 ? "0" : " ") + e.features[i].properties.gmt, "YYYY-MM-DD[Z] HHmm")), (e.features[i].properties.epoch_time = n.unix());
                      r._data ? r._data.features.push.apply(r._data.features, e.features) : (r._data = e), !e.totalFeatures || e.totalFeatures < r._maxFeatures ? a.apply(r) : r._getModisBetween2009_2016(n.clone(), t, a);
                  });
    },
    _getModisAfter2016: function (e, t, i) {
        var a = this,
            r = e.isBefore("2017-01-01") ? moment("2017-01-01") : e,
            n =
                "https://firemap.sdsc.edu:8443/geoserver/WIFIRE/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=WIFIRE:view_modis_c6&maxFeatures=" +
                this._maxFeatures +
                "&cql_filter=epoch_time > " +
                r.unix() +
                "  and epoch_time < " +
                t.unix() +
                " and bbox(location, " +
                this._map.getBounds().toBBoxString() +
                ") and confidence >= " +
                this._minModisConfidence +
                "&sortBy=epoch_time&propertyname=location,epoch_time&outputFormat=text/javascript&format_options=callback:asdasd";
        t.isBefore("2017-01-01")
            ? i.apply(this)
            : $.ajax({ url: n, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "asdasd", timeout: this._wfsTimeout })
                  .fail(function (e, t) {
                      "abort" !== t && alert("Error retrieving satellite detections: " + t);
                  })
                  .done(function (e) {
                      a._data ? a._data.features.push.apply(a._data.features, e.features) : (a._data = e),
                          !e.totalFeatures || e.totalFeatures < a._maxFeatures ? i.apply(a) : a._getModisAfter2016(moment.unix(e.features[e.features.length - 1].properties.epoch_time), t, i);
                  });
    },
    _getViirsData: function (e, t, i) {
        var a = this;
        t.year() < 2017
            ? this._getViirsDataBefore2017(e, t, i)
            : e.year() >= 2017
            ? this._getViirsDataAfter2017(e, t, i)
            : this._getViirsDataBefore2017(e, moment("2016-12-31"), function () {
                  a._getViirsDataAfter2017(moment("2017-01-01"), t, i);
              });
    },
    _getViirsDataAfter2017: function (e, t, i) {
        var a = this,
            r =
                "https://firemap.sdsc.edu:8443/geoserver/WIFIRE/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=WIFIRE:view_viirs_iband&maxFeatures=" +
                this._maxFeatures +
                "&cql_filter=acq_date > '" +
                e.format("M/D/YY") +
                " 12:00 AM'  and acq_date < '" +
                t.format("M/D/YY") +
                " 12:00 AM' and bbox(location, " +
                this._map.getBounds().toBBoxString() +
                ")&sortBy=epoch_time&propertyname=location,epoch_time&outputFormat=text/javascript&format_options=callback:asdasd";
        $.ajax({ url: r, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "asdasd", timeout: this._wfsTimeout })
            .fail(function (e, t) {
                "abort" !== t && alert("Error retrieving satellite detections: " + t);
            })
            .done(function (e) {
                a._data ? a._data.features.push.apply(a._data.features, e.features) : (a._data = e),
                    !e.totalFeatures || e.totalFeatures < a._maxFeatures ? i.apply(a) : a._getViirsData(moment.unix(e.features[e.features.length - 1].properties.epoch_time), t, i);
            });
    },
    _getViirsDataBefore2017: function (e, t, a) {
        var r = this,
            n =
                "https://firemap.sdsc.edu:8443/geoserver/WIFIRE/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=WIFIRE:viirs_iband_cumulative&maxFeatures=" +
                this._maxFeatures +
                "&cql_filter=date > '" +
                e.format("M/D/YY") +
                " 12:00 AM'  and date < '" +
                t.format("M/D/YY") +
                " 12:00 AM' and bbox(geom, " +
                this._map.getBounds().toBBoxString() +
                ")&sortBy=date&propertyname=geom,date,gmt&outputFormat=text/javascript&format_options=callback:asdasd";
        $.ajax({ url: n, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "asdasd", timeout: this._wfsTimeout })
            .fail(function (e, t) {
                "abort" !== t && alert("Error retrieving satellite detections: " + t);
            })
            .done(function (e) {
                var n;
                for (i in e.features) (n = moment(e.features[i].properties.date + (e.features[i].properties.gmt < 1e3 ? "0" : " ") + e.features[i].properties.gmt, "YYYY-MM-DD[Z] HHmm")), (e.features[i].properties.epoch_time = n.unix());
                r._data ? r._data.features.push.apply(r._data.features, e.features) : (r._data = e), !e.totalFeatures || e.totalFeatures < r._maxFeatures ? a.apply(r) : r._getViirsData(n.clone(), t, a);
            });
    },
    _lockMap: function () {
        this._map.dragging.disable(),
            this._map.touchZoom.disable(),
            this._map.doubleClickZoom.disable(),
            this._map.scrollWheelZoom.disable(),
            this._map.boxZoom.disable(),
            this._map.keyboard.disable(),
            this._map.tab && this._map.tap.disable(),
            (document.getElementById("map").style.cursor = "default"),
            this._slider.setAttribute("disabled", !0);
    },
    _unlockMap: function () {
        this._map.dragging.enable(),
            this._map.touchZoom.enable(),
            this._map.doubleClickZoom.enable(),
            this._map.scrollWheelZoom.enable(),
            this._map.boxZoom.enable(),
            this._map.keyboard.enable(),
            this._map.tap && this._map.tap.enable(),
            (document.getElementById("map").style.cursor = " grab"),
            this._slider.removeAttribute("disabled");
    },
};
var GOESGeoColor = function (e) {
    (this._overlay = e.overlay),
        (this._url = "https://words-geo-www.nautilus.optiputer.net/GOES16-ABI-CONUS-GEOCOLOR/latest/"),
        (this._layer = L.tileLayer(this._url + "tiles/{z}/{x}/{y}.png", {
            tms: !0,
            maxZoom: 9,
            attribution: '<a href="https://www.star.nesdis.noaa.gov/star/index.php" target="_blank">NOAA NESDIS STAR</a>, <a href="https://www.cira.colostate.edu" target="_blank">CIRA</a>',
        }));
};
GOESGeoColor.prototype = {
    onAdd: function (e) {
        var t = this;
        (this._map = e),
            e.addLayer(this._layer),
            this._timer && window.clearInterval(this._timer),
            (this._timer = window.setInterval(function () {
                console.log("redraw"), t._layer.redraw(), t._checkZoom();
            }, 3e5)),
            e.on("zoomend", this._checkZoom, this),
            this._checkZoom(),
            this._overlay.show("goesGeoColor");
    },
    onRemove: function (e) {
        this._timer && (window.clearInterval(this._timer), (this._timer = null)), this._overlay.close("goesGeoColor"), e.off("zoomend", this._checkZoom, this), this._layer.onRemove(e);
    },
    _checkZoom: function () {
        this._map.getZoom() <= 8
            ? ((document.getElementById("goesGeoColorTitle").innerHTML = "GOES GeoColor"), this._getLastUpdate())
            : ((document.getElementById("goesGeoColorTitle").innerHTML = "GOES GeoColor: Zoom out"), (document.getElementById("goesGeoColorText").style.color = "lightgray"));
    },
    _getLastUpdate: function () {
        var e = this;
        $.ajax(this._url + "metadata.json", { dataType: "json" })
            .fail(function (e, t) {
                console.log("error getting goes geocolor metadata: " + t);
            })
            .done(function (t) {
                e._map.getZoom() <= 8 &&
                    ((document.getElementById("goesGeoColorText").style.color = "black"),
                    t.timestamp
                        ? (document.getElementById("goesGeoColorText").innerHTML = "Last update: " + moment.utc(t.timestamp, "YYYYDDDHHmm").tz(Constants.tz).format("YYYY-MM-DD HH:mm z"))
                        : (document.getElementById("goesGeoColorText").innerHTML = "Pending"));
            });
    },
};
var NASAGIBS = function (e) {
    var t = this;
    (this._options = e),
        (this._MOMENT_FORMAT = "YYYY-MM-DD"),
        (this._FLATPICKR_FORMAT = "Y-m-d"),
        (this._firstDateMODIS = new Date("February 24, 2000")),
        (this._firstDateVIIRS = new Date("November 24, 2015")),
        (this._template = "https://gibs-{s}.earthdata.nasa.gov/wmts/epsg3857/all/{layer}/default/{time}/{tileMatrixSet}/{z}/{y}/{x}.jpg"),
        (this._timeVal = moment().subtract(1, "day").format(this._MOMENT_FORMAT)),
        (this._time = document.getElementById("gibsTimeVal").flatpickr({
            disableMobile: !0,
            dateFormat: this._FLATPICKR_FORMAT,
            defaultDate: this._timeVal,
            enableTime: !1,
            maxDate: new Date(),
            minDate: this._firstDateMODIS,
            onValueUpdate: function (e, i, a) {
                (t._timeVal = i), t._updateLayer();
            },
        })),
        L.DomEvent.addListener(document.getElementById("gibsBackwardButton"), "click", this._stepBackward, this),
        L.DomEvent.addListener(document.getElementById("gibsForwardButton"), "click", this._stepForward, this);
    var i,
        a = document.getElementById("gibsProduct"),
        r = {
            "SNPP VIIRS M11-I2-I1": "VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1",
            "SNPP VIIRS M3-I3-M11": "VIIRS_SNPP_CorrectedReflectance_BandsM3-I3-M11",
            "SNPP VIIRS True Color": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
            "Terra MODIS Corrected 7-2-1": "MODIS_Terra_CorrectedReflectance_Bands721",
            "Terra MODIS Corrected 3-6-7": "MODIS_Terra_CorrectedReflectance_Bands367",
            "Terra MODIS True Color": "MODIS_Terra_CorrectedReflectance_TrueColor",
        };
    for (i in r) (o = document.createElement("option")), (o.innerHTML = i), (o.value = r[i]), a.add(o);
    (a.selectedIndex = 0),
        (a.onchange = function () {
            t._updateLayer();
        });
};
NASAGIBS.prototype = {
    onAdd: function (e) {
        (this._map = e), this._map.on("zoomend", this._checkZoom, this), this._updateLayer(), this._map.addLayer(this._layer), this._options.overlay.show("gibsControl");
    },
    onRemove: function (e) {
        this._options.overlay.close("gibsControl"), this._layer.onRemove(e), (this._layer = null), this._map.off("zoomend", this._checkZoom, this), (this._map = null);
    },
    setDate: function (e) {
        this._time.setDate(e), e.getTime() < this._firstDateVIIRS.getTime() && document.getElementById("gibsProduct").selectedIndex < 3 && (document.getElementById("gibsProduct").selectedIndex = 3), this._updateLayer();
    },
    setOpacity: function (e) {
        this._layer.setOpacity(e);
    },
    _checkZoom: function (e) {
        this._map.getZoom() <= 9
            ? ((document.getElementById("gibsTitle").innerHTML = "NASA GIBS"),
              (document.getElementById("gibsBackwardButton").disabled = document.getElementById("gibsForwardButton").disabled = document.getElementById("gibsTimeVal").disabled = document.getElementById("gibsProduct").disabled = !1))
            : ((document.getElementById("gibsTitle").innerHTML = "NASA GIBS: Zoom out"),
              (document.getElementById("gibsBackwardButton").disabled = document.getElementById("gibsForwardButton").disabled = document.getElementById("gibsTimeVal").disabled = document.getElementById("gibsProduct").disabled = !0));
    },
    _stepBackward: function () {
        this._time.setDate(moment(this._timeVal, this._MOMENT_FORMAT).subtract(1, "day").toDate());
    },
    _stepForward: function () {
        this._time.setDate(moment(this._timeVal, this._MOMENT_FORMAT).add(1, "day").toDate());
    },
    _updateLayer: function () {
        var e = !1;
        this._layer && this._map.hasLayer(this._layer) && (this._map.removeLayer(this._layer), (e = !0)),
            (this._layer = L.tileLayer(this._template, {
                layer: document.getElementById("gibsProduct").value,
                tileMatrixSet: "GoogleMapsCompatible_Level9",
                maxZoom: 9,
                time: this._timeVal,
                tileSize: 256,
                subdomains: "abc",
                noWrap: !0,
                continuousWorld: !0,
                bounds: [
                    [-85.0511287776, -179.999999975],
                    [85.0511287776, 179.999999975],
                ],
            })),
            this._checkZoom(),
            e && this._map.addLayer(this._layer);
    },
};
var UserMetadataLayers = function () {
    this._layers = {
        "Electric Power Transmission Lines": {
            updateProperties: function (e) {
                delete e.id, delete e.objectid, delete e.shape__len;
            },
        },
        "EMS Stations": {
            updateProperties: function (e) {
                delete e.geolinkid, delete e.id, delete e.x, delete e.y;
            },
        },
        "Evacuation Shelters": {
            updateProperties: function (e) {
                delete e.arc_id, delete e.id, delete e.latitude, delete e.longitude, delete e.objectid;
            },
        },
        "Fire Stations": {
            updateProperties: function (e) {
                delete e.id, delete e.x, delete e.y;
            },
        },
        Hospitals: {
            updateProperties: function (e) {
                delete e.id, delete e.latitude, delete e.longitude, delete e.objectid, delete e.shape__len;
            },
        },
        "Natural Gas Liquid Pipelines": {
            updateProperties: function (e) {
                delete e.fid, delete e.shape_leng, delete e.shape__len;
            },
        },
        "Power Plants": {
            updateProperties: function (e) {
                var t;
                for (t in (delete e.fid, delete e.latitude83, delete e.longitude8, e)) (e[t] && "." !== e[t]) || delete e[t];
            },
        },
        "Responsibility Areas": {
            updateProperties: function (e) {
                delete e.orig_fid, delete e.shape_area, delete e.shape_leng;
            },
        },
        "Direct Protection Areas": {
            updateProperties: function (e) {
                delete e.orig_fid, delete e.shape_area, delete e.shape_leng;
            },
        },
    };
};
UserMetadataLayers.prototype = {
    updateProperties: function (e) {
        return this._layers[e] ? this._layers[e].updateProperties : null;
    },
};
var Alerts = function (e) {
    let t,
        i,
        a = this;
    (this._options = e),
        (this._map = null),
        (this._retrySeconds = 20),
        (this._timeoutID = 0),
        (this._colors = {
            warning: { normal: "#f90", hover: "#ffb84d" },
            error: { normal: "#f30", hover: "#ff704d" },
            info: { normal: "#09f", hover: "#4db8ff" },
            success: { normal: "#3c3", hover: "#70db70" },
            test: { normal: "#42f5cb", hover: "#baffef" },
            old: { normal: "#999", hover: "#bfbfbf" },
        }),
        ((t = document.createElement("div")).id = "alertsOverlay"),
        t.classList.add("hidden", "overlay", "draggable"),
        document.body.appendChild(t),
        ((i = document.createElement("div")).className = "titleText"),
        (i.innerHTML = "Alerts"),
        t.appendChild(i),
        (this._alertsList = document.createElement("UL")),
        (this._alertsList.id = "alertsList"),
        this._alertsList.setAttribute("not-draggable", !0),
        t.appendChild(this._alertsList),
        (this._notifyGranted = !0),
        Notify.needsPermission &&
            Notify.isSupported() &&
            Notify.requestPermission(
                function () {
                    a._notifyGranted = !0;
                },
                function () {
                    a._notifyGranted = !1;
                }
            );
};
Alerts.prototype = {
    onAdd: function (e) {
        let t = this;
        (this._map = e),
            $.ajax("/lib/data/agencies.json", { dataType: "json" })
                .fail(function (e, t) {
                    "abort" !== t && alert("Error agency codes: " + t);
                })
                .done(function (e) {
                    (t._agencies = e), t._connect();
                }),
            firemap.overlay.show("alertsOverlay");
    },
    onRemove: function (e) {
        (this._map = null), firemap.overlay.close("alertsOverlay"), this._socket && ((this._socket.onclose = null), this._socket.close(), (this._socket = null)), this._timeoutID && (clearInterval(this._timeoutID), (this._timeoutID = 0));
    },
    _connect: function () {
        let e = this;
        this._socket ||
            ((this._socket = new WebSocket(Constants.urls.ws)),
            (this._socket.error = function (e) {
                console.log("pylaski ws error: " + e);
            }),
            (this._socket.onopen = function (t) {
                e._timeoutID && (clearInterval(e._timeoutID), (e._timeoutID = null));
            }),
            (this._socket.onclose = function (t) {
                (e._socket = null),
                    e._timeoutID ||
                        (e._timeoutID = setTimeout(function () {
                            (e._timeoutID = 0), e._connect();
                        }, 1e3 * e._retrySeconds));
            }),
            (this._socket.onmessage = function (t) {
                "object" == typeof t.data && "Blob" === t.data.constructor.name
                    ? t.data.text().then(function (t) {
                          e._handleMessage(JSON.parse(t));
                      })
                    : e._handleMessage(JSON.parse(t.data));
            }));
    },
    _handleMessage: function (e) {
        if (e.error) return void console.log(e.error);
        let t,
            i,
            a,
            r = this,
            n = "",
            s = e.data.AgencyID + "_" + e.data.IncidentNumber;
        for (let t = 0; t < this._alertsList.childNodes.length; t++) if (this._alertsList.childNodes[t]._id === s) return console.log("duplicate for:"), void console.log(e);
        if ("post" === e.cmd) {
            if (("TestAlert" === e.src || "PulsePoint" === e.src) && e.data.Latitude && e.data.Latitude) {
                if (e.data.CallReceivedDateTime) {
                    let t = moment(e.data.CallReceivedDateTime),
                        i = moment();
                    i.isSame(t, "days") ? (n += moment(e.data.CallReceivedDateTime).local().tz(Constants.tz).format("HH:mm")) : (n += moment(e.data.CallReceivedDateTime).local().tz(Constants.tz).format("MMM DD HH:mm")),
                        moment(i).subtract(1, "hour").isSameOrAfter(t) && (a = this._colors.old);
                }
                "PulsePoint" === e.src ? ((n += " CAD:"), a || (a = this._colors.warning)) : ((n += " TEST:"), a || (a = this._colors.test)),
                    (t = "warning"),
                    e.data.AgencyID && this._agencies[e.data.AgencyID] && (n += " " + this._agencies[e.data.AgencyID]),
                    e.data.FullDisplayAddress && e.data.CityOrLocality ? (n += " " + e.data.FullDisplayAddress.substring(0, e.data.FullDisplayAddress.length - 4)) : e.data.CityOrLocality && (n += " " + e.data.CityOrLocality),
                    (e.data._title = n),
                    (i = [parseFloat(e.data.Latitude), parseFloat(e.data.Longitude)]),
                    delete e.data.AgencyID,
                    delete e.data.AgencyIncidentCallTypeDescription,
                    delete e.data.CallReceivedDateTime,
                    delete e.data.CityOrLocality,
                    delete e.data.ID,
                    delete e.data.Latitude,
                    delete e.data.Longitude,
                    delete e.data.StateOrProvince,
                    delete e.data.StreetName,
                    delete e.data.StreetNumber,
                    delete e.data.StreetSuffix,
                    delete e.data.UnitsDispatched;
            }
            if (i) {
                let t = document.createElement("LI");
                (t._id = s),
                    (t.style.background = a.normal),
                    (t.onmouseover = function () {
                        t._clicked ? (t.style.background = r._colors.old.hover) : (t.style.background = a.hover);
                    }),
                    (t.onmouseout = function () {
                        t._clicked ? (t.style.background = r._colors.old.normal) : (t.style.background = a.normal);
                    });
                let o = document.createElement("div");
                (o.className = "cam-btn"),
                    (o.style.background = Constants.cameraButton.backgroundColor),
                    (o.onclick = function (e) {
                        firemap.cameras.showCamerasViewingLatLng(L.latLng(i), r._map);
                    }),
                    (o.onmouseover = function () {
                        o.style.background = Constants.cameraButton.hover.backgroundColor;
                    }),
                    (o.onmouseout = function () {
                        o.style.background = Constants.cameraButton.backgroundColor;
                    }),
                    t.appendChild(o);
                let l = document.createElement("div");
                (l.className = "btn"),
                    (l.style.background = Constants.closeButton.backgroundColor),
                    (l.onclick = function (e) {
                        r._alertsList.removeChild(t), e.stopPropagation();
                    }),
                    (l.onmouseover = function () {
                        l.style.background = Constants.closeButton.hover.backgroundColor;
                    }),
                    (l.onmouseout = function () {
                        l.style.background = Constants.closeButton.backgroundColor;
                    }),
                    t.appendChild(l);
                let d = document.createElement("SPAN");
                (d.textContent = n),
                    (t.onclick = function () {
                        (t._clicked = !0), firemap.fire.addIgnitionAtLatLng(i, e.data, e.src + " Ignitions", n), r._map.setView(i, 13);
                    }),
                    t.appendChild(d),
                    this._alertsList.hasChildNodes() ? this._alertsList.insertBefore(t, this._alertsList.childNodes[0]) : this._alertsList.appendChild(t),
                    firemap.overlay.show("alertsOverlay"),
                    this._notifyGranted &&
                        document.hidden &&
                        new Notify("Firemap Alert", {
                            body: n,
                            timeout: 60,
                            notifyClick: function () {
                                firemap.fire.addIgnitionAtLatLng(i, e.data, e.src + " Ignitions", n), r._map.setView(i, 13);
                            },
                        }).show();
            }
        }
    },
};
var WeatherForecast = function (e) {
    var t = this;
    (this._canvasUtils = new CanvasUtils()),
        (this._utils = new Utils()),
        (this._shownCharts = {}),
        (this._sources = {
            firebuster: { title: "FireBuster (5km)", shortTitle: "FB", name: "firebuster", attribution: "USFS FireBuster", windyURLPrefix: "https://pulaski.sdsc.edu/", color: "#4daf4a" },
            hrrr: { title: "HRRR (3km)", name: "hrrr", attribution: "NOAA HRRR", wmsURLPrefix: "https://sdge.sdsc.edu/", windyURLPrefix: "https://sdge.sdsc.edu/", color: "#377eb8" },
            ndfd: { title: "NDFD (2.5km)", name: "ndfd", attribution: "NOAA NDFD", windyURLPrefix: "https://pulaski.sdsc.edu/", color: "#ff7f00" },
            nbm: { title: "NBM (2.5km)", name: "nbm", attribution: "NOAA NBM", windyURLPrefix: "https://pulaski.sdsc.edu/", color: "#984ea3" },
        }),
        (this._curSource = "hrrr");
    let i = document.getElementById("forecastTypeSelect");
    for (let e in this._sources) {
        let t = document.createElement("option");
        (t.text = this._sources[e].title), (t.value = e), i.add(t);
    }
    (i.onchange = function () {
        (t._curSource = this.value), t._updateLayer();
    }),
        (i.value = this._curSource),
        (this._observables = {
            "Air Temperature": {
                getValue: function (e) {
                    return ((9 * e) / 5 + 32).toFixed(1);
                },
                getColor: function (e) {
                    return t._canvasUtils.temperatureColor(e);
                },
                getLayer: function () {
                    return "WIFIRE:" + t._curSource + "_temperature";
                },
                min: 0,
                max: 120,
                units: "F",
            },
            Humidity: {
                getColor: function (e) {
                    return t._canvasUtils.humidityColor(e);
                },
                getLayer: function () {
                    return "WIFIRE:" + t._curSource + "_humidity";
                },
                min: 0,
                max: 100,
                units: "%",
            },
            Wind: {
                getValue: function (e) {
                    return (2.237 * e).toFixed(1);
                },
                getColor: function (e) {
                    return t._canvasUtils.windSpeedColor(e);
                },
                getLayer: function () {
                    return t._showGust ? "WIFIRE:" + t._curSource + "_wind_gust" : "WIFIRE:" + t._curSource + "_wind_speed";
                },
                min: 0,
                max: 85,
                units: "MPH",
            },
        }),
        (this._currentObservable = "Air Temperature");
    var a = moment().tz(Constants.tz).format("z").replace(/(\w)/g, "\\\\$1");
    (this._FLATPICKR_FORMAT = "Y-m-d H:00 " + a),
        (this._timeVal = moment().minutes(0).seconds(0).milliseconds(0).add(1, "hour").toDate()),
        (this._minDate = this._timeVal),
        (this._maxDate = moment.utc(this._timeVal).add(23, "hour").toDate()),
        (this._time = document.getElementById("wxForecastTimeVal").flatpickr({
            disableMobile: !0,
            dateFormat: this._FLATPICKR_FORMAT,
            defaultDate: this._timeVal,
            enableTime: !0,
            maxDate: moment.utc(this._timeVal).add(23, "hour").toDate(),
            minDate: this._timeVal,
            time_24hr: !0,
            onValueUpdate: function (e, i, a) {
                (t._timeVal = e[0]), t._updateStepButtons(), t._updateLayer(!0);
            },
        })),
        L.DomEvent.addListener(document.getElementById("wxForecastBackwardButton"), "click", this._stepBackward, this),
        L.DomEvent.addListener(document.getElementById("wxForecastForwardButton"), "click", this._stepForward, this),
        (document.getElementById("wxForecastBackwardButton").disabled = !0);
    let r = function () {
        Object.keys(t._shownCharts).length > 0 && t.resizeCharts();
    };
    window.addEventListener("resize", r),
        (document.getElementById("forecastWindTab").onclick = document.getElementById("forecastHumidTab").onclick = r),
        document.getElementById("wxForecastColorScale").getContext("2d").scale(1, 3),
        (document.getElementById("forecastShowWind").onchange = function () {
            (t._showWind = this.checked), t._updateWind();
        }),
        (document.getElementById("forecastShowWind").checked = this._showWind = !0),
        (document.getElementById("forecastShowGust").onchange = function () {
            (t._showGust = this.checked), t._updateLayer();
        }),
        (document.getElementById("forecastShowGust").checked = this._showGust = !1);
};
WeatherForecast.prototype = {
    _drawColorScale: function () {
        var e = document.getElementById("wxForecastColorScale").getContext("2d"),
            t = this._observables[this._currentObservable];
        (document.getElementById("wxForecastTypeControl").style.height = 260), e.clearRect(0, 0, 300, 50);
        var i,
            a = e.createLinearGradient(0, 0, 290, 20);
        for (i = t.min; i <= t.max; i += t.max / 30) a.addColorStop((i - t.min) / (t.max - t.min), t.getColor(i).bg);
        for (e.fillStyle = a, e.fillRect(0, 0, 290, 20), e.strokeStyle = "black", e.lineWidth = 1, e.font = '14px/1.5 "Helvetica Neue", Arial, Helvetica, sans-serif', e.fillStyle = "black", i = 0; i <= 290; i += 290 / 6) {
            e.beginPath(), 0 == i ? (e.moveTo(i + 1, 20), e.lineTo(i + 1, 30)) : 290 == i ? (e.moveTo(i - 1, 20), e.lineTo(i - 1, 30)) : (e.moveTo(i, 20), e.lineTo(i, 30)), e.stroke(), e.beginPath();
            let a = Math.round((t.max - t.min) * (i / 290));
            0 == i ? e.fillText(a, i, 42) : 290 == i ? e.fillText(a, i - 7 * a.toString().length, 42) : e.fillText(a, i - 4 * a.toString().length, 42);
        }
    },
    onAdd: function (e) {
        var t = this,
            i = Object.keys(this._observables);
        this._map = e;
        for (let e in i) i[e] += " (" + this._observables[i[e]].units + ")";
        let a = Object.keys(this._observables);
        if (
            ((this._typeSlider = this._utils.createSlider({ id: "wxForecastType", start: 0, step: 1, min: 0, max: a.length - 1, textId: ["wxForecastTypeVal"], formatMap: a, textFormatMap: i })),
            this._typeSlider.noUiSlider.on("set", function () {
                t._updateLayer();
            }),
            this._currentObservable)
        )
            for (let e = 0; e < a.length; e++)
                if (a[e] === this._currentObservable) {
                    this._typeSlider.noUiSlider.set(e);
                    break;
                }
        window.firemap.overlay.show("wxForecastTypeControl"), this._updateLayer(), e.on("click", this._click, this);
    },
    onRemove: function (e) {
        this._removeWind(),
            e.off("click", this._click, this),
            window.firemap.overlay.close("wxForecastTypeControl"),
            this._typeSlider.noUiSlider.destroy(),
            this._layer && (this._layer.onRemove(e), (this._layer = null), (this._curLayer = null)),
            (this._map = null);
    },
    setOpacity: function (e) {
        this._layer && this._layer.setOpacity(e);
    },
    getModels: function () {
        return this._sources;
    },
    getModelTitle: function (e) {
        return this._sources[e].title;
    },
    getModelShortTitle: function (e) {
        return this._sources[e].shortTitle || this._sources[e].name.toUpperCase();
    },
    _stepBackward: function () {
        this._time.setDate(moment.utc(this._timeVal).subtract(1, "hour").toDate());
    },
    _stepForward: function () {
        this._time.setDate(moment.utc(this._timeVal).add(1, "hour").toDate());
    },
    _removeWind: function () {
        this._ajaxWindyFile && (this._ajaxWindyFile.abort(), (this._ajaxWindyFile = null)), this._windLayer && (this._windLayer.onRemove(map), (this._windLayer = null), (this._loadedWindyFile = null));
    },
    _updateWind: function () {
        if (this._showWind) {
            var e = this,
                t = (this._sources[this._curSource].windyURLPrefix || "") + "data/" + this._curSource + "-wind/" + moment.utc(this._timeVal).format("YYYYMMDDHH");
            this._showGust && (t += "-gust"),
                (t += ".json") !== this._loadedWindyFile &&
                    (this._ajaxWindyFile = $.ajax(t)
                        .always(function () {
                            e._ajaxWindyFile = null;
                        })
                        .fail(function (i, a) {
                            console.log("Error loading windy file", t, ":", a), e._windLayer && (e._map.removeLayer(e._windLayer), (e._windLayer = null));
                        })
                        .done(function (i) {
                            e._map &&
                                ((e._loadedWindyFile = t),
                                e._windLayer
                                    ? e._windLayer.setData(i)
                                    : ((e._windLayer = L.velocityLayer({ zIndex: Constants.zLayers.forecast, data: i, maxVelocity: 22, displayValues: !1, colorScale: ["#fff"] })), e._map.addLayer(e._windLayer)));
                        }));
        } else this._removeWind();
    },
    _updateLayer: function (e) {
        this._updateWind(), (this._currentObservable = this._typeSlider.noUiSlider.get()), this._drawColorScale(), this._createWMSLayer();
        let t = this._observables[this._currentObservable].getLayer();
        (e || t !== this._curLayer) && ((this._curLayer = t), this._layer.setParams({ layers: t, TIME: moment.utc(this._timeVal).toISOString() }), this._map.addLayer(this._layer));
    },
    _createWMSLayer: function () {
        let e = this._sources[this._curSource].wmsURLPrefix ? this._sources[this._curSource].wmsURLPrefix + "geoserver/wms" : Constants.urls.wms;
        if (!this._layer || !this._curWMSUrlPrefix != e) {
            this._layer && this._map.removeLayer(this._layer),
                (this._curWMSUrlPrefix = e),
                (this._layer = L.tileLayer.wms(this._curWMSUrlPrefix, {
                    layers: this._observables[this._currentObservable].getLayer(),
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.0",
                    attribution: this._sources[this._curSource].attribution,
                    zIndex: Constants.zLayers.forecast,
                    detectRetina: Constants.retina,
                    opacity: 0.6,
                })),
                this._map.addLayer(this._layer);
        }
    },
    _updateStepButtons: function () {
        this._timeVal.getTime() === this._minDate.getTime() ? (document.getElementById("wxForecastBackwardButton").disabled = !0) : (document.getElementById("wxForecastBackwardButton").disabled = !1),
            this._timeVal.getTime() === this._maxDate.getTime() ? (document.getElementById("wxForecastForwardButton").disabled = !0) : (document.getElementById("wxForecastForwardButton").disabled = !1);
    },
    _click: function (e) {
        var t = this;
        this._ajaxForecastData && this._ajaxForecastData.abort();
        var i = new Spinner().spin(),
            a = this._utils.initChart("forecastTemperatureChart", this),
            r = this._utils.initChart("forecastWindSpeedChart", this),
            n = this._utils.initChart("forecastWindGustChart", this),
            s = this._utils.initChart("forecastWindDirectionChart", this),
            o = this._utils.initChart("forecastHumidityChart", this);
        a.appendChild(i.el),
            firemap.overlay.isShown("forecastChartControl") || (this.resizeCharts(), firemap.overlay.show("forecastChartControl")),
            (this._ajaxForecastData = $.ajax({
                url: Constants.urls.pylaski + "forecast?lat=" + e.latlng.lat + "&lon=" + e.latlng.lng + "&source=all",
                type: "GET",
                dataType: "jsonp",
                jsonp: "callback",
                jsonpCallback: "forecastData",
                timeout: 3e4,
            })
                .always(function () {
                    t._ajaxForecastData = null;
                })
                .fail(function (e, t) {
                    "abort" !== t && (a.innerHTML = '<div style="text-align:center;">Error retrieving measurements: ' + t + ".</div>");
                })
                .done(function (e) {
                    if (e.hasOwnProperty("features")) {
                        if (e.features.length > 0) {
                            let p = { temp: {}, rh: {}, ws: {}, wg: {}, wd: {} },
                                _ = (foundWs = foundWg = foundWd = foundRh = !1);
                            for (zz in e.features) {
                                let t = e.features[zz];
                                if (t.hasOwnProperty("properties")) {
                                    let e = t.properties,
                                        a = e.description.source,
                                        r = e.hasOwnProperty("timestamp") ? e.timestamp : null,
                                        n = e.hasOwnProperty("temperature") ? e.temperature : null,
                                        s = e.hasOwnProperty("relative_humidity") ? e.relative_humidity : null,
                                        o = e.hasOwnProperty("wind_speed") ? e.wind_speed : null,
                                        u = e.hasOwnProperty("wind_gust") ? e.wind_gust : null,
                                        h = e.hasOwnProperty("wind_direction") ? e.wind_direction : null,
                                        y = e.hasOwnProperty("units") ? e.units : null;
                                    (p.temp[a] = []), (p.rh[a] = []), (p.ws[a] = []), (p.wg[a] = []), (p.wd[a] = []);
                                    let f = moment(),
                                        g = moment().add(1, "days");
                                    for (var i = 0; i < r.length; i++) {
                                        var l = moment(r[i]),
                                            d = l.valueOf();
                                        if (l.isAfter(g)) break;
                                        if (!l.isBefore(f)) {
                                            if (
                                                (null !== n && (y && "C" == y.temperature ? p.temp[a].push([d, (9 * n[i]) / 5 + 32]) : p.temp[a].push([d, n[i]]), (_ = !0)),
                                                null !== s && (p.rh[a].push([d, s[i]]), (foundRh = !0)),
                                                null !== o)
                                            ) {
                                                var m = o[i];
                                                y && "mps" == y.wind_speed && (m *= Constants.MPS_TO_MPH), p.ws[a].push([d, m]), (foundWs = !0);
                                            }
                                            if (null !== u) {
                                                var c = u[i];
                                                y && "mps" == y.wind_gust && (c *= Constants.MPS_TO_MPH), p.wg[a].push([d, c]), (foundWg = !0);
                                            }
                                            null !== h && (p.wd[a].push([d, h[i]]), (foundWd = !0));
                                        }
                                    }
                                }
                            }
                            var u = [];
                            (t._shownCharts = { wind: [], humid: [] }),
                                _ && t._shownCharts.humid.push("forecastTemperatureChart"),
                                foundWs && t._shownCharts.wind.push("forecastWindSpeedChart"),
                                foundWg && t._shownCharts.wind.push("forecastWindGustChart"),
                                foundWd && t._shownCharts.wind.push("forecastWindDirectionChart"),
                                foundRh && t._shownCharts.humid.push("forecastHumidityChart");
                            var h = Constants.chartHeight.big + "px";
                            if (_) {
                                u = [];
                                for (let e in p.temp)
                                    p.temp[e].length &&
                                        u.push({
                                            title: t._sources[e].shortTitle || t._sources[e].name.toUpperCase(),
                                            units: "F",
                                            values: p.temp[e],
                                            color: t._sources[e].color,
                                            yTickInterval: 5,
                                            xTickInterval: Constants.chartXTickInterval,
                                            legendItemClick: t._chartLegendItemClick,
                                        });
                                (a.style.height = h), t._utils.showChart(u, { id: "forecastTemperatureChart", title: "Temperature", singleYAxis: !0 });
                            } else a.innerHTML = '<div style="text-align:center;">No temperature measurements.</div>';
                            if (foundWs) {
                                u = [];
                                for (let e in p.ws)
                                    p.ws[e].length &&
                                        u.push({
                                            title: t._sources[e].shortTitle || t._sources[e].name.toUpperCase(),
                                            units: "mph",
                                            values: p.ws[e],
                                            color: t._sources[e].color,
                                            yTickInterval: 10,
                                            xTickInterval: Constants.chartXTickInterval,
                                            legendItemClick: t._chartLegendItemClick,
                                        });
                                (r.style.height = h), t._utils.showChart(u, { id: "forecastWindSpeedChart", title: "Speed", singleYAxis: !0 });
                            } else r.innerHTML = '<div style="text-align:center;">No wind speed measurements.</div>';
                            if (foundWg) {
                                u = [];
                                for (let e in p.wg)
                                    p.wg[e].length &&
                                        u.push({
                                            title: t._sources[e].shortTitle || t._sources[e].name.toUpperCase(),
                                            units: "mph",
                                            values: p.wg[e],
                                            color: t._sources[e].color,
                                            yTickInterval: 10,
                                            xTickInterval: Constants.chartXTickInterval,
                                            legendItemClick: t._chartLegendItemClick,
                                        });
                                (n.style.height = h), t._utils.showChart(u, { id: "forecastWindGustChart", title: "Gust", singleYAxis: !0 });
                            } else n.innerHTML = '<div style="text-align:center;">No wind gust measurements.</div>';
                            if (foundWd) {
                                u = [];
                                for (let e in p.wd)
                                    p.wd[e].length &&
                                        u.push({
                                            title: t._sources[e].shortTitle || t._sources[e].name.toUpperCase(),
                                            units: "",
                                            values: p.wd[e],
                                            color: t._sources[e].color,
                                            max: 360,
                                            yTickInterval: 90,
                                            xTickInterval: Constants.chartXTickInterval,
                                            legendItemClick: t._chartLegendItemClick,
                                        });
                                (s.style.height = h), t._utils.showChart(u, { id: "forecastWindDirectionChart", title: "Direction", singleYAxis: !0 });
                            } else s.innerHTML = '<div style="text-align:center;">No wind direction measurements.</div>';
                            if (foundRh) {
                                u = [];
                                for (let e in p.rh)
                                    p.rh[e].length &&
                                        u.push({
                                            title: t._sources[e].shortTitle || t._sources[e].name.toUpperCase(),
                                            units: "%",
                                            values: p.rh[e],
                                            color: t._sources[e].color,
                                            max: 100,
                                            yTickInterval: 10,
                                            xTickInterval: Constants.chartXTickInterval,
                                            legendItemClick: t._chartLegendItemClick,
                                        });
                                (o.style.height = h), t._utils.showChart(u, { id: "forecastHumidityChart", title: "Humidity", singleYAxis: !0 });
                            } else o.innerHTML = '<div style="text-align:center;">No relative humidity measurements.</div>';
                        }
                        t.resizeCharts();
                    } else a.innerHTML = '<div style="text-align:center;">No measurements found.</div>';
                }));
    },
    _chartLegendItemClick: function (e) {
        if ("click" != e.browserEvent.type) return !1;
        let t = this.visible,
            i = document.getElementsByClassName("wxChart");
        for (let e in i)
            if (i[e].id && 0 === i[e].id.indexOf("forecast")) {
                let a = $("#" + i[e].id).highcharts();
                if (a !== this.chart)
                    for (let e in a.series)
                        if (a.series[e].name === this.name) {
                            t ? a.series[e].hide() : a.series[e].show();
                            break;
                        }
            }
    },
    resizeCharts: function () {
        var e,
            t,
            i = document.getElementById("forecastChartControl"),
            a = document.getElementById("forecastTitle"),
            r = document.getElementById("forecastTemperatureChart"),
            n = document.getElementById("forecastWindSpeedChart"),
            s = document.getElementById("forecastWindGustChart"),
            o = document.getElementById("forecastWindDirectionChart"),
            l = document.getElementById("forecastHumidityChart"),
            d = window.innerWidth - 30,
            m = d < Constants.chartWidth.max ? d : Constants.chartWidth.max;
        let c;
        if (
            ((i.style.width = a.style.width = r.style.width = n.style.width = s.style.width = o.style.width = l.style.width = m + "px"),
            $(".tab__content").css("width", m + "px"),
            (c = document.getElementById("forecastWindTab").checked ? "wind" : "humid"),
            this._shownCharts[c])
        ) {
            let a = "wind" === c ? 3 : 2;
            for (t in ((e = this._utils.getChartHeight("forecastTitle", this._shownCharts[c].length, a, 30)), this._shownCharts[c])) document.getElementById(this._shownCharts[c][t]).style.height = e + "px";
            (e = a * e + 20), $("#forecastTabs").css("height", e + "px"), (i.style.height = 35 + e + "px");
        } else i.style.height = "100px";
    },
};
var Overlay = function (e) {
    (this._config = e || Constants.overlayConfig), (this._sharedOverlays = {}), (this._lastOverlayZIndex = 1e3), (this._listeners = {});
    var t = this;
    window.addEventListener("resize", function () {
        setTimeout(function () {
            t.redraw();
        }, 100);
    }),
        (window.dragMoveListener = this._dragMoveListener);
};
Overlay.prototype = {
    allowDrag: function (e) {
        var t = this,
            i = {
                inertia: !0,
                restrict: { restriction: "parent", endOnly: !0, elementRect: { top: 0.75, left: 0.75, bottom: 0.25, right: 0.25 } },
                autoScroll: !1,
                onmove: dragMoveListener,
                onstart: function (e) {
                    e.target.style["z-index"] = t._lastOverlayZIndex++;
                },
                onend: function (e) {
                    var i, a;
                    t._state &&
                        (((i = (a = t._state.load("overlays")) ? JSON.parse(a) : {})[e.target.id] = { x: parseFloat(e.target.getAttribute("data-x")), y: parseFloat(e.target.getAttribute("data-y")) }),
                        t._state.save("overlays", JSON.stringify(i)));
                },
            };
        e && e.ignore && (i.ignoreFrom = e.ignore),
            interact(".draggable")
                .draggable(i)
                .on("tap", function (e) {
                    "touch" === e.pointerType && 0 == Object.keys(e.target).length && $(e.target).trigger("click");
                }),
            interact(".drag-resizable")
                .draggable(i)
                .resizable({ preserveAspectRatio: !1, edges: { left: !0, right: !0, bottom: !0, top: !0 } })
                .on("resizemove", function (e) {
                    var t = e.target,
                        i = parseFloat(t.getAttribute("data-x")) || 0,
                        a = parseFloat(t.getAttribute("data-y")) || 0;
                    (t.style.width = e.rect.width + "px"),
                        (t.style.height = e.rect.height + "px"),
                        (i += e.deltaRect.left),
                        (a += e.deltaRect.top),
                        (i = Math.round(i)),
                        (a = Math.round(a)),
                        (t.style.webkitTransform = t.style.transform = "translate(" + i + "px," + a + "px)"),
                        t.setAttribute("data-x", i),
                        t.setAttribute("data-y", a),
                        t._overlayOptions && t._overlayOptions.resizeListener && t._overlayOptions.resizeListener(e.deltaRect.bottom - e.deltaRect.top, e.deltaRect.right - e.deltaRect.left);
                });
    },
    close: function (e, t) {
        var i,
            a = !0;
        if (t && t.sharedOwner && this._sharedOverlays[e])
            for (i in ((a = !1), this._sharedOverlays[e]))
                if (this._sharedOverlays[e][i] == t.sharedOwner) {
                    this._sharedOverlays[e].splice(i, 1), 0 == this._sharedOverlays[e].length && (a = !0);
                    break;
                }
        if (a && ((document.getElementById(e).style.display = "none"), (document.getElementById(e).onclick = null), this._listeners.close)) for (i in this._listeners.close) (x = this._listeners.close[i]), x.fn.call(x.context, { id: e });
    },
    isShown: function (e) {
        var t = document.getElementById(e);
        return !!(t && t.style && t.style.display) && "block" == t.style.display;
    },
    moveToStayInWindow: function (e, t) {
        var i,
            a,
            r = parseFloat(e.getAttribute("data-x")) || 0,
            n = parseFloat(e.getAttribute("data-y")) || 0,
            s = t || e.offsetWidth,
            o = parseInt(e.style.left.substring(0, e.style.left.indexOf("px"))) + r,
            l = o + s + 5,
            d = parseInt(e.style.top.substring(0, e.style.top.indexOf("px"))) + n,
            m = d + e.offsetHeight + 5;
        (i = l > window.innerWidth ? r + (window.innerWidth - l) : o < 0 ? r - o + 5 : r), (a = m > window.innerHeight ? n + (window.innerHeight - m) : d < 0 ? n - d + 5 : n), this._moveTarget(e, i, a);
    },
    on: function (e, t, i) {
        this._listeners[e] || (this._listeners[e] = []), this._listeners[e].push({ fn: t, context: i });
    },
    off: function (e, t) {
        var i;
        for (i in this._listeners[e]) this._listeners[e][i].fn === t && this._listeners[e].splice(i, 1);
    },
    redraw: function (e) {
        var t,
            i,
            a = document.getElementsByClassName("overlay");
        for (t in a) a[t].style && "block" == a[t].style.display && (((i = a[t]._overlayOptions || {}).resize = !0), this.show(a[t].id, i), a[t].className.indexOf("draggable") > -1 && this.moveToStayInWindow(a[t]));
    },
    setState: function (e) {
        this._state = e;
    },
    show: function (e, t) {
        var i,
            a,
            r = document.getElementById(e),
            n = !1,
            s = !1,
            o = this,
            l = "block",
            d = !1;
        if (
            ((r._context = this),
            t && ((l = t.display || "block"), (i = t.position), (n = t.ignoreSavedPosition), t.hasOwnProperty("allowOverlap") && (d = t.allowOverlap)),
            this._config[e] && !i && this._config[e].position && (i = this._config[e].position),
            "IMG" != r.nodeName || r.complete
                ? ((r.style.display = l), this._setPosition(r, i, d, n))
                : (r.onload = function () {
                      (r.style.display = l), o._setPosition(r, i, d, n);
                  }),
            this._config[e] && this._config[e].zindex
                ? (r.style["z-index"] = this._config[e].zindex)
                : ((r.style["z-index"] = this._lastOverlayZIndex++),
                  (r.onclick = function () {
                      this.style["z-index"] = this._lastOverlayZIndex++;
                  })),
            (r._overlayOptions = t),
            t && t.sharedOwner)
        )
            if (this._sharedOverlays[e]) {
                for (a in ((s = !1), this._sharedOverlays[e]))
                    if (this._sharedOverlays[e][a] == t.sharedOwner) {
                        s = !0;
                        break;
                    }
                s || this._sharedOverlays[e].push(t.sharedOwner);
            } else this._sharedOverlays[e] = [t.sharedOwner];
    },
    showMessageOverlay: function (e, t) {
        var i = document.getElementById("messageOverlayButton"),
            a = this;
        (document.getElementById("messageText").innerHTML = e),
            t && t.overlay
                ? (i.onclick = function () {
                      a.swap("messageOverlay", t.overlay);
                  })
                : (i.onclick = function () {
                      a.close("messageOverlay");
                  }),
            this.show("messageOverlay");
    },
    swap: function (e, t, i) {
        this.close(e), this.show(t, i);
    },
    _dragMoveListener: function (e) {
        var t = e.target,
            i = (parseFloat(t.getAttribute("data-x")) || 0) + e.dx,
            a = (parseFloat(t.getAttribute("data-y")) || 0) + e.dy;
        t._context._moveTarget(t, i, a);
    },
    _getCoords: function (e) {
        var t = { top: parseInt(e.style.top.substring(0, e.style.top.indexOf("px"))), left: parseInt(e.style.left.substring(0, e.style.left.indexOf("px"))) };
        return (t.left += parseFloat(e.getAttribute("data-x") || 0)), (t.right = t.left + e.offsetWidth), (t.top += parseFloat(e.getAttribute("data-y") || 0)), (t.bottom = t.top + e.offsetHeight), t;
    },
    _isCoordsOverlapping: function (e, t) {
        return !(e.top >= t.bottom || t.top >= e.bottom || e.left >= t.right || t.left >= e.right);
    },
    _moveTarget: function (e, t, i) {
        (t = Math.round(t)), (i = Math.round(i)), (e.style.webkitTransform = e.style.transform = "translate(" + t + "px, " + i + "px)"), e.setAttribute("data-x", t), e.setAttribute("data-y", i);
    },
    _moveToNotOverlap: function (e, t, i) {
        var a = parseInt(e.style.left.substring(0, e.style.left.indexOf("px")));
        (xdist = Math.abs(i.right + 1 - a)), (right = a + xdist + e.offsetWidth), right <= window.innerWidth && this._moveTarget(e, xdist, 0);
    },
    _setPosition: function (e, t, i, a) {
        var r,
            n,
            s,
            o = 0,
            l = !1,
            d = !0;
        if (
            (a || null == e.getAttribute("data-x") || "" == e.getAttribute("data-x")) &&
            (t && "center" !== t
                ? "centertop" === t
                    ? ((e.style.left = window.innerWidth / 2 - e.offsetWidth / 2 + "px"), (e.style.top = "8px"))
                    : "centerbottom" === t
                    ? ((e.style.left = window.innerWidth / 2 - e.offsetWidth / 2 + "px"), (e.style.top = window.innerHeight - e.offsetHeight - 8 + "px"))
                    : "leftcenter" === t
                    ? ((e.style.left = "50px"), (e.style.top = window.innerHeight / 2 - e.offsetHeight / 2 + "px"))
                    : "leftbottom" === t
                    ? ((e.style.left = "50px"), (e.style.top = window.innerHeight - e.offsetHeight - 8 + "px"))
                    : "lefttop" === t
                    ? ((e.style.left = "50px"), (e.style.top = "8px"))
                    : "rightcenter" === t
                    ? ((e.style.left = window.innerWidth - e.offsetWidth + "px"), (e.style.top = window.innerHeight / 2 - e.offsetHeight / 2 + "px"))
                    : "righttop" === t
                    ? ((e.style.left = window.innerWidth - e.offsetWidth + "px"), (e.style.top = "8px"))
                    : "rightbottom" === t
                    ? ((e.style.left = window.innerWidth - e.offsetWidth + "px"), (e.style.top = window.innerHeight - e.offsetHeight - 8 + "px"))
                    : t.left && t.top
                    ? ((e.style.left = t.left + "px"), (e.style.top = t.top + "px"))
                    : t.top && ((e.style.top = t.top + "px"), (e.style.left = window.innerWidth / 2 - e.offsetWidth / 2 + "px"))
                : ((e.style.left = window.innerWidth / 2 - e.offsetWidth / 2 + "px"), (e.style.top = window.innerHeight / 2 - e.offsetHeight / 2 + "px")),
            a ||
                !this._state ||
                (t && t.hasOwnProperty("loadFromState") && !0 !== t.loadFromState) ||
                ((s = this._state.load("overlays")) && ((overlayState = JSON.parse(s)), overlayState[e.id] && (this._moveTarget(e, overlayState[e.id].x, overlayState[e.id].y), (l = !0)))),
            !i && !l && e.className.indexOf("draggable") > -1)
        )
            for (n = document.getElementsByClassName("overlay"); d && o < 20; ) {
                o++, (d = !1);
                let t = this._getCoords(e);
                for (r in n)
                    if (n[r] != e && n[r].style && "block" == n[r].style.display && ((otherCoords = this._getCoords(n[r])), this._isCoordsOverlapping(t, otherCoords))) {
                        this._moveToNotOverlap(e, t, otherCoords), (d = !0);
                        break;
                    }
            }
        e.className.indexOf("draggable") > -1 && this.moveToStayInWindow(e);
    },
};
var LegendOverlay = function (e, t, i, a) {
    var r,
        n,
        s,
        o,
        l,
        d,
        m = this;
    if (!a || !a.title) throw "Must specify title.";
    for (r in ((this._layer = t),
    (this._overlayUtils = i),
    (this._overlay = document.createElement("div")),
    (this._overlay.id = "Legend " + a.title),
    this._overlay.classList.add("overlay", "draggable"),
    $(document).ready(function () {
        document.body.appendChild(m._overlay);
    }),
    e
        .on("overlayadd", function (e) {
            e.layer === m._layer && m._overlayUtils.show(m._overlay.id, { position: "leftbottom" });
        })
        .on("overlayremove", function (e) {
            e.layer === m._layer && m._overlayUtils.close(m._overlay.id);
        }),
    (n = document.createElement("div")).classList.add("titleText"),
    (n.style["margin-left"] = n.style["margin-right"] = "5px"),
    (n.innerHTML = a.title),
    this._overlay.appendChild(n),
    ((d = document.createElement("div")).className = "legend-items-container"),
    this._overlay.appendChild(d),
    a.items))
        (s = document.createElement("div")),
            ((o = document.createElement("div")).className = "legend-items-color"),
            (o.style.background = a.items[r].color),
            ((l = document.createElement("div")).className = "legend-items-text"),
            (l.innerHTML = a.items[r].name),
            s.appendChild(o),
            s.appendChild(l),
            d.appendChild(s);
};
(FireModeling = function (e) {
    var t = this;
    (this._map = e.map),
        (this._mapLayers = e.mapLayers),
        (this._firemap = e.firemap),
        (this._overlay = firemap.overlay),
        (this._WeatherStationsLayer = e.WeatherStationsLayer),
        (this._WeatherForecastLayer = e.WeatherForecastLayer),
        (this._webview = e.webview),
        (this._utils = new Utils()),
        this._ignitionLayer,
        (this._ignitionLayers = L.layerGroup()),
        (this._fireLayers = L.layerGroup()),
        (this._barrierLayers = { active: null, inactive: null }),
        this._winddirSlider,
        this._windspeedSlider,
        this._humiditySlider,
        this._temperatureSlider,
        this._timeSlider,
        this._selectedFire,
        this._fireTimeSlider,
        this._ensFireSlider,
        (this._fuelMoistureRanges = { one_hr: { min: 3, max: 300 }, ten_hr: { min: 4, max: 300 }, hundred_hr: { min: 5, max: 300 }, live_herb: { min: 5, max: 300 }, live_woody: { min: 60, max: 300 } }),
        (this._fireOptions = {
            conditions: "unknown",
            startTime: moment(),
            perimeterResolution: 60,
            fuelType: Constants.defaultFuel,
            fuelMoisture: { v: [{ model: 0, one_hr: 3, ten_hr: 4, hundred_hr: 6, live_herb: 60, live_woody: 110 }] },
            emberProbability: { min: 0, max: 100, v: 0 },
            timestep: { min: 10, max: 120, v: 30 },
            hours: { min: 1, max: 6, v: 3 },
            airtemperature: { min: 0, max: 110, v: [70, 70, 70, 70, 70, 70] },
            winddir: { min: 0, max: 359, v: [180, 180, 180, 180, 180, 180] },
            windspeed: { min: 0, max: 40, v: [5, 5, 5, 5, 5, 5] },
            humidity: { min: 0, max: 100, v: [50, 50, 50, 50, 50, 50] },
        }),
        (this._copiedFireOptions = e.copiedFireOptions),
        (this._fireNum = 0),
        (this._numRunFires = 0),
        this._fireSpinner,
        this._playFireTimer,
        (this._configuringFire = !1),
        this._fireStartTime,
        this._wxStationStartTime,
        (this._wxStationStartTimeIsNow = !0),
        (this._wxStationWindSpeedAverage = !0),
        (this._FORMAT_FLATPICKR_FIRE_START_TIME = "Y-m-d H:i"),
        (this._FORMAT_MOMENT_FIRE_START_TIME = "YYYY-MM-DD HH:mm"),
        (this._FORMAT_MESOWEST_TIME = "YYYY-MM-DD HH:mmZZ"),
        (this._wxStationStartTimeVal = this._fireOptions.startTime.format(this._FORMAT_MOMENT_FIRE_START_TIME)),
        (document.getElementById("fireDisplayType").onchange = function () {
            (t._selectedFire.displayType = this.value), t._setFireStyle(t._selectedFire);
        }),
        (document.getElementById("fireDisplayFrequency").onchange = function () {
            (t._selectedFire.displayFrequency = this.value), t._setFireStyle(t._selectedFire), t._updateLegend();
        }),
        (this._fireColors = ["darkred", "firebrick", "red", "orangered", "tomato", "darkorange", "orange", "gold", "yellow", "darkkhaki", "khaki", "white"]),
        (this._selectedPopulationStyle = { color: "purple", fillColor: "purple", opacity: 1, fillOpacity: 0.5 }),
        (this._selectedIgnitionPointIcon = L.AwesomeMarkers.icon({ markerColor: "red", icon: "fire", prefix: "fa" })),
        (this._selectedEnsIgnitionPointIcon = L.AwesomeMarkers.icon({ markerColor: "orange", icon: "fire", prefix: "fa" })),
        (this._unselectedIgnitionPointIcon = L.AwesomeMarkers.icon({ markerColor: "gray", icon: "fire", prefix: "fa" })),
        (this._selectedIgnitionStyle = { color: this._fireColors[0], opacity: 1, fillColor: "black", fillOpacity: 0.7 }),
        (this._unselectedIgnitionStyle = { color: "gray", opacity: 1, fillColor: "black", fillOpacity: 0.7 }),
        (this._ensIgnitionOpacity = 1),
        (this._selectedEnsIgnitionStyle = { color: "orange", opacity: this._ensIgnitionOpacity, fillOpacity: 0 }),
        (this._unselectedEnsIgnitionStyle = { color: "gray", opacity: this._ensIgnitionOpacity, fillOpacity: 0 }),
        (this._activeBarrierStyle = { color: "blue", fillColor: "blue", opacity: 1 }),
        (this._inactiveBarrierStyle = { color: "green", fillColor: "green", opacity: 1 }),
        (L.drawLocal.draw.toolbar.buttons.polyline = "Draw a line for fire suppression."),
        (L.drawLocal.draw.toolbar.buttons.polygon = "Draw a polygon fire perimeter."),
        (L.drawLocal.draw.toolbar.buttons.rectangle = "Draw a rectangle fire perimeter."),
        (L.drawLocal.draw.toolbar.buttons.marker = "Draw a fire marker."),
        (L.drawLocal.edit.handlers.remove.tooltip.text = "Click on a feature to remove and then click on Save.");
    var a = document.getElementById("perimeterEnsembleSizeVal");
    (a.min = 2),
        (a.max = 20),
        (a.step = 1),
        document.getElementById("perimeterEnsembleSizeVal").addEventListener("focusout", function () {
            t.randomizePerimeterEnsemble(!1);
        }),
        document.getElementById("perimeterEnsembleSizeVal").addEventListener("keypress", function (e) {
            13 === e.keyCode && t.randomizePerimeterEnsemble(!1);
        });
    var r = document.getElementById("perimeterEnsembleVarianceVal");
    for (i in ((r.min = 100),
    (r.max = 9999),
    (r.step = 1),
    document.getElementById("perimeterEnsembleVarianceVal").addEventListener("focusout", function () {
        t.randomizePerimeterEnsemble(!1);
    }),
    document.getElementById("perimeterEnsembleVarianceVal").addEventListener("keypress", function (e) {
        13 === e.keyCode && t.randomizePerimeterEnsemble(!1);
    }),
    window.addEventListener("resize", function () {
        t.resizeOverlays();
    }),
    (this._imports = []),
    (this._exports = []),
    (this._user = e.user),
    e.user.metadata))
        "import" === e.user.metadata[i].type ? this._imports.push(e.user.metadata[i]) : "export" === e.user.metadata[i].type && this._exports.push(e.user.metadata[i]);
    this._imports.sort(function (e, t) {
        return e.name == t.name ? 0 : e.name < t.name ? -1 : 1;
    });
    let n = !1,
        s = document.getElementById("loadChannel");
    for (let e = s.options.length - 1; e >= 0; e--) s.options.remove(e);
    for (let t in e.user.channel) {
        let i = document.createElement("option");
        (i.value = i.text = e.user.channel[t]), s.add(i), "Operational" === i.text && (n = !0);
    }
    (this._isTrainingSite = -1 !== window.location.hostname.indexOf("training")),
        !this._isTrainingSite && n ? (document.getElementById("loadChannel").value = this._channelSharedRuns = "Operational") : (document.getElementById("loadChannel").value = this._channelSharedRuns = "Training"),
        (document.getElementById("loadChannel").onchange = function (e) {
            t._overlay.isShown("showSharedRuns") && ((t._channelSharedRuns = this.value), t._showSharedRuns());
        });
    var o = document.getElementById("loadGroup");
    for (i = o.options.length - 1; i >= 0; i--) o.options.remove(i);
    (option = document.createElement("option")), (option.text = option.value = "all users"), o.add(option);
    var l = this._webview.loginInfo.groups.slice();
    for (i in (l.sort(), l)) "firemod" !== l[i] && ((option = document.createElement("option")), (option.text = option.value = l[i]), o.add(option));
    for (
        o.onchange = function () {
            $.fn.DataTable.isDataTable("#sharedRunsTable") &&
                ("all users" === this.value ? $("#sharedRunsTable").DataTable().column("group:name").search("").draw() : $("#sharedRunsTable").DataTable().column("group:name").search(this.value).draw());
        },
            this._selectedImportLayerName = "",
            document.getElementById("importFilterSelect").onchange = function () {
                (t._selectedImportLayerName = this.value),
                    t._lastImportedIgnitionsSlider.noUiSlider.updateOptions({
                        range: { min: 1, max: t._importedLayers[t._selectedImportLayerName].getLayers().length + t._importedFilteredLayers[t._selectedImportLayerName].getLayers().length },
                    }),
                    (t._reverseImportedIgnitionsButtonVal = t._reverseImportedIgnitionsVal[t._selectedImportLayerName]);
            },
            this._reverseImportedIgnitionsButtonVal = !1,
            document.getElementById("reverseImportedIgnitions").onclick = function () {
                (t._reverseImportedIgnitionsButtonVal = !t._reverseImportedIgnitionsButtonVal),
                    t._reverseImportedIgnitionsButtonVal ? (this.classList.remove("fireButton"), this.classList.add("selFireButton")) : (this.classList.remove("selFireButton"), this.classList.add("fireButton")),
                    t._reverseImportedIgnitions();
            },
            document.getElementById("showImportsLegend").onclick = function () {
                t._overlay.isShown("importsLegend")
                    ? (this.classList.remove("selFireButton"), this.classList.add("fireButton"), t._overlay.close("importsLegend"))
                    : (this.classList.remove("fireButton"), this.classList.add("selFireButton"), t._updateImportsLegend());
            },
            this._map.on("move", function () {
                t._overlay.isShown("importsLegend") && t._updateImportsLegend();
            }),
            o = document.getElementById("forecastForFireSelect"),
            i = o.options.length - 1;
        i >= 0;
        i--
    )
        o.options.remove(i);
    let d = e.WeatherForecastLayer.getModels();
    for (i in d) (option = document.createElement("option")), (option.text = e.WeatherForecastLayer.getModelTitle(i)), (option.value = i), o.add(option);
    (o.selectedIndex = 1),
        (this._weatherForecastModel = o.value),
        (o.onchange = function () {
            (t._weatherForecastModel = this.value), "forecast" === t._fireOptions.conditions && t.setFireConditions("forecast");
        });
    let m = document.getElementById("fuelForFire");
    if (((m.innerHTML = ""), (e.user.fuel && 0 !== e.user.fuel.length) || (console.log("no fuels for user; adding default", Constants.defaultFuel), (e.user.fuel = [Constants.defaultFuel])), 1 === e.user.fuel.length)) {
        let t = document.createElement("SPAN");
        (t.innerHTML = e.user.fuel[0]), m.appendChild(t);
    } else {
        (o = document.createElement("SELECT")), m.appendChild(o);
        let i = 0;
        for (let t in e.user.fuel) (option = document.createElement("option")), (option.text = option.value = e.user.fuel[t]), o.add(option), Constants.defaultFuel === e.user.fuel[t] && (i = t);
        (o.selectedIndex = i),
            (this._fireOptions.fuelType = e.user.fuel[i]),
            (o.onchange = function () {
                (t._fireOptions.fuelType = this.value), document.getElementById("perimeterResolution").onkeyup();
            });
    }
    (document.getElementById("perimeterResolution").onkeyup = function () {
        let i,
            a = parseInt(this.value);
        if (isNaN(a)) i = "Perimeter resolution must be a number.";
        else
            for (let r in e.user.metadata) {
                let n = e.user.metadata[r];
                if ("paramset" === n.type && "fuel" === n.paramset_type && n.name === t._fireOptions.fuelType) {
                    n.range && n.range.perimeterResolution && n.range.perimeterResolution.hasOwnProperty("max")
                        ? a > n.range.perimeterResolution.max && (i = "Perimeter resolution must be less than " + n.range.perimeterResolution.max + " for<br/>" + t._fireOptions.fuelType)
                        : a > 500 && (i = "Perimeter resolution must be less than 500m."),
                        n.range &&
                            n.range.perimeterResolution &&
                            n.range.perimeterResolution.hasOwnProperty("min") &&
                            a < n.range.perimeterResolution.min &&
                            (i = "Perimeter resolution must be at least " + n.range.perimeterResolution.min + "m for<br/>" + t._fireOptions.fuelType);
                    break;
                }
            }
        i
            ? ((document.getElementById("advancedFireStatusText").innerHTML = i), (document.getElementById("advancedFireDoneButton").disabled = !0))
            : ((document.getElementById("advancedFireStatusText").innerHTML = ""), (document.getElementById("advancedFireDoneButton").disabled = !1), (t._fireOptions.perimeterResolution = a));
    }),
        (document.getElementById("perimeterResolution").value = 60);
}),
    (FireModeling.prototype = {
        enable: function () {
            var e = this;
            (this._fireStatusControl = L.control({ position: "bottomright" })),
                (this._fireStatusControl.onAdd = function (e) {
                    var t = document.createElement("div");
                    return $("#fireStatusControl").appendTo(t), t;
                }),
                this._map.addControl(this._fireStatusControl),
                (this._barrierLayers.active = L.featureGroup()),
                (this._barrierLayers.active.name = "Active"),
                this._mapLayers.addNestedOverlay(this._barrierLayers.active, "Active", "Barriers"),
                (this._barrierLayers.inactive = L.featureGroup()),
                (this._barrierLayers.inactive.name = "Inactive"),
                this._mapLayers.addNestedOverlay(this._barrierLayers.inactive, "Inactive", "Barriers"),
                this._map
                    .on("overlayadd", this._bringToFrontBarriers, this)
                    .on("overlayremove", this._overlayRemoveEvent, this)
                    .on("draw:drawstart", this._drawStartEvent, this)
                    .on("draw:created", this._drawCreatedEvent, this)
                    .on("draw:deleted", this._drawDeletedEvent, this)
                    .on("draw:edited", this._drawEditedEvent, this),
                (this._drawnLayers = new L.FeatureGroup());
            var t = { shapeOptions: this._selectedIgnitionStyle },
                i = { allowIntersection: !1, metric: !1, shapeOptions: this._activeBarrierStyle };
            (this._drawControl = new L.Control.Draw({ draw: { circle: !1, marker: { icon: this._selectedIgnitionPointIcon }, polyline: i, polygon: t, rectangle: t }, edit: { featureGroup: this._drawnLayers, edit: !0, remove: !0 } })),
                this._map.addControl(this._drawControl),
                (this._showFireDialogButton = L.easyButton(
                    "fa-fire fa-lg easyButtonLg",
                    function (t, i) {
                        e._ignitionLayer ? (e.resizeOverlays(), e._firemap.checkPassword("manualFireOverlay")) : e._overlay.showMessageOverlay("Must draw or select fire ignition.");
                    },
                    "Configure and run fire model."
                ).addTo(this._map));
            var a = $("#winddir");
            a.roundSlider({ handleSize: 0, handleShape: "square", min: this._fireOptions.winddir.min, max: this._fireOptions.winddir.max, step: 1, startAngle: 90, showTooltip: !1, sliderType: "min-range" }),
                a
                    .on("change", function (t) {
                        e._changeWindDir(t);
                    })
                    .on("drag", function (t) {
                        e._changeWindDir(t);
                    }),
                (this._winddirSlider = a.data("roundSlider"));
            var r = document.getElementById("winddirval");
            (r.value = 180),
                (r.min = this._fireOptions.winddir.min),
                (r.max = this._fireOptions.winddir.max),
                (r.step = 1),
                (r.onchange = function () {
                    var t = (parseInt(this.value) + 180) % 360;
                    0 === t && (t = 360), e._winddirSlider.setValue(t), e._changeWindDir({ value: t });
                }),
                (this._windspeedSlider = this._utils.createSlider({
                    id: "windspeed",
                    start: 5,
                    step: 1,
                    min: this._fireOptions.windspeed.min,
                    max: this._fireOptions.windspeed.max,
                    textId: ["windspeedval"],
                    onset: function (t) {
                        e._updateFireOptions({ type: "windspeed", value: t });
                    },
                })),
                (this._humiditySlider = this._utils.createSlider({
                    id: "humidity",
                    start: 50,
                    step: 1,
                    min: this._fireOptions.humidity.min,
                    max: this._fireOptions.humidity.max,
                    textId: ["humidityval"],
                    onset: function (t) {
                        e._updateFireOptions({ type: "humidity", value: t });
                    },
                })),
                (this._temperatureSlider = this._utils.createSlider({
                    id: "temperature",
                    start: 70,
                    step: 1,
                    min: this._fireOptions.airtemperature.min,
                    max: this._fireOptions.airtemperature.max,
                    range: { min: this._fireOptions.airtemperature.min, "20%": 50, max: this._fireOptions.airtemperature.max },
                    textId: ["temperatureval"],
                    onset: function (t) {
                        e._updateFireOptions({ type: "airtemperature", value: t });
                    },
                })),
                (this._timeSlider = this._utils.createSlider({
                    id: "time",
                    start: 3,
                    step: 1,
                    min: this._fireOptions.hours.min,
                    max: this._fireOptions.hours.max,
                    textId: ["timeval"],
                    onset: function (t) {
                        e._updateFireOptions({ type: "hours", value: t });
                    },
                })),
                (document.getElementById("emberval").oninput = function () {
                    var t = parseInt(document.getElementById("emberval").value);
                    t > e._fireOptions.emberProbability.max
                        ? ((t = e._fireOptions.emberProbability.max), (document.getElementById("emberStatus").innerHTML = '<span style="color:red;">Maximum is 100.</span>'), (document.getElementById("advancedFireDoneButton").disabled = !0))
                        : t < e._fireOptions.emberProbability.min
                        ? ((t = e._fireOptions.emberProbability.min), (document.getElementById("emberStatus").innerHTML = '<span style="color:red;">Minimum is 0.</span>'), (document.getElementById("advancedFireDoneButton").disabled = !0))
                        : ((document.getElementById("emberStatus").innerHTML = ""), (document.getElementById("advancedFireDoneButton").disabled = !1)),
                        (e._fireOptions.emberProbability.v = t);
                }),
                (this._listSharedRunsButton = L.easyButton(
                    "fa-folder-open fa-lg easyButtonLg",
                    function (t, i) {
                        e._firemap.checkPassword(e._showSharedRuns, null, e);
                    },
                    "List shared fires."
                ).addTo(this._map)),
                (this._fireStartTime = document.getElementById("starttimeval").flatpickr({
                    disableMobile: !0,
                    dateFormat: this._FORMAT_FLATPICKR_FIRE_START_TIME,
                    defaultDate: this._fireOptions.startTime.format(this._FORMAT_MOMENT_FIRE_START_TIME),
                    enableTime: !0,
                    time_24hr: !0,
                    onOpen: function (t, i, a) {
                        e._fireStartTimePickrIsOpen = !0;
                    },
                    onClose: function (t, i, a) {
                        (e._fireStartTimePickrIsOpen = !1), (e._fireOptions.startTime = moment(t[0]));
                    },
                    onChange: function (t, i, a) {
                        (e._fireOptions.startTime = moment(t[0])), e._fireStartTimePickrIsOpen && e._fireStartTimeInterval && (window.clearInterval(e._fireStartTimeInterval), (e._fireStartTimeInterval = null));
                    },
                })),
                this._setFireStartTime(),
                (this._wxStationStartTime = document.getElementById("wxStationStartTimeVal").flatpickr({
                    maxDate: moment().toDate(),
                    disableMobile: !0,
                    dateFormat: this._FORMAT_FLATPICKR_FIRE_START_TIME,
                    defaultDate: this._wxStationStartTimeVal,
                    enableTime: !0,
                    time_24hr: !0,
                    disable: [
                        function (e) {
                            return e.getTime() > Date.now();
                        },
                    ],
                    onChange: function (t, i, a) {
                        (e._wxStationStartTimeIsNow = !1), (e._wxStationStartTimeVal = i);
                    },
                    onClose: function (t, i, a) {
                        e.setFireConditions("station"), e.setFuelMoistureConditions("station"), e._setFireStartTime(t);
                    },
                })),
                (this._importedLayers = {}),
                (this._importLayersButton = L.easyButton(
                    "fa-refresh fa-lg easyButtonLg",
                    function (t, i) {
                        var a = document.getElementById("importButtons"),
                            r = this;
                        this.disable(), (a.innerHTML = "");
                        for (let i in e._imports)
                            ((t = document.createElement("button")).className = "fireButton"),
                                (t.innerHTML = e._imports[i].name),
                                (t.onclick = function () {
                                    e._overlay.close("importOverlay"), e._import(e._imports[i]);
                                }),
                                a.appendChild(t),
                                a.appendChild(document.createElement("br"));
                        ((t = document.createElement("button")).className = "fireButton"),
                            (t.innerHTML = "Cancel"),
                            (t.onclick = function () {
                                e._overlay.close("importOverlay"), r.enable();
                            }),
                            a.appendChild(t),
                            e._overlay.show("importOverlay");
                    },
                    "Import ignitions and barriers."
                ).addTo(this._map)),
                this._utils.adjustIconsInButtons(),
                (document.getElementById("emberval").value = 0),
                (this._lastImportedIgnitionsVal = 10),
                (this._lastImportedIgnitionsSlider = this._utils.createSlider({ id: "lastImportedIgnitions", start: this._lastImportedIgnitionsVal, step: 1, min: 1, max: 10, textId: ["lastImportedIgnitionsVal"], nopips: !0 })),
                (this._importedFilteredLayers = {}),
                (this._reverseImportedIgnitionsVal = {}),
                this._lastImportedIgnitionsSlider.noUiSlider.on("update", function () {
                    e._updateShownImportedIgnitions();
                });
        },
        disable: function () {
            var e,
                t = this,
                i = ["downloadOverlay", "ensembleInfoOverlay", "fireAreaOverlay", "fireInfoOverlay", "fireWeather", "manualFireOverlay", "queryPopulationOverlayRect", "queryPopulationOverlayPolygon", "shareFireRun"];
            for (e in (this._overlay.isShown("showSharedRuns") && this.closeSharedRuns(), i)) this._overlay.isShown(i[e]) && this._overlay.close(i[e]);
            for (e in (this._playFireTimer && window.clearInterval(this._playFireTimer),
            this._fireTimeSlider && this._fireTimeSlider.noUiSlider.destroy(),
            this._ensFireSlider && this._ensFireSlider.noUiSlider.destroy(),
            this._importedLayers))
                this._map.removeLayer(this._importedLayers[e]);
            (this._importedLayers = null),
                this._importLayersButton.removeFrom(this._map),
                (this._importedFilteredLayers = this._reverseImportedIgnitionsVal = null),
                this._ignitionLayers.eachLayer(function (e) {
                    t._map.removeLayer(e), t._mapLayers.removeLayer(e);
                }),
                this._ignitionLayers.clearLayers(),
                this._fireLayers.eachLayer(function (e) {
                    t._map.removeLayer(e), t._mapLayers.removeLayer(e);
                }),
                this._fireLayers.clearLayers(),
                this._fireStartTime.destroy(),
                this._wxStationStartTime.destroy(),
                this._listSharedRunsButton.removeFrom(this._map),
                this._windspeedSlider.noUiSlider.destroy(),
                this._humiditySlider.noUiSlider.destroy(),
                this._temperatureSlider.noUiSlider.destroy(),
                this._timeSlider.noUiSlider.destroy(),
                $("#winddir").roundSlider("destroy"),
                this._showFireDialogButton.removeFrom(this._map),
                this._map.removeControl(this._drawControl),
                this._drawnLayers.eachLayer(function (e) {
                    t._map.removeLayer(e);
                }),
                (this._drawnLayers = null),
                this._map
                    .off("overlayadd", this._bringToFrontBarriers, this)
                    .off("overlayremove", this._overlayRemoveEvent, this)
                    .off("draw:drawstart", this._drawStartEvent, this)
                    .off("draw:created", this._drawCreatedEvent, this)
                    .off("draw:deleted", this._drawDeletedEvent, this)
                    .off("draw:edited", this._drawEditedEvent, this),
                this._mapLayers.removeLayer(this._barrierLayers.active),
                (this._barrierLayers.active = null),
                this._mapLayers.removeLayer(this._barrierLayers.inactive),
                (this._barrierLayers.inactive = null),
                (document.getElementById("fireStatusControl").style.display = "none"),
                this._fireStartTimeInterval && (window.clearInterval(this._fireStartTimeInterval), (this._fireStartTimeInterval = null)),
                this._overlay.close("importsFilterControl"),
                this._lastImportedIgnitionsSlider.noUiSlider.destroy();
        },
        addIgnitionPoint: function (e, t, i) {
            this._drawnLayers.addLayer(e), this._createIgnitionLayer(e, t, i);
        },
        addIgnitionAtLatLng: function (e, t, i, a) {
            let r = L.marker(e, { icon: this._selectedIgnitionPointIcon });
            (r.feature = { properties: t }), this.addIgnitionPoint(r, i, a);
        },
        _drawStartEvent: function (e) {
            "polyline" != e.layerType || this._ignitionLayer || this._overlay.showMessageOverlay("Must draw fire perimeter first.");
        },
        _drawCreatedEvent: function (e) {
            this._drawnLayers.addLayer(e.layer),
                "polyline" == e.layerType
                    ? (this._createBarrierLayer(e.layer), this._barrierLayers.active.addTo(this._map), this._barrierLayers.inactive.addTo(this._map))
                    : "rectangle" == e.layerType
                    ? ((this._globalLayer = e.layer), this._map.addLayer(this._globalLayer), this._overlay.show("queryPopulationOverlayRect"))
                    : "polygon" == e.layerType
                    ? ((this._globalLayer = e.layer), this._map.addLayer(this._globalLayer), this._overlay.show("queryPopulationOverlayPolygon"))
                    : this._createIgnitionLayer(e.layer);
        },
        _drawDeletedEvent: function (e) {
            var t = this;
            e.layers.eachLayer(function (e) {
                t._map.removeLayer(e), t._drawnLayers.removeLayer(e), t._barrierLayers.active.removeLayer(e), t._barrierLayers.inactive.removeLayer(e), t._ignitionLayer == e && (t._ignitionLayer = null);
            });
        },
        _drawEditedEvent: function (e) {
            var t = [];
            e.layers.eachLayer(function (e) {
                e.isPopulationLayer && (e.closePopup(), e.unbindPopup(), t.push(e));
            }),
                t.length > 0 && this._getPopulation(t, !0);
        },
        _overlayRemoveEvent: function (e) {
            this._selectedFire && e.layer == this._selectedFire.layer ? this.playFire("stop") : e.layer.ensembleLayer && this._map.removeLayer(e.layer.ensembleLayer);
        },
        _setIgnitionStyle: function (e, t, i) {
            var a = this;
            e.setStyle
                ? (e.setStyle(t),
                  e.eachLayer &&
                      e.eachLayer(function (e) {
                          a._setIgnitionStyle(e, t, i);
                      }))
                : e.setIcon && e.setIcon(i);
        },
        _setSelectedIgnitionStyle: function (e) {
            e.parentLayer
                ? this._setIgnitionStyle(e, this._selectedEnsIgnitionStyle, this._selectedEnsIgnitionPointIcon)
                : (this._setIgnitionStyle(e, this._selectedIgnitionStyle, this._selectedIgnitionPointIcon), e.ensembleLayer && this._setIgnitionStyle(e.ensembleLayer, this._selectedEnsIgnitionStyle, this._selectedEnsIgnitionPointIcon));
        },
        _setUnselectedIgnitionStyle: function (e) {
            e.parentLayer
                ? this._setIgnitionStyle(e, this._unselectedEnsIgnitionStyle, this._unselectedIgnitionPointIcon)
                : (this._setIgnitionStyle(e, this._unselectedIgnitionStyle, this._unselectedIgnitionPointIcon),
                  e.ensembleLayer && this._setIgnitionStyle(e.ensembleLayer, this._unselectedEnsIgnitionStyle, this._unselectedIgnitionPointIcon));
        },
        _selectIgnitionLayer: function (e) {
            this._ignitionLayer && this._setUnselectedIgnitionStyle(this._ignitionLayer), (this._ignitionLayer = e), this._setSelectedIgnitionStyle(this._ignitionLayer);
        },
        _createIgnitionLayer: function (e, t, a) {
            var r,
                n = this;
            this._ignitionLayers.addLayer(e),
                this._selectIgnitionLayer(e),
                (this._ignitionLayer.fireNum = this._fireNum++),
                this._ignitionLayer.addTo(this._map),
                (r = a || "Ignition: " + this._ignitionLayer.fireNum),
                this._mapLayers.addNestedOverlay(this._ignitionLayer, r, t),
                this._ignitionLayer
                    .on("click", function (e) {
                        n._map.contextmenu.hide(), n._selectIgnitionLayer(e.target);
                    })
                    .on("dblclick", function (e) {
                        let t,
                            a = null;
                        if (("Point" != e.target.toGeoJSON().geometry.type && (a = Math.round(turf.area.default(e.target.toGeoJSON()) * Constants.SQM_TO_ACRES)), e.target.feature && e.target.feature.properties)) {
                            let r = Object.keys(e.target.feature.properties),
                                s = n._getImportedIgnitionName(e.target, !0),
                                o = [],
                                l = [];
                            for (i in (r.sort(), r)) {
                                let t = e.target.feature.properties[r[i]],
                                    a = r[i].toLowerCase();
                                t &&
                                    "objectid" != a &&
                                    "globalid" != a &&
                                    "_import_name" != a &&
                                    "fid" != a &&
                                    "id" != a &&
                                    "shape__length" != a &&
                                    "shape__area" != a &&
                                    "_title" != a &&
                                    (("created_date" !== a && "creationdate" !== a && "modify_date" !== a && "editdate" !== a) || (t = moment(t).local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")), o.push(r[i]), l.push(t));
                            }
                            if (0 == o.length) t = '<div style="font-size:14px;">Ignition Acres is ' + a + "</div>";
                            else {
                                let r;
                                for (i in ("unknown" != s ? (r = s) : e.target.feature.properties._title && (r = e.target.feature.properties._title),
                                (t = r ? '<div style="font-size:16px;font-weight: bold;">' + r + "</div>" : ""),
                                null != a && (t += '<div style="font-size:14px; font-weight:bold;">Acres: ' + a + "</div>"),
                                o))
                                    t += '<div style="font-size:14px;padding-right:10px;">' + o[i] + ": " + l[i] + "</div>";
                            }
                        } else null != a && (t = '<div class="titleText" style="font-weight:bold;">Acres ' + a + "</div>");
                        L.popup()
                            .setLatLng(e.latlng)
                            .setContent(t || '<div style="font-size:14px;">Unknown</div>')
                            .openOn(n._map);
                    });
        },
        _createBarrierLayer: function (e) {
            var t = this;
            this._barrierLayers.active.addLayer(e),
                e.on("click", function (i) {
                    t._map.contextmenu.hide(),
                        t._barrierLayers.active.hasLayer(e)
                            ? (e.setStyle(t._inactiveBarrierStyle), t._barrierLayers.active.removeLayer(e), t._barrierLayers.inactive.addLayer(e))
                            : (e.setStyle(t._activeBarrierStyle), t._barrierLayers.inactive.removeLayer(e), t._barrierLayers.active.addLayer(e));
                });
        },
        _updateFireOptions: function (e) {
            var t,
                i,
                a = e.type,
                r = ["airtemperature", "windspeed", "winddir", "humidity"];
            if ("hours" === a || "all" === a)
                if (((this._fireOptions.hours.v = this._timeSlider.noUiSlider.get()), "forecast" === this._fireOptions.conditions || ("station" === this._fireOptions.conditions && !this._wxStationStartTimeIsNow)))
                    this.setFireConditions(this._fireOptions.conditions);
                else {
                    var n = (60 * this._fireOptions.hours.v) / this._fireOptions.timestep.v;
                    for (i in r) {
                        var s = r[i];
                        if (this._fireOptions[s].v.length > n) this._fireOptions[s].v = this._fireOptions[s].v.slice(0, n);
                        else if (this._fireOptions[s].v.length < n) for (; this._fireOptions[s].v.length < n; ) this._fireOptions[s].v.push(this._fireOptions[s].v[this._fireOptions[s].v.length - 1]);
                    }
                }
            if ("airtemperature" === a || "all" === a) for (t in ((v = this._temperatureSlider.noUiSlider.get()), this._fireOptions.airtemperature.v)) this._fireOptions.airtemperature.v[t] = v;
            if ("humidity" === a || "all" === a) for (t in ((v = this._humiditySlider.noUiSlider.get()), this._fireOptions.humidity.v)) this._fireOptions.humidity.v[t] = v;
            if ("windspeed" === a || "all" === a) for (t in ((v = this._windspeedSlider.noUiSlider.get()), this._fireOptions.windspeed.v)) this._fireOptions.windspeed.v[t] = v;
            if ("winddir" === a || "all" === a) for (t in ((v = parseInt(document.getElementById("winddirval").value)), this._fireOptions.winddir.v)) this._fireOptions.winddir.v[t] = v;
            "hours" !== a &&
                "all" !== a &&
                ((this._fireOptions.conditions = "manual"), this._utils.updateStatus("fireConfigWeatherStatus", "manually updated."), this._firemap.disableButtons(!1), this._changeButtonSelection("selFireButton", []));
        },
        _updateFireConfigEnsembleStatus: function () {
            this._ignitionLayer.ensembleLayer ? this._utils.updateStatus("fireConfigEnsembleStatus", this._ignitionLayer.ensembleLayer.getLayers().length + 1 + " perimeters.") : this._utils.updateStatus("fireConfigEnsembleStatus", "none.");
        },
        _getLatLngOfIgnition: function () {
            var e,
                t = this._ignitionLayer.toGeoJSON();
            return t.features && (t = t.features[0]), "Point" === t.geometry.type ? t.geometry.coordinates : ((e = t.geometry.coordinates[0][0]), Array.isArray(e[0]) ? e[0] : e);
        },
        _createIgnitionEnsembleLayer: function (e) {
            var t = this;
            (e.ensembleLayer = L.featureGroup().on("click", function (e) {
                t._map.contextmenu.hide(), t._selectIgnitionLayer(e.target.parentLayer);
            })),
                (e.ensembleLayer.parentLayer = this._ignitionLayer);
        },
        _addIgnitionEnsembleToMap: function (e) {
            this._setSelectedIgnitionStyle(e.ensembleLayer), e.ensembleLayer.addTo(this._map), e.bringToFront ? e.bringToFront() : e.setZIndexOffset && e.setZIndexOffset(1e3);
        },
        _createFireEnsembleLayers: function (e) {
            var t = L.featureGroup().addTo(this._map);
            return (
                (t.setOpacity = function (e) {
                    this.eachLayer(function (t) {
                        t.setOpacity(e);
                    });
                }),
                this._mapLayers.addOverlay(t, e || "Fire Ensemble Perimeters"),
                t
            );
        },
        _parseAndAddFireLayer: function (e, t) {
            var i, a, r;
            for (i in t) t[i].hasOwnProperty("perimeters") ? (r = JSON.parse(t[i].perimeters)) : t[i].hasOwnProperty("area") && ((e.times = t[i].time), (e.area = t[i].area));
            if (r) {
                let t = turf.area.default(e.ignitionLayer.toGeoJSON()) * Constants.SQM_TO_ACRES;
                for (a in e.area) (e.area[a] *= Constants.SQM_TO_ACRES), (e.area[a] += t);
                r.features.sort(function (e, t) {
                    return t.properties.Elapsed_Mi - e.properties.Elapsed_Mi;
                }),
                    this._addFireLayer(e, r);
            }
        },
        _bringToFrontBarriers: function () {
            this._map.hasLayer(this._barrierLayers.active) && this._barrierLayers.active.bringToFront(), this._map.hasLayer(this._barrierLayers.inactive) && this._barrierLayers.inactive.bringToFront();
        },
        _addFireLayer: function (e, t) {
            var i = this;
            (e.perimeters = t), (e.opacity = 1);
            var a = L.geoJson(t, {
                style: function (t) {
                    var a;
                    return (
                        "Fill" === e.displayType ? (a = { opacity: 0, fillOpacity: 1, fill: !0 }) : "Lines" === e.displayType && (a = { opacity: 1, fillOpacity: 0, fill: !1, weight: 2 }),
                        (a.fillColor = a.color = i._fireColors[((t.properties.Elapsed_Mi - e.timestep.v) / e.timestep.v) % i._fireColors.length]),
                        (a.displayType = e.displayType),
                        a
                    );
                },
                onEachFeature: function (t, r) {
                    r.on("click", function (t) {
                        i._map.contextmenu.hide(),
                            e.ignitionLayer.parentLayer ? i._selectIgnitionLayer(e.ignitionLayer.parentLayer) : i._selectIgnitionLayer(e.ignitionLayer),
                            i._showFireInfo(e),
                            i._overlay.isShown("fireWeather") && i._showSelectedFireWeather(),
                            i._overlay.isShown("fireAreaOverlay") && i._showFireAreaChart();
                    }),
                        r.on("mouseover", function (e) {
                            var t;
                            "Fill" === e.layer.options.displayType && e.layer.options.fillOpacity > 0
                                ? (t = { opacity: 1, weight: 2, color: "black" })
                                : "Lines" === e.layer.options.displayType && e.layer.options.opacity > 0 && (t = { opacity: 1, color: "black" }),
                                e.target.setStyle
                                    ? e.target.setStyle(t)
                                    : e.target.eachLayer &&
                                      e.target.eachLayer(function (e) {
                                          e.setStyle(t);
                                      }),
                                L.Browser.ie || L.Browser.opera || (a.bringToFront(), i._bringToFrontBarriers());
                        }),
                        r.on("mouseout", function (a) {
                            var r;
                            "Fill" === a.layer.options.displayType && a.layer.options.fillOpacity > 0
                                ? (r = { opacity: 0, color: i._fireColors[((t.properties.Elapsed_Mi - e.timestep.v) / e.timestep.v) % i._fireColors.length] })
                                : "Lines" === a.layer.options.displayType && a.layer.options.opacity > 0 && (r = { color: i._fireColors[((t.properties.Elapsed_Mi - e.timestep.v) / e.timestep.v) % i._fireColors.length] }),
                                a.target.setStyle
                                    ? a.target.setStyle(r)
                                    : a.target.eachLayer &&
                                      a.target.eachLayer(function (e) {
                                          e.setStyle(r);
                                      });
                        });
                },
                contextmenu: !0,
                contextmenuItems: [
                    {
                        text: "Copy Fire Settings",
                        callback: function (t) {
                            (i._copiedFireOptions = {
                                perimeterResolution: e.perimeterResolution,
                                fuelType: e.fuelType,
                                fuelMoisture: { v: e.fuelMoisture.v.slice() },
                                emberProbability: { v: e.emberProbability.v },
                                timestep: { v: e.timestep.v },
                                hours: { v: e.hours.v },
                                winddir: { v: e.winddir.v.slice() },
                                windspeed: { v: e.windspeed.v.slice() },
                                humidity: { v: e.humidity.v.slice() },
                                airtemperature: { v: e.airtemperature.v.slice() },
                                startTime: e.startTime,
                            }),
                                (document.getElementById("pasteFireSettingsButton").disabled = !1);
                        },
                    },
                    { separator: !0 },
                    {
                        text: "Animate",
                        callback: function (t) {
                            i._selectedFire != e && t.relatedTarget.fireEvent("click"), i.playFire("start");
                        },
                    },
                    { separator: !0 },
                    {
                        text: "Show ETA",
                        callback: function (t) {
                            i._selectedFire != e && t.relatedTarget.fireEvent("click"), i._showFireLegend();
                        },
                    },
                    {
                        text: "Show Weather",
                        callback: function (t) {
                            i._selectedFire != e && t.relatedTarget.fireEvent("click"), i._overlay.isShown("fireWeather") || i._overlay.show("fireWeather"), i._showFireWeather(e, !1);
                        },
                    },
                    {
                        text: "Show Area",
                        callback: function (t) {
                            i._selectedFire != e && t.relatedTarget.fireEvent("click"), i._overlay.isShown("fireAreaOverlay") || i._overlay.show("fireAreaOverlay"), i._showFireAreaChart(e);
                        },
                    },
                    { separator: !0 },
                    {
                        text: "Share",
                        callback: function (t) {
                            i._selectedFire != e && t.relatedTarget.fireEvent("click"), i._firemap.checkPassword("shareFireRun");
                        },
                    },
                    { separator: !0 },
                    {
                        text: "Download",
                        callback: function (t) {
                            i._selectedFire != e && t.relatedTarget.fireEvent("click"), i._firemap.overlay.show("downloadOverlay");
                        },
                    },
                ],
            });
            (a.setOpacity = function (t) {
                (e.opacity = t),
                    this.eachLayer(function (i) {
                        "Fill" === e.displayType ? i.setStyle({ fillOpacity: t }) : "Lines" === e.displayType && i.setStyle({ opacity: t });
                    });
            }),
                e.ensembleFireLayers
                    ? (e.ensembleFireLayers.addLayer(a), (a.ignitionLayer = e.ignitionLayer), this._fireLayers.addLayer(e.ensembleFireLayers))
                    : (a.addTo(this._map), this._mapLayers.addOverlay(a, e.fireName || "Fire Model Perimeters"), this._fireLayers.addLayer(a)),
                (e.layer = a),
                this._bringToFrontBarriers();
        },
        manualFireRun: function () {
            var e,
                t = this;
            if ((this._overlay.close("manualFireOverlay"), !this._fireOptions.startTime || !this._fireOptions.startTime.isValid()))
                return this._overlay.showMessageOverlay("Start Time is invalid. Please enter a time HH:MM where HH is 00 to 24, and MM is 00 to 59."), void this.overlay.show("manualFireOverlay");
            this._ignitionLayer.ensembleLayer && (e = this._createFireEnsembleLayers()),
                this._singleFireRun(this._ignitionLayer, e),
                this._ignitionLayer.ensembleLayer &&
                    this._ignitionLayer.ensembleLayer.eachLayer(function (i) {
                        t._singleFireRun(i, e);
                    });
        },
        _singleFireRun: function (e, t) {
            var i,
                a = this,
                r = e.toGeoJSON();
            if ((r.features && (r = r.features[0]), "Point" === r.geometry.type)) {
                var n = r.geometry.coordinates[1],
                    s = r.geometry.coordinates[0];
                i = L.polygon([
                    L.latLng([n, s]),
                    L.latLng([n, s + Constants.sixtyMeterDiffLatLng]),
                    L.latLng([n + Constants.sixtyMeterDiffLatLng, s + Constants.sixtyMeterDiffLatLng]),
                    L.latLng([n + Constants.sixtyMeterDiffLatLng, s]),
                    L.latLng([n, s]),
                ]);
            } else i = e;
            var o = {
                perimeterResolution: this._fireOptions.perimeterResolution,
                fuelType: this._fireOptions.fuelType,
                fuelMoisture: { v: this._fireOptions.fuelMoisture.v },
                emberProbability: { v: this._fireOptions.emberProbability.v },
                timestep: { v: this._fireOptions.timestep.v },
                hours: { v: this._fireOptions.hours.v },
                winddir: { v: this._fireOptions.winddir.v.slice() },
                windspeed: { v: this._fireOptions.windspeed.v.slice() },
                humidity: { v: this._fireOptions.humidity.v.slice() },
                airtemperature: { v: this._fireOptions.airtemperature.v.slice() },
                startTime: this._fireOptions.startTime.clone(),
                ignitionLayer: e,
                barrierLayers: L.layerGroup(this._barrierLayers.active.getLayers()),
                ensembleFireLayers: t,
            };
            (o.displayType = t ? "Lines" : "Fill"),
                this._numRunFires++,
                1 === this._numRunFires && ((document.getElementById("fireStatusControl").style.display = "block"), (this._fireSpinner = new Spinner({ left: "15px", scale: 0.5 }).spin(document.getElementById("fireSpinner")))),
                this._webview
                    .run({
                        reqType: "POST",
                        wf_name: "FarsiteManual",
                        wf_param: {
                            ignition: JSON.stringify(i.toGeoJSON()),
                            windDirection: o.winddir.v,
                            windSpeed: o.windspeed.v,
                            humidity: o.humidity.v,
                            temperature: o.airtemperature.v,
                            hours: o.hours.v,
                            barriers: JSON.stringify(o.barrierLayers.toGeoJSON()),
                            emberProbability: o.emberProbability.v,
                            fuelMoisture: o.fuelMoisture.v,
                            perimeterResolution: o.perimeterResolution,
                        },
                        wf_paramset: { fuel: o.fuelType },
                    })
                    .always(function () {
                        a._numRunFires--, 0 === a._numRunFires && a._fireSpinner.stop();
                    })
                    .fail(function (e) {
                        console.log("Error: " + e),
                            -1 !== e.indexOf("Unable to determine type of input of") || -1 !== e.indexOf("Unable to open datasource")
                                ? a._overlay.showMessageOverlay("Fire ignition on non-burnable fuel model. Move ignition to a burnable location.")
                                : -1 != e.indexOf("Execution timeout")
                                ? a._overlay.showMessageOverlay("Model timeout. Try reducing burn time.", { overlay: "manualFireOverlay" })
                                : -1 != e.indexOf("No covering file found")
                                ? a._overlay.showMessageOverlay("Fire ignition location currently not supported.")
                                : "Unauthorized" === e
                                ? a._firemap.checkPassword("manualFireOverlay", "Wrong username or password.")
                                : 0 === e.indexOf("Permission denied: ")
                                ? a._firemap.checkPassword("manualFireOverlay", e.substring("Permission denied: ".length))
                                : 0 === e.indexOf("Permission denied setting paramset")
                                ? a._overlay.showMessageOverlay("Permission denied setting fuel.<br/>Change fuel.", { overlay: "manualFireOverlay" })
                                : alert("Error running fire model.\nSee console for details.");
                    })
                    .done(function (e) {
                        a._parseAndAddFireLayer(o, e.responses);
                    });
        },
        _changeWindDir: function (e) {
            (document.getElementById("winddirval").value = (e.value + 180) % 360), this._updateFireOptions({ type: "winddir" });
        },
        _changeButtonSelection: function (e, t, i) {
            var a,
                r,
                n,
                s = { manualFireOverlay: ["wxSantaAna", "wxForecast", "wxEdit", "wxNearest", "wxChoose", "wxNow", "wxStationStartTimeVal", "wxWindAverage", "wxWindGust"], fuelMoistureOverlay: ["fuelMoistureNearest", "fuelMoistureChoose"] }[
                    i || "manualFireOverlay"
                ];
            for (a in ("string" == typeof t && (t = [t]), t)) document.getElementById(t[a]).classList.add(e);
            for (a in s) {
                for (r in ((n = !1), t))
                    if (s[a] == t[r]) {
                        n = !0;
                        break;
                    }
                n || document.getElementById(s[a]).classList.remove(e);
            }
        },
        setFuelMoistureConditions: function (e, t) {
            var a = this;
            function r(e) {
                var t, r, n, s, o, l;
                for (i in e)
                    if ("number" == typeof e[i]) e[i] = Math.round(e[i]);
                    else for (j in e[i]) e[i][j] = Math.round(e[i][j]);
                (t = a._fuelMoistureTable ? a._fuelMoistureTable.getData() : a._fireOptions.fuelMoisture.v),
                    "number" == typeof e.ten_hr
                        ? ((r = e.ten_hr), (s = e.one_hr), (n = e.hundred_hr), (o = e.live_herb), (l = e.live_woody))
                        : ((r = e.ten_hr[0]), (s = e.one_hr[0]), (n = e.hundred_hr[0]), e.live_herb && ((o = e.live_herb[0]), (l = e.live_woody[0]))),
                    (a._fireOptions.fuelMoisture.v = [{ model: 0, one_hr: s, ten_hr: r, hundred_hr: n, live_herb: o || t[0].live_herb, live_woody: l || t[0].live_woody }]),
                    a._fuelMoistureTable && a._fuelMoistureTable.setData(a._fireOptions.fuelMoisture.v);
            }
            if ("sa" === e) r({ one_hr: 4, ten_hr: 5, hundred_hr: 6, live_herb: 5, live_woody: 60 });
            else if ("nearest" === e) (this._stationName = null), (this._stationLatLng = this._getLatLngOfIgnition()), this.setFuelMoistureConditions("station");
            else if ("choose" === e)
                this._map.hasLayer(this._WeatherStationsLayer) || this._map.addLayer(this._WeatherStationsLayer),
                    this._WeatherStationsLayer.setWeatherType(2),
                    this._overlay.close("fuelMoistureOverlay"),
                    this._WeatherStationsLayer.chooseStation(
                        function (e) {
                            (a._stationLatLng = e.geometry.coordinates), (a._stationName = e.properties.description.name), a.setFuelMoistureConditions("station"), a._overlay.show("fuelMoistureOverlay");
                        },
                        ["fm_dead_10"]
                    );
            else if ("paste" === e)
                r({
                    one_hr: this._copiedFireOptions.fuelMoisture.v[0].one_hr,
                    ten_hr: this._copiedFireOptions.fuelMoisture.v[0].ten_hr,
                    hundred_hr: this._copiedFireOptions.fuelMoisture.v[0].hundred_hr,
                    live_herb: this._copiedFireOptions.fuelMoisture.v[0].live_herb,
                    live_woody: this._copiedFireOptions.fuelMoisture.v[0].live_woody,
                }),
                    this._utils.updateStatus("fuelMoistureStatus", "pasted fuel moisture settings.");
            else if ("station" === e) {
                var n,
                    s,
                    o = this._firemap.disableButtons(!0, { except: "Cancel", spinner: !0, id: "fuelMoistureOverlay" }),
                    l = this._stationLatLng || this._getLatLngOfIgnition(),
                    d = Constants.urls.pylaski,
                    m = [];
                this._stationName
                    ? (this._utils.updateStatus("fuelMoistureStatus", "getting fuel moisture at " + this._stationName + "."), m.push("fuelMoistureChoose"))
                    : (this._utils.updateStatus("fuelMoistureStatus", "getting fuel moisture at nearest weather station."), m.push("fuelMoistureNearest")),
                    this._wxStationStartTimeIsNow ||
                        ((n = moment(this._wxStationStartTimeVal).subtract(1, "hour").format(this._FORMAT_MESOWEST_TIME)),
                        (s = moment(this._wxStationStartTimeVal, this._FORMAT_MOMENT_FIRE_START_TIME)
                            .add(this._timeSlider.noUiSlider.get() + 1, "hours")
                            .format(this._FORMAT_MESOWEST_TIME))),
                    this._wxStationStartTimeIsNow ? (d += "stations/data/latest?") : (d += "stations/data?from=" + n + "&to=" + s + "&"),
                    (d += "selection=closestTo&lat=" + l[1] + "&lon=" + l[0]),
                    (d += t ? "&observable=fm_dead_10" : "&obsgroup=fuel_moistures&all=true"),
                    (d += $.ajax({ url: d, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "nearestFMData", timeout: 5e3 })
                        .fail(function (e, t) {
                            a._utils.updateStatus("fuelMoistureStatus", "Error retrieving fuel moisture: " + t), a._firemap.disableButtons(!1, { except: "Run", spinner: o, id: "fuelMoistureOverlay" });
                        })
                        .done(function (e) {
                            var l, d, c, u, h;
                            if (e.hasOwnProperty("result") && null === e.result)
                                t
                                    ? (a._utils.updateStatus("fuelMoistureStatus", "Error retrieving conditions: no measurements found."), a._firemap.disableButtons(!1, { except: "Run", spinner: o, id: "fuelMoistureOverlay" }))
                                    : a.setFuelMoistureConditions("station", !0);
                            else if (e.features && e.features.length >= 1 && e.features[0].properties) {
                                var p = e.features[0].properties;
                                function _(e, t) {
                                    return e.hasOwnProperty(t) ? (void 0 !== e[t].value ? e[t].value : e[t]) : null;
                                }
                                if (
                                    ((l = _(p, "fm_dead_1")),
                                    (d = _(p, "fm_dead_10")),
                                    (c = _(p, "fm_dead_100")),
                                    (u = _(p, "fm_live_herb")),
                                    (h = _(p, "fm_live_wood")),
                                    null === d &&
                                        (a._utils.updateStatus("fuelMoistureStatus", "Error retrieving conditions: no measurements found within 10 miles."),
                                        a._firemap.disableButtons(!1, { except: "Run", spinner: o, id: "fuelMoistureOverlay" })),
                                    l && Array.isArray(l) && ((l = l ? l[0] : null), (d = d ? d[0] : null), (c = c ? c[0] : null), (u = u ? u[0] : null), (h = h ? h[0] : null)),
                                    Array.isArray(d))
                                ) {
                                    var y = [];
                                    for (i in p.timestamp) y.push(moment(p.timestamp[i]).diff(moment(a._wxStationStartTimeVal), "minutes"));
                                    var f = [],
                                        g = 60 * a._fireOptions.hours.v;
                                    for (i = 0; i <= g; i += a._fireOptions.timestep.v) f.push(i);
                                    if (((d = everpolate.linear(f, y, d)), l)) l = everpolate.linear(f, y, l);
                                    else for (i in (l = d.slice())) l[i] -= 1;
                                    for (i in l) (l[i] = Math.max(l[i], a._fuelMoistureRanges.one_hr.min)), (l[i] = Math.min(l[i], a._fuelMoistureRanges.one_hr.max));
                                    for (i in d) (d[i] = Math.max(d[i], a._fuelMoistureRanges.ten_hr.min)), (d[i] = Math.min(d[i], a._fuelMoistureRanges.ten_hr.max));
                                    if (c) c = everpolate.linear(f, y, c);
                                    else for (i in (c = d.slice())) c[i] += 1;
                                    for (i in c) (c[i] = Math.max(c[i], a._fuelMoistureRanges.hundred_hr.min)), (c[i] = Math.min(c[i], a._fuelMoistureRanges.hundred_hr.max));
                                    if (u) for (i in (u = everpolate.linear(f, y, u))) (u[i] = Math.max(u[i], a._fuelMoistureRanges.live_herb.min)), (u[i] = Math.min(u[i], a._fuelMoistureRanges.live_herb.max));
                                    if (h) for (i in ((h = everpolate.linear(f, y, h)), u)) (h[i] = Math.max(h[i], a._fuelMoistureRanges.live_woody.min)), (h[i] = Math.min(h[i], a._fuelMoistureRanges.live_woody.max));
                                } else
                                    null === l && (l = d - 1),
                                        (l = Math.max(l, a._fuelMoistureRanges.one_hr.min)),
                                        (l = Math.min(l, a._fuelMoistureRanges.one_hr.max)),
                                        (d = Math.max(d, a._fuelMoistureRanges.ten_hr.min)),
                                        (d = Math.min(d, a._fuelMoistureRanges.ten_hr.max)),
                                        null === c && (c = d + 1),
                                        (c = Math.max(c, a._fuelMoistureRanges.hundred_hr.min)),
                                        (c = Math.min(c, a._fuelMoistureRanges.hundred_hr.max)),
                                        null !== u && ((u = Math.max(u, a._fuelMoistureRanges.live_herb.min)), (u = Math.min(u, a._fuelMoistureRanges.live_herb.max))),
                                        null !== h && ((h = Math.max(h, a._fuelMoistureRanges.live_woody.min)), (h = Math.min(h, a._fuelMoistureRanges.live_woody.max)));
                                r({ ten_hr: d, one_hr: l, hundred_hr: c, live_herb: u, live_woody: h });
                                var v = "";
                                if (
                                    (u ? (v = a._wxStationStartTimeIsNow ? "today's calculated " : "past calculated ") : a._wxStationStartTimeIsNow && (v = "current 10 HR "),
                                    (v += "conditions at " + p.description.name + " station"),
                                    (!a._stationName || a._stationName != p.description.name) && p.hasOwnProperty("distanceFromLocation"))
                                ) {
                                    var w = p.distanceFromLocation.value;
                                    "km" == p.distanceFromLocation.units && (w *= Constants.KM_TO_MI),
                                        isNaN(w) || ((v += " (" + w.toFixed(2) + " miles away"), a._stationName && a._stationName != p.description.name && (v += " from " + a._stationName), (v += ")"));
                                }
                                a._wxStationStartTimeIsNow || (v += " from " + n + " to " + s),
                                    (v += ". "),
                                    u || (v += "Setting 1 HR and 100 HR based on 10 HR."),
                                    a._utils.updateStatus("fuelMoistureStatus", v),
                                    a._firemap.disableButtons(!1, { spinner: o, id: "fuelMoistureOverlay" }),
                                    a._changeButtonSelection("selFireButton", m, "fuelMoistureOverlay");
                            } else a._utils.updateStatus("fuelMoistureStatus", "Error retrieving conditions: no measurements found within 10 miles."), a._firemap.disableButtons(!1, { except: "Run", spinner: o, id: "fuelMoistureOverlay" });
                        }));
            }
        },
        _setWxStationStartTimeToNow: function () {
            let e = new Date();
            this._wxStationStartTime.set("maxDate", e), this._wxStationStartTime.setDate(e, !0), (this._wxStationStartTimeIsNow = !0);
        },
        _setFireStartTime: function (e) {
            if (e) this._fireStartTimeInterval && (window.clearInterval(this._fireStartTimeInterval), (this._fireStartTimeInterval = null)), this._fireStartTime.setDate(e, !0);
            else if (!this._fireStartTimeInterval) {
                let e = new Date();
                this._fireStartTime.setDate(e, !0),
                    this._wxStationStartTime && this._wxStationStartTime.set("maxDate", e),
                    (this._fireStartTimeInterval = window.setInterval(
                        function () {
                            let e = new Date();
                            this._fireStartTime.setDate(e, !0), this._wxStationStartTime.set("maxDate", e);
                        }.bind(this),
                        3e4
                    ));
            }
        },
        setFireConditions: function (e) {
            var t = this;
            function a(e) {
                var i, a, r;
                for (i in e)
                    if ("number" == typeof e[i]) e[i] = Math.round(e[i]);
                    else for (a in e[i]) e[i][a] = Math.round(e[i][a]);
                if (
                    ("number" == typeof e.temp ? t._temperatureSlider.noUiSlider.set(e.temp) : (t._temperatureSlider.noUiSlider.set(e.temp[0]), (t._fireOptions.airtemperature.v = e.temp)),
                    "number" == typeof e.humid ? t._humiditySlider.noUiSlider.set(e.humid) : (t._humiditySlider.noUiSlider.set(e.humid[0]), (t._fireOptions.humidity.v = e.humid)),
                    "number" == typeof e.windspeed ? t._windspeedSlider.noUiSlider.set(e.windspeed) : (t._windspeedSlider.noUiSlider.set(e.windspeed[0]), (t._fireOptions.windspeed.v = e.windspeed)),
                    "number" == typeof e.winddir)
                )
                    r = e.winddir;
                else {
                    for (i in e.winddir) (e.winddir[i] < 0 || e.winddir[i] > 359) && console.log("wind dir!! " + e.winddir[i]);
                    r = e.winddir[0];
                }
                var n = (r + 180) % 360;
                t._winddirSlider.setValue(n), t._changeWindDir({ value: n }), "number" != typeof e.winddir && (t._fireOptions.winddir.v = e.winddir);
            }
            if ((this._wxStationStartTimeIsNow ? this._setFireStartTime() : this._setFireStartTime(moment(this._wxStationStartTimeVal).toDate()), "sa" === e))
                a({ winddir: 55, windspeed: 25, humid: 7, temp: 97 }),
                    this._utils.updateStatus("fireConfigWeatherStatus", "Santa Ana."),
                    this._firemap.disableButtons(!1),
                    this._changeButtonSelection("selFireButton", "wxSantaAna"),
                    this.setFuelMoistureConditions("sa");
            else if ("paste" === e)
                a({ winddir: this._copiedFireOptions.winddir.v, windspeed: this._copiedFireOptions.windspeed.v, humid: this._copiedFireOptions.humidity.v, temp: this._copiedFireOptions.airtemperature.v }),
                    this._timeSlider.noUiSlider.set(this._copiedFireOptions.hours.v),
                    this._setFireStartTime(this._copiedFireOptions.startTime.toDate()),
                    this._utils.updateStatus("fireConfigWeatherStatus", "pasted fire settings.");
            else if ("nowStation" === e) this._setWxStationStartTimeToNow(), this.setFireConditions("station"), this.setFuelMoistureConditions("nearest");
            else if ("nearest" === e) (this._stationName = null), (this._stationLatLng = this._getLatLngOfIgnition()), this.setFireConditions("station"), this.setFuelMoistureConditions("nearest");
            else if ("windAverage" === e) (this._wxStationWindSpeedAverage = !0), document.getElementById("wxForecast").classList.contains("selFireButton") ? this.setFireConditions("forecast") : this.setFireConditions("station");
            else if ("windGust" === e) (this._wxStationWindSpeedAverage = !1), document.getElementById("wxForecast").classList.contains("selFireButton") ? this.setFireConditions("forecast") : this.setFireConditions("station");
            else if ("choose" === e)
                this._map.hasLayer(this._WeatherStationsLayer) || this._map.addLayer(this._WeatherStationsLayer),
                    this._overlay.close("manualFireOverlay"),
                    this._WeatherStationsLayer.chooseStation(function (e) {
                        (t._stationLatLng = e.geometry.coordinates), (t._stationName = e.properties.description.name), t.setFireConditions("station"), t._overlay.show("manualFireOverlay");
                    });
            else if ("station" === e) {
                var r,
                    n,
                    s = this._firemap.disableButtons(!0, { except: "Cancel", spinner: !0 }),
                    o = this._stationLatLng || this._getLatLngOfIgnition(),
                    l = Constants.urls.pylaski,
                    d = [];
                (this._fireOptions.conditions = e),
                    this._stationName
                        ? (this._utils.updateStatus("fireConfigWeatherStatus", "getting conditions at " + this._stationName + "."), d.push("wxChoose"))
                        : (this._utils.updateStatus("fireConfigWeatherStatus", "getting conditions at nearest weather station."), d.push("wxNearest")),
                    this._wxStationStartTimeIsNow ||
                        ((r = moment(this._wxStationStartTimeVal).subtract(1, "hour").format(this._FORMAT_MESOWEST_TIME)),
                        (n = moment(this._wxStationStartTimeVal, this._FORMAT_MOMENT_FIRE_START_TIME)
                            .add(this._timeSlider.noUiSlider.get() + 1, "hours")
                            .format(this._FORMAT_MESOWEST_TIME))),
                    this._wxStationStartTimeIsNow ? ((l += "stations/data/latest?"), d.push("wxNow")) : ((l += "stations/data?from=" + r + "&to=" + n + "&"), d.push("wxStationStartTimeVal")),
                    (l += "selection=closestTo&lat=" + o[1] + "&lon=" + o[0]),
                    (l += "&observable=temperature&observable=relative_humidity&observable=wind_direction&all=true"),
                    this._wxStationWindSpeedAverage ? ((l += "&observable=wind_speed"), d.push("wxWindAverage")) : ((l += "&observable=wind_gust"), d.push("wxWindGust")),
                    $.ajax({ url: l, type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "nearestWxData", timeout: 3e4 })
                        .fail(function (e, i) {
                            t._utils.updateStatus("fireConfigWeatherStatus", "Error retrieving conditions: " + i), t._firemap.disableButtons(!1, { except: "Run", spinner: s });
                        })
                        .done(function (o) {
                            if (o.features && o.features.length >= 1 && o.features[0].properties) {
                                var l,
                                    m,
                                    c,
                                    u,
                                    h = o.features[0].properties;
                                if (!t._wxStationStartTimeIsNow) {
                                    let e = moment(h.timestamp[0]),
                                        i = moment(h.timestamp[h.timestamp.length - 1]),
                                        a = moment(t._wxStationStartTimeVal),
                                        r = a.clone().add(t._timeSlider.noUiSlider.get() + 1, "hours");
                                    if ((e.isAfter(a) && a.diff(e, "minutes") > 10) || (i.isBefore(r) && r.diff(i, "minutes") > 10))
                                        return (
                                            console.log("requested", a.format(t._FORMAT_MESOWEST_TIME), r.format(t._FORMAT_MESOWEST_TIME)),
                                            console.log("got", e.format(t._FORMAT_MESOWEST_TIME), i.format(t._FORMAT_MESOWEST_TIME)),
                                            console.log("diff (minutes) start", a.diff(e, "minutes"), "stop", r.diff(i, "minutes")),
                                            t._utils.updateStatus("fireConfigWeatherStatus", h.description.name + " does not have measurements for the requested time period. Please choose another station."),
                                            void t._firemap.disableButtons(!1, { except: "Run", spinner: s })
                                        );
                                }
                                if (((l = void 0 !== h.wind_direction.value ? h.wind_direction.value : h.wind_direction), t._wxStationWindSpeedAverage)) {
                                    if (((m = void 0 !== h.wind_speed.value ? h.wind_speed.value : h.wind_speed), (h.wind_speed.units && "mps" === h.wind_speed.units) || (h.units.wind_speed && "mps" === h.units.wind_speed)))
                                        if (Array.isArray(m)) for (i in m) m[i] *= Constants.MPS_TO_MPH;
                                        else m *= Constants.MPS_TO_MPH;
                                } else if (((m = void 0 !== h.wind_gust.value ? h.wind_gust.value : h.wind_gust), (h.wind_gust.units && "mps" === h.wind_gust.units) || (h.units.wind_gust && "mps" === h.units.wind_gust)))
                                    if (Array.isArray(m)) for (i in m) m[i] *= Constants.MPS_TO_MPH;
                                    else m *= Constants.MPS_TO_MPH;
                                if (((c = void 0 !== h.relative_humidity.value ? h.relative_humidity.value : h.relative_humidity), (u = void 0 !== h.temperature.value ? h.temperature.value : h.temperature), Array.isArray(l))) {
                                    var p = [];
                                    for (i in h.timestamp) p.push(moment(h.timestamp[i]).diff(moment(t._wxStationStartTimeVal), "minutes"));
                                    var _ = [],
                                        y = 60 * t._fireOptions.hours.v;
                                    for (i = 0; i <= y; i += t._fireOptions.timestep.v) _.push(i);
                                    var f = [],
                                        g = [];
                                    for (i in l) {
                                        var v = (((270 - l[i] + 360) % 360) * Math.PI) / 180;
                                        f.push(m[i] * Math.cos(v)), g.push(m[i] * Math.sin(v));
                                    }
                                    for (i in ((u = everpolate.linear(_, p, u)), (c = everpolate.linear(_, p, c)), (m = everpolate.linear(_, p, m)), (f = everpolate.linear(_, p, f)), (g = everpolate.linear(_, p, g)), (l = []), f))
                                        l.push((270 - (180 * Math.atan2(g[i], f[i])) / Math.PI) % 360);
                                }
                                a({ winddir: l, windspeed: m, humid: c, temp: u });
                                var w = "";
                                if (
                                    (t._wxStationStartTimeIsNow && (w = "current "),
                                    (w += "conditions at " + h.description.name + " station"),
                                    (!t._stationName || t._stationName != h.description.name) && h.hasOwnProperty("distanceFromLocation"))
                                ) {
                                    var L = h.distanceFromLocation.value;
                                    "km" == h.distanceFromLocation.units && (L *= Constants.KM_TO_MI),
                                        isNaN(L) || ((w += " (" + L.toFixed(2) + " miles away"), t._stationName && t._stationName != h.description.name && (w += " from " + t._stationName), (w += ")"));
                                }
                                t._wxStationStartTimeIsNow || (w += " from " + r + " to " + n),
                                    (w += "."),
                                    t._utils.updateStatus("fireConfigWeatherStatus", w),
                                    (t._fireOptions.conditions = e),
                                    t._firemap.disableButtons(!1, { spinner: s }),
                                    t._changeButtonSelection("selFireButton", d);
                            } else t._utils.updateStatus("fireConfigWeatherStatus", "Error retrieving conditions: no measurements found within 10 miles."), t._firemap.disableButtons(!1, { except: "Run", spinner: s });
                        });
            } else if ("forecast" === e) {
                this.setFuelMoistureConditions("nearest"), (this._stationLatLng = null), (this._stationName = null), this._setWxStationStartTimeToNow();
                let i = this._firemap.disableButtons(!0, { except: "Cancel", spinner: !0 });
                this._utils.updateStatus("fireConfigWeatherStatus", "getting forecast data.");
                let r = this._getLatLngOfIgnition();
                $.ajax({ url: Constants.urls.pylaski + "forecast?source=" + t._weatherForecastModel + "&lat=" + r[1] + "&lon=" + r[0], type: "GET", dataType: "jsonp", jsonp: "callback", jsonpCallback: "forecast", timeout: 3e4 })
                    .fail(function (e, a) {
                        t._utils.updateStatus("fireConfigWeatherStatus", "Error retrieving forecast: " + a), t._firemap.disableButtons(!1, { except: "Run", spinner: i });
                    })
                    .done(function (r) {
                        if (r.features && r.features.length > 0 && r.features[0].properties) {
                            var n,
                                s,
                                o = r.features[0].properties,
                                l = [],
                                d = [],
                                m = [],
                                c = [],
                                u = [],
                                h = [],
                                p = [],
                                _ = moment();
                            let g = function (e) {
                                t._utils.updateStatus("fireConfigWeatherStatus", "Error retrieving forecast: " + e + "."), t._firemap.disableButtons(!1, { except: "Run", spinner: i });
                            };
                            if (moment(o.timestamp[o.timestamp.length - 1]).isBefore(_)) return void g("measurements too old");
                            if (!o.temperature) return void g("no temperature measurements");
                            if (!o.relative_humidity) return void g("no humidity measurements");
                            if (!o.wind_speed) return void g("no wind speed measurements");
                            if (!o.wind_direction) return void g("no wind direction measurements");
                            if (o.units)
                                for (n in o.timestamp)
                                    "C" == o.units.temperature && (o.temperature[n] = (9 * o.temperature[n]) / 5 + 32),
                                        "mps" == o.units.wind_speed && (o.wind_speed[n] *= Constants.MPS_TO_MPH),
                                        o.units.wind_gust && "mps" == o.units.wind_gust && (o.wind_gust[n] *= Constants.MPS_TO_MPH);
                            for (n in o.timestamp)
                                l.push(moment(o.timestamp[n]).diff(_, "minutes")),
                                    d.push(o.temperature[n]),
                                    m.push(o.relative_humidity[n]),
                                    t._wxStationWindSpeedAverage || !o.hasOwnProperty("wind_gust") ? c.push(o.wind_speed[n]) : c.push(o.wind_gust[n]),
                                    (s = 270 - o.wind_direction[n]) < 0 && (s += 360),
                                    (s *= Math.PI / 180),
                                    t._wxStationWindSpeedAverage || !o.hasOwnProperty("wind_gust")
                                        ? (h.push(o.wind_speed[n] * Math.cos(s)), p.push(o.wind_speed[n] * Math.sin(s)))
                                        : (h.push(o.wind_gust[n] * Math.cos(s)), p.push(o.wind_gust[n] * Math.sin(s)));
                            var y = [],
                                f = 60 * t._fireOptions.hours.v;
                            for (n = 0; n <= f; n += t._fireOptions.timestep.v) y.push(n);
                            for (n in ((h = everpolate.linear(y, l, h)), (p = everpolate.linear(y, l, p)), h)) {
                                let e = (270 - Math.atan2(p[n], h[n]) * (180 / Math.PI)) % 360;
                                u.push(e);
                            }
                            a({ temp: everpolate.linear(y, l, d), humid: everpolate.linear(y, l, m), windspeed: everpolate.linear(y, l, c), winddir: u }),
                                t._utils.updateStatus("fireConfigWeatherStatus", "forecast from " + t._WeatherForecastLayer.getModelShortTitle(document.getElementById("forecastForFireSelect").value) + "."),
                                (t._fireOptions.conditions = e),
                                t._firemap.disableButtons(!1, { spinner: i }),
                                t._wxStationWindSpeedAverage ? t._changeButtonSelection("selFireButton", ["wxForecast", "wxWindAverage"]) : t._changeButtonSelection("selFireButton", ["wxForecast", "wxWindGust"]);
                        }
                    });
            }
        },
        _showFireWeather: function (e, t) {
            var i = document.getElementById("dragWeatherText"),
                a = this;
            i.style.display = t ? "" : "none";
            var r = [],
                n = [],
                s = [],
                o = [],
                l = [],
                d = { airtemperature: { min: this._fireOptions.airtemperature.min, max: this._fireOptions.airtemperature.max }, windspeed: { min: this._fireOptions.windspeed.min, max: this._fireOptions.windspeed.max } };
            function m(e, t) {
                t < e.min ? (e.min = t) : t > e.max && (e.max = t);
            }
            for (var c = (60 * e.hours.v) / e.timestep.v, u = 0; u < c; u++) {
                var h = e.startTime
                    .clone()
                    .add(u * e.timestep.v, "minutes")
                    .valueOf();
                l.push(h), r.push([h, e.airtemperature.v[u]]), m(d.airtemperature, e.airtemperature.v[u]), n.push([h, e.humidity.v[u]]), s.push([h, e.windspeed.v[u]]), m(d.windspeed, e.windspeed.v[u]), o.push([h, e.winddir.v[u]]);
            }
            var p = { type: "datetime", tickPositions: l, labels: { format: "{value:%H:%M}" }, gridLineWidth: 1 };
            this._utils.initChart("fireTempChart"),
                this._utils.initChart("fireHumidChart"),
                this._utils.initChart("fireWindSpeedChart"),
                this._utils.initChart("fireWindDirectionChart"),
                this.resizeOverlays(),
                $("#fireTempChart").highcharts({
                    chart: Constants.chartOptions,
                    title: { text: "Air Temperature (F)" },
                    xAxis: p,
                    yAxis: { title: { text: null }, min: d.airtemperature.min, max: d.airtemperature.max, tickInterval: 1, endOnTick: !1 },
                    series: [
                        {
                            name: "Air Temperature",
                            data: r,
                            color: Constants.wxChartColors.airTemp,
                            tooltip: { valueSuffix: " F" },
                            draggableY: t,
                            dragMinY: this._fireOptions.airtemperature.min,
                            dragMaxY: this._fireOptions.airtemperature.max,
                        },
                    ],
                    legend: { enabled: !1 },
                    credits: { enabled: !1 },
                    tooltip: { valueDecimals: 0 },
                    plotOptions: {
                        series: {
                            point: {
                                events: {
                                    drop: function () {
                                        a._fireOptions.airtemperature.v[this.index] = Math.round(this.y);
                                    },
                                },
                            },
                        },
                    },
                }),
                $("#fireHumidChart").highcharts({
                    chart: Constants.chartOptions,
                    title: { text: "Relative Humidity (%)" },
                    xAxis: p,
                    yAxis: { title: { text: null }, min: this._fireOptions.humidity.min, max: this._fireOptions.humidity.max, tickInterval: 5, endOnTick: !1 },
                    series: [
                        { name: "Relative Humidity", data: n, color: Constants.wxChartColors.humidity, tooltip: { valueSuffix: " %" }, draggableY: t, dragMinY: this._fireOptions.humidity.min, dragMaxY: this._fireOptions.humidity.max },
                    ],
                    legend: { enabled: !1 },
                    credits: { enabled: !1 },
                    tooltip: { valueDecimals: 0 },
                    plotOptions: {
                        series: {
                            point: {
                                events: {
                                    drop: function () {
                                        a._fireOptions.humidity.v[this.index] = Math.round(this.y);
                                    },
                                },
                            },
                        },
                    },
                }),
                $("#fireWindSpeedChart").highcharts({
                    chart: { spacingBottom: 1, spacingTop: 5, spacingLeft: 6, spacingRight: 10 },
                    title: { text: "Wind Speed (mph)" },
                    xAxis: p,
                    yAxis: { title: { text: null }, min: d.windspeed.min, max: d.windspeed.max, tickInterval: 1, endOnTick: !1 },
                    series: [{ name: "Wind Speed", data: s, color: Constants.wxChartColors.winSpeed, tooltip: { valueSuffix: " mph" }, draggableY: t, dragMinY: this._fireOptions.windspeed.min, dragMaxY: this._fireOptions.windspeed.max }],
                    legend: { enabled: !1 },
                    credits: { enabled: !1 },
                    tooltip: { valueDecimals: 0 },
                    plotOptions: {
                        series: {
                            point: {
                                events: {
                                    drop: function () {
                                        a._fireOptions.windspeed.v[this.index] = Math.round(this.y);
                                    },
                                },
                            },
                        },
                    },
                }),
                $("#fireWindDirectionChart").highcharts({
                    chart: Constants.chartOptions,
                    title: { text: "Wind Direction (degrees)" },
                    xAxis: p,
                    yAxis: { title: { text: null }, labels: { format: "{value}" }, min: this._fireOptions.winddir.min, max: this._fireOptions.winddir.max, tickInterval: 10, endOnTick: !1 },
                    series: [{ name: "Wind Direction", data: o, color: Constants.wxChartColors.windDirection, draggableY: t, dragMinY: this._fireOptions.winddir.min, dragMaxY: this._fireOptions.winddir.max }],
                    legend: { enabled: !1 },
                    credits: { enabled: !1 },
                    tooltip: { valueDecimals: 0 },
                    plotOptions: {
                        series: {
                            point: {
                                events: {
                                    drop: function () {
                                        a._fireOptions.winddir.v[this.index] = Math.round(this.y);
                                    },
                                },
                            },
                        },
                    },
                });
        },
        editFireWeather: function () {
            this._showFireWeather(this._fireOptions, !0), this._overlay.swap("manualFireOverlay", "fireWeather", { position: "center" }), (this._configuringFire = !0);
        },
        closeFireWeather: function () {
            this._configuringFire
                ? ((this._fireOptions.conditions = "manual"),
                  this._utils.updateStatus("fireConfigWeatherStatus", "manually updated."),
                  this._firemap.disableButtons(!1),
                  this._overlay.swap("fireWeather", "manualFireOverlay"),
                  (this._configuringFire = !1),
                  this._changeButtonSelection("selFireButton", "wxEdit"))
                : this._overlay.close("fireWeather");
        },
        _showSelectedFireWeather: function () {
            this._showFireWeather(this._selectedFire, !1), this._overlay.show("fireWeather");
        },
        toggleSelectedFireETA: function (e) {
            void 0 === e && (e = this._selectedFire.legendOverlayId), this._overlay.isShown(e) ? (this._overlay.close(e), document.body.removeChild(document.getElementById(e))) : this._showFireLegend();
        },
        _showFireLegend: function () {
            var e,
                t,
                a,
                r,
                n,
                s,
                o,
                l,
                d,
                m = this,
                c = [],
                u = this._selectedFire;
            (n = document.createElement("tbody")),
                (s = document.createElement("table")),
                (t = document.createElement("tr")),
                ((a = document.createElement("th")).innerHTML = "Color"),
                t.appendChild(a),
                ((a = document.createElement("th")).innerHTML = "ETA"),
                t.appendChild(a),
                ((a = document.createElement("th")).innerHTML = "Acres"),
                t.appendChild(a),
                ((a = document.createElement("th")).innerHTML = "Population"),
                t.appendChild(a),
                ((a = document.createElement("th")).innerHTML = "Housing"),
                t.appendChild(a),
                n.appendChild(t);
            for (let e = u.perimeters.features.length; e--; ) {
                let i, s, d, m;
                ((t = document.createElement("tr"))._elapsed = r = u.perimeters.features[e].properties.Elapsed_Mi),
                    ((a = document.createElement("td")).style["background-color"] = this._fireColors[((r - u.timestep.v) / u.timestep.v) % this._fireColors.length]),
                    (a.innerHTML = '<div style="width: 50px;"></div>'),
                    t.appendChild(a),
                    ((a = document.createElement("td")).innerHTML = u.startTime.clone().add(r, "minutes").format("HH:mm")),
                    t.appendChild(a),
                    ((a = document.createElement("td")).innerHTML = '<div style="text-align:right;">' + Math.round(u.area[u.perimeters.features.length - e - 1]) + "</div>"),
                    t.appendChild(a),
                    (i = document.createElement("td")),
                    t.appendChild(i),
                    (s = document.createElement("td")),
                    t.appendChild(s),
                    (m = L.GeoJSON.geometryToLayer(u.perimeters.features[e]).getBounds()),
                    (points = [m.getNorth(), m.getWest(), m.getNorth(), m.getEast(), m.getSouth(), m.getEast(), m.getSouth(), m.getWest(), m.getNorth(), m.getWest()].join(",")),
                    (d = Constants.urls.pylaski + "population?selection=polygon&points=" + points),
                    c.push(function () {
                        return $.ajax({ url: d, type: "GET", dataType: "jsonp", jsonpCallback: "getJsonPopulation_" + u.ignitionLayer.fireNum + "_" + e })
                            .fail(function (e, t) {
                                console.log(e + " " + t);
                            })
                            .done(function (e) {
                                var t;
                                e.features &&
                                    1 == e.features.length &&
                                    ((t = e.features[0].properties["total-population"]),
                                    "number" == typeof o && (t = t < o ? o : t),
                                    (o = t),
                                    (i.innerHTML = '<div style="text-align:right;">' + t + "</div>"),
                                    (t = e.features[0].properties["total-housing"]),
                                    "number" == typeof l && (t = t < l ? l : t),
                                    (l = t),
                                    (s.innerHTML = '<div style="text-align:right;">' + t + "</div>"));
                            });
                    }),
                    n.appendChild(t);
            }
            for (
                s.appendChild(n),
                    (e = document.createElement("div")).id = u.legendOverlayId = "fire_legend_" + u.ignitionLayer.fireNum,
                    e.className = "overlay draggable eta",
                    div = document.createElement("span"),
                    div.id = e.id + "_title",
                    div.innerHTML = u.fireName || "Summary",
                    div.className = "titleText",
                    e.appendChild(div),
                    div = document.createElement("div"),
                    div.className = "btn btnInChart",
                    div.onclick = function () {
                        m.toggleSelectedFireETA(e.id);
                    },
                    e.appendChild(div),
                    e.appendChild(document.createElement("br")),
                    e.appendChild(s),
                    document.body.appendChild(e),
                    d = promise = $.Deferred(),
                    i = 0;
                i < c.length;
                i++
            )
                promise = promise.then(c[i]);
            d.resolve(),
                (bounds = u.ensembleFireLayers ? u.ensembleFireLayers.getBounds() : u.layer.getBounds()),
                this._overlay.show(u.legendOverlayId, {
                    position: { top: this._map.latLngToLayerPoint(bounds.getCenter()).y - 15 * (u.perimeters.features.length + 1), left: this._map.latLngToLayerPoint(bounds.getNorthEast()).x + 20, loadFromState: !1 },
                }),
                this._overlay.redraw(),
                this._updateLegend();
        },
        _updateLegend: function (e) {
            if (this._selectedFire.legendOverlayId) {
                let e = document.getElementById(this._selectedFire.legendOverlayId);
                for (let t = 0; t < e.childNodes.length; t++)
                    if (e.childNodes[t].rows) {
                        let i = e.childNodes[t];
                        for (let e, t = 0; (e = i.rows[t]); t++) e._elapsed && (this._selectedFire.displayFrequency && e._elapsed % this._selectedFire.displayFrequency != 0 ? (e.style.display = "none") : (e.style.display = "table-row"));
                        break;
                    }
            }
        },
        _setFireStyle: function (e) {
            var t = this._fireTimeSlider ? this._fireTimeSlider.noUiSlider.get() : 999999;
            if (e.ensembleFireLayers) {
                var i = this._ensFireSlider ? this._ensFireSlider.noUiSlider.get() : 0,
                    a = 0;
                e.ensembleFireLayers.eachLayer(function (r) {
                    0 == i || i - 1 == a
                        ? (r.setStyle(function (i) {
                              return i.properties.Elapsed_Mi > t || (e.displayFrequency && i.properties.Elapsed_Mi % e.displayFrequency != 0)
                                  ? { fillOpacity: 0, opacity: 0 }
                                  : "Fill" === e.displayType
                                  ? { fillOpacity: e.opacity, opacity: 0, fill: !0, weight: 5, displayType: e.displayType }
                                  : "Lines" === e.displayType
                                  ? { opacity: e.opacity, fillOpacity: 0, fill: !1, weight: 2, displayType: e.displayType }
                                  : void 0;
                          }),
                          r.ignitionLayer && (r.ignitionLayer.setOpacity ? r.ignitionLayer.setOpacity(1) : (r.ignitionLayer.setStyle({ opacity: 1 }), 1 == i && r.ignitionLayer.setStyle({ fillOpacity: 0.2 }))))
                        : (r.setStyle({ opacity: 0, fillOpacity: 0 }), r.ignitionLayer && (r.ignitionLayer.setOpacity ? r.ignitionLayer.setOpacity(0) : r.ignitionLayer.setStyle({ opacity: 0, fillOpacity: 0 }))),
                        a++;
                }),
                    e.ensProbabilityLayer && this._map.removeLayer(e.ensProbabilityLayer);
            } else
                e.layer.setStyle(function (i) {
                    return i.properties.Elapsed_Mi > t || (e.displayFrequency && i.properties.Elapsed_Mi % e.displayFrequency != 0)
                        ? { fillOpacity: 0, opacity: 0 }
                        : "Fill" === e.displayType
                        ? { fillOpacity: e.opacity, opacity: 0, fill: !0, weight: 5, displayType: e.displayType }
                        : "Lines" === e.displayType
                        ? { opacity: e.opacity, fillOpacity: 0, fill: !1, weight: 2, displayType: e.displayType }
                        : void 0;
                });
        },
        _showFireInfo: function (e) {
            var t = this;
            e != this._selectedFire && this.playFire("stop"), (this._selectedFire = e);
            var a = e.perimeters.features[0].properties.Elapsed_Mi,
                r = a - e.perimeters.features[1].properties.Elapsed_Mi;
            for (
                this._fireTimeSlider && this._fireTimeSlider.noUiSlider.destroy(),
                    this._fireTimeSlider = this._utils.createSlider({
                        id: "fireTime",
                        start: a,
                        step: r,
                        min: 0,
                        max: a,
                        nopips: !0,
                        onupdate: function (i) {
                            (document.getElementById("fireTimeText").innerHTML = e.startTime.clone().add(i, "minutes").format("YYYY-MM-DD HH:mm")), t._setFireStyle(e);
                        },
                    }),
                    select = document.getElementById("fireDisplayType"),
                    0 === select.options.length
                        ? (this._utils.addToSelect(select, "Fill"), this._utils.addToSelect(select, "Lines"))
                        : "Fill" === e.displayType
                        ? (select.selectedIndex = 0)
                        : "Lines" === e.displayType && (select.selectedIndex = 1),
                    select = document.getElementById("fireDisplayFrequency"),
                    i = select.options.length - 1;
                i >= 0;
                i--
            )
                select.remove(i);
            this._utils.addToSelect(select, "30 minutes", 30),
                this._utils.addToSelect(select, "1 hour", 60),
                a % 120 == 0 && this._utils.addToSelect(select, "2 hours", 120),
                a % 180 == 0 && this._utils.addToSelect(select, "3 hours", 180),
                this._utils.addToSelect(select, "Only final", a),
                30 == e.displayFrequency
                    ? (select.selectedIndex = 0)
                    : e.displayFrequency == a
                    ? (select.selectedIndex = select.length - 1)
                    : 60 == e.displayFrequency
                    ? (select.selectedIndex = 1)
                    : 120 == e.displayFrequency
                    ? (select.selectedIndex = 2)
                    : 180 == e.displayFrequency && (select.selectedIndex = 3),
                this._overlay.show("fireInfoOverlay"),
                e.ensembleFireLayers ? this.showEnsembleInfo(e) : this._overlay.close("ensembleInfoOverlay");
        },
        showEnsembleInfo: function (e) {
            var t = this;
            this._ensFireSlider && this._ensFireSlider.noUiSlider.destroy(),
                (this._ensFireSlider = this._utils.createSlider({
                    id: "ensFireSlider",
                    start: 0,
                    step: 1,
                    min: 0,
                    max: e.ensembleFireLayers.getLayers().length,
                    onupdate: function (i) {
                        t._setFireStyle(e);
                    },
                })),
                this._overlay.show("ensembleInfoOverlay");
        },
        toggleSelectedFireWeather: function () {
            this._overlay.isShown("fireWeather") ? this._overlay.close("fireWeather") : this._showSelectedFireWeather();
        },
        toggleFireAreaChart: function () {
            this._overlay.isShown("fireAreaOverlay") ? this._overlay.close("fireAreaOverlay") : this._showFireAreaChart();
        },
        _showFireAreaChart: function () {
            var e = [this._selectedFire.startTime.clone().valueOf()],
                t = [[e[0], 0]];
            for (var i in this._selectedFire.times) {
                var a = this._selectedFire.startTime.clone().add(this._selectedFire.times[i], "minutes").valueOf();
                e.push(a), t.push([a, this._selectedFire.area[i]]);
            }
            this._utils.initChart("fireAreaChart"),
                this.resizeOverlays(),
                $("#fireAreaChart").highcharts({
                    xAxis: { type: "datetime", tickPositions: e, tickInterval: 6e4, labels: { format: "{value:%H:%M}" } },
                    yAxis: { title: { text: null } },
                    series: [{ name: "Area", data: t, color: "#FF0000" }],
                    tooltip: {
                        formatter: function () {
                            return "At " + moment(this.x).format("HH:mm") + ", fire is " + Math.round(this.y) + " acres.";
                        },
                    },
                    title: { text: "Area (acres)" },
                    legend: { enabled: !1 },
                    credits: { enabled: !1 },
                }),
                this._overlay.show("fireAreaOverlay");
        },
        playFire: function (e) {
            var t = this;
            this._playFireTimer && window.clearInterval(this._playFireTimer);
            var i = this._selectedFire;
            if (i) {
                var a = 60 * i.hours.v + 1;
                this._playFireTimer =
                    "start" === e
                        ? setInterval(function () {
                              t._fireTimeSlider.noUiSlider.set((t._fireTimeSlider.noUiSlider.get() + i.timestep.v) % a);
                          }, 500)
                        : null;
            }
        },
        configureShareFireRun: function () {
            var e, t, i, a, r, n;
            if (
                (this._shareFireRunOverlay && document.body.removeChild(this._shareFireRunOverlay),
                ((e = this._shareFireRunOverlay = document.createElement("div")).className = "overlay titleText draggable"),
                (e.id = "shareFireRun"),
                (i =
                    '<table> <tr><td>Fire Name:</td><td><input id="shareFireName" value="test" maxlength="64"></td></tr><tr><td>Incident ID:</td><td><input id="shareIncidentId" value="Wildland" maxlength="1024"></td></tr><tr><td>Your Name:</td><td><div id="shareFullName">' +
                    this._webview.loginInfo.fullname +
                    '</div></td></tr><tr><td>Group:</td><td><select id="shareGroup"></select></td></tr>'),
                this._isTrainingSite
                    ? (i += "<tr><td>Channel:</td><td>Training</td></tr>")
                    : 1 === this._user.channel.length
                    ? (i += "<tr><td>Channel:</td><td>" + this._user.channel[0] + "</td></tr>")
                    : (i += '<tr><td>Channel:</td><td><select id="shareChannel"></select></td></tr>'),
                (i += "<tr><td>Description:</td><td></td></tr></table>"),
                (i += '<textarea id="shareDescription" rows="5" columns="80" maxlength="1024"></textarea>'),
                (i += "<table>"),
                this._exports.length > 0)
            )
                for (t in ((i += '<tr><td colspan="2">Share to:</td></tr>'), this._exports)) i += "<tr><td><span>" + this._exports[t].name + '</span></td><td><input id="Share ' + this._exports[t].name + '" type="checkbox"></td></tr>';
            for (
                i +=
                    '<tr><td colspan="2"><label id="shareStatus"></label></td></tr><tr><td colspan="2"><div style="float:right;"><button class="fireButton" onclick="firemap.fire.shareFireRun()">Share</button><button class="fireButton" onclick="firemap.overlay.close(\'shareFireRun\')">Cancel</button></div></td></tr></table>',
                    e.innerHTML = i,
                    document.body.appendChild(e),
                    t = (a = document.getElementById("shareGroup")).options.length - 1;
                t >= 0;
                t--
            )
                a.options.remove(t);
            for (t in (((r = document.createElement("option")).text = r.value = "all users"), a.add(r), (n = this._webview.loginInfo.groups.slice()).sort(), n))
                "firemod" !== n[t] && (((r = document.createElement("option")).text = r.value = n[t]), a.add(r));
            if (!this._isTrainingSite && this._user.channel.length > 1) {
                if (0 === (a = document.getElementById("shareChannel")).options.length) for (let e in this._user.channel) ((r = document.createElement("option")).text = r.value = this._user.channel[e]), a.add(r);
                a.value = document.getElementById("loadChannel").value;
            }
            this._overlay.show("shareFireRun");
        },
        shareFireRun: function () {
            let e;
            e = this._isTrainingSite ? "Training" : 1 === this._user.channel.length ? this._user.channel[0] : document.getElementById("shareChannel").value;
            var t,
                i = {
                    shareGroup: document.getElementById("shareGroup").value,
                    shareChannel: e,
                    shareDescription: document.getElementById("shareDescription").value,
                    fireName: document.getElementById("shareFireName").value,
                    incidentId: document.getElementById("shareIncidentId").value,
                };
            if (!i.fireName || 0 === i.fireName.trim().length) return void (document.getElementById("shareStatus").innerHTML = "Enter Fire Name.");
            if (!i.incidentId || 0 === i.incidentId.trim().length) return void (document.getElementById("shareStatus").innerHTML = "Enter Incident ID.");
            for (t in ((document.getElementById("shareStatus").innerHTML = ""), this._exports)) document.getElementById("Share " + this._exports[t].name).checked && "agol" === this._exports[t].exportType && this.shareFireRunToAgol(i, t);
            this.shareFireRunToWifire(i), (this._selectedFire.fireName = i.fireName);
            let a = document.getElementById(this._selectedFire.legendOverlayId + "_title");
            a && (a.innerHTML = i.fireName), this._overlay.close("shareFireRun");
        },
        shareFireRunToAgol: function (e, t) {
            var a = this,
                r = [];
            this._selectedFire.ensembleFireLayers
                ? this._selectedFire.ensembleFireLayers.eachLayer(function (e) {
                      r.push(e.toGeoJSON());
                  })
                : r.push(this._selectedFire.layer.toGeoJSON());
            var n = ArcgisToGeojsonUtils.geojsonToArcGIS(r[0]);
            for (i in (n.reverse(), n)) {
                var s = n[i].attributes;
                (s.elapsed_minutes = s.Elapsed_Mi),
                    delete s.Elapsed_Mi,
                    (s.start_time = this._selectedFire.startTime.valueOf()),
                    (s.description = e.shareDescription),
                    (s.fire_name = e.fireName),
                    (s.incident_id = e.incidentId),
                    (s.status = "Active"),
                    this._exports[t].version > 1 &&
                        ((s.air_temperature = this._selectedFire.airtemperature.v[i]),
                        (s.relative_humidity = this._selectedFire.humidity.v[i]),
                        (s.wind_direction = this._selectedFire.winddir.v[i]),
                        (s.wind_speed = this._selectedFire.windspeed.v[i]),
                        (s.ember_probability = this._selectedFire.emberProbability.v),
                        (s.fm_dead_1 = this._selectedFire.fuelMoisture.v[0].one_hr),
                        (s.fm_dead_10 = this._selectedFire.fuelMoisture.v[0].ten_hr),
                        (s.fm_dead_100 = this._selectedFire.fuelMoisture.v[0].hundred_hr),
                        (s.fm_live_herb = this._selectedFire.fuelMoisture.v[0].live_herb),
                        (s.fm_live_wood = this._selectedFire.fuelMoisture.v[0].live_woody)),
                    this._exports[t].version > 2 && (s.fuel_type = this._selectedFire.fuel_type);
            }
            n.reverse(),
                this._webview
                    .run({
                        reqType: "POST",
                        app_name: "ShareFireRunToAGOL",
                        app_param: { firesPerimeters: n, startTime: this._selectedFire.startTime.format("YYYY-MM-DD HH:mm"), fireName: e.fireName, shareDescription: e.shareDescription, name: this._exports[t].name },
                    })
                    .fail(function (e) {
                        a._overlay.showMessageOverlay("Error saving fire to " + a._exports[t].name + ".");
                    })
                    .done(function (e) {
                        a._overlay.showMessageOverlay("Fire successfully saved to " + a._exports[t].name + ".");
                    });
        },
        shareFireRunToWifire: function (e) {
            var t,
                i = [],
                a = [],
                r = [],
                n = this._selectedFire.ignitionLayer,
                s = this;
            n.parentLayer && (n = n.parentLayer),
                this._selectedFire.barrierLayers &&
                    this._selectedFire.barrierLayers.eachLayer(function (e) {
                        a.push(e.toGeoJSON());
                    }),
                this._selectedFire.ensembleFireLayers
                    ? ((t = "ignition"),
                      this._selectedFire.ensembleFireLayers.eachLayer(function (e) {
                          r.push(e.toGeoJSON()), i.push(e.ignitionLayer.toGeoJSON());
                      }))
                    : ((t = "none"), r.push(this._selectedFire.layer.toGeoJSON()), i.push(this._selectedFire.ignitionLayer.toGeoJSON())),
                this._webview
                    .run({
                        reqType: "POST",
                        app_name: "ShareFireRun",
                        app_param: {
                            ignitions: i,
                            barriers: a,
                            firesPerimeters: r,
                            ensembletype: t,
                            windDirection: this._selectedFire.winddir.v,
                            windSpeed: this._selectedFire.windspeed.v,
                            humidity: this._selectedFire.humidity.v,
                            temperature: this._selectedFire.airtemperature.v,
                            emberProbability: this._selectedFire.emberProbability.v,
                            fuelMoisture: this._selectedFire.fuelMoisture.v,
                            fuelType: this._selectedFire.fuelType,
                            perimeterResolution: this._selectedFire.perimeterResolution,
                            hours: this._selectedFire.hours.v,
                            startTime: this._selectedFire.startTime.format("YYYY-MM-DD HH:mm"),
                            fireName: e.fireName,
                            shareGroup: e.shareGroup,
                            shareChannel: e.shareChannel,
                            description: e.shareDescription,
                            incidentId: e.incidentId,
                        },
                    })
                    .fail(function (e) {
                        alert("Error sharing fire: " + e);
                    })
                    .done(function (e) {
                        e.responses.length > 0 && e.responses[0].hasOwnProperty("success") && e.responses[0].success
                            ? s._overlay.showMessageOverlay("Fire successfully saved to WIFIRE.")
                            : s._overlay.showMessageOverlay("Error saving fire to WIFIRE.");
                    });
        },
        closeSharedRuns: function () {
            $("#sharedRunsTable").DataTable().destroy(), $("#sharedRunsTable tbody").off("click", "tr"), this._overlay.close("showSharedRuns"), this._listSharedRunsButton.enable();
        },
        closeFilesToImport: function (e) {
            $("#showFilesToImportTable").DataTable().destroy(), $("#showFilesToImportTable tbody").off("click", "tr"), this._overlay.close("showFilesToImport"), e && this._importLayersButton.enable();
        },
        loadSharedRuns: function (e) {
            var t = $("#sharedRunsTable").DataTable().cells(".selected", 0).data(),
                i = this;
            if (($("#sharedRunsTable").DataTable().destroy(), $("#sharedRunsTable tbody").off("click", "tr"), this.closeSharedRuns(), t.length < 1)) alert("Error: No runs selected.");
            else {
                for (var a = [], r = t.length, n = 0; n < r; n++) a.push(t[n]);
                this._webview
                    .run({ reqType: "POST", app_name: "GetSharedRuns", app_param: { ids: a } })
                    .fail(function (e) {
                        alert("Error loading fire(s): " + e);
                    })
                    .done(function (e) {
                        var t,
                            a,
                            r,
                            n,
                            s,
                            o,
                            l,
                            d = L.latLngBounds([]),
                            m = e.responses;
                        function c(e, t) {
                            return "Point" === e.type
                                ? L.marker([e.coordinates[1], e.coordinates[0]], { icon: t })
                                : L.geoJson(e, {
                                      pointToLayer: function (e, i) {
                                          return L.marker(i, { icon: t });
                                      },
                                  });
                        }
                        function u(e, t, i) {
                            var a,
                                r = { features: [], type: "FeatureCollection" };
                            for (a = 0; a < e.fires[i].steps.length; a++)
                                if ("null" !== e.fires[i].steps[a].perimeter) {
                                    var n = JSON.parse(e.fires[i].steps[a].perimeter);
                                    r.features.push({ id: a, type: "Feature", geometry: n, properties: { Elapsed_Mi: t.times[a] } });
                                }
                            return r.features.reverse(), r;
                        }
                        for (t = 0; t < m.length; t++) {
                            s = m[t];
                            var h = [];
                            for (
                                h.push({
                                    winddir: { v: [] },
                                    windspeed: { v: [] },
                                    humidity: { v: [] },
                                    airtemperature: { v: [] },
                                    fuelMoisture: { v: [] },
                                    emberProbability: { v: 0 },
                                    hours: { v: parseInt(s.durationMinutes / 60) },
                                    startTime: moment(s.startTime),
                                    timestep: { v: s.stepMinutes },
                                    area: [],
                                    fireName: s.fireName,
                                }),
                                    h[0].times = [],
                                    l = s.durationMinutes,
                                    r = s.stepMinutes;
                                r <= l;
                                r += s.stepMinutes
                            )
                                h[0].times.push(r);
                            for (a = 0; a < s.fires[0].steps.length; a++)
                                h[0].winddir.v.push(s.fires[0].steps[a].windDirection),
                                    h[0].windspeed.v.push(s.fires[0].steps[a].windSpeed),
                                    h[0].humidity.v.push(s.fires[0].steps[a].humidity),
                                    h[0].airtemperature.v.push(s.fires[0].steps[a].temperature),
                                    h[0].area.push(s.fires[0].steps[a].area * Constants.SQM_TO_ACRES);
                            for (
                                h[0].emberProbability.v = s.fires[0].emberProbability,
                                    h[0].fuelMoisture.v = s.fires[0].fuelMoisture.slice(),
                                    h[0].fuelType = s.fires[0].fuelType,
                                    h[0].perimeterResolution = s.fires[0].perimeterResolution,
                                    a = 1;
                                a < s.fires.length;
                                a++
                            )
                                h.push(JSON.parse(JSON.stringify(h[0]))), (h[a].startTime = moment(s.startTime));
                            if (((h[0].ignitionLayer = c(JSON.parse(s.fires[0].ignitions[0]), i._selectedIgnitionPointIcon)), i._createIgnitionLayer(h[0].ignitionLayer), "none" === s.ensembleType))
                                (h[0].displayType = "Fill"), (n = u(s, h[0], 0)), i._addFireLayer(h[0], n), d.extend(h[0].layer.getBounds());
                            else if ("ignition" === s.ensembleType) {
                                for (i._createIgnitionEnsembleLayer(h[0].ignitionLayer), i._addIgnitionEnsembleToMap(h[0].ignitionLayer), a = 1; a < s.fires.length; a++)
                                    (h[a].ignitionLayer = c(JSON.parse(s.fires[a].ignitions[0]), i._selectedEnsIgnitionPointIcon)),
                                        (h[a].ignitionLayer.parentLayer = h[0].ignitionLayer),
                                        h[0].ignitionLayer.ensembleLayer.addLayer(h[a].ignitionLayer);
                                for (i._selectIgnitionLayer(h[0].ignitionLayer), h[0].ensembleFireLayers = i._createFireEnsembleLayers(h[0].fireName), a = 0; a < s.fires.length; a++)
                                    (h[a].displayType = "Lines"), (n = u(s, h[a], a)), a > 0 && (h[a].ensembleFireLayers = h[0].ensembleFireLayers), i._addFireLayer(h[a], n);
                                d.extend(h[0].ensembleFireLayers.getBounds());
                            }
                            if ((i._showFireInfo(h[0]), s.fires[0].barriers.length > 0))
                                for (a in ((h[0].barrierLayers = L.layerGroup()), s.fires[0].barriers))
                                    (o = L.geoJson(JSON.parse(s.fires[0].barriers[a]))), i._createBarrierLayer(o), o.setStyle(i._activeBarrierStyle), h[0].barrierLayers.addLayer(o);
                        }
                        i._map.fitBounds(d, { maxZoom: 14 });
                    });
            }
        },
        _showSharedRuns: function () {
            var e = this;
            this._listSharedRunsButton.disable(),
                (document.getElementById("loadSharedButton").disabled = !0),
                this._webview
                    .run({ reqType: "POST", app_name: "ListSharedRuns", app_param: { channel: this._channelSharedRuns } })
                    .fail(function (t) {
                        e._listSharedRunsButton.enable(),
                            "Unauthorized" === t
                                ? e._firemap.checkPassword(e._showSharedRuns, "Wrong username or password.", e)
                                : 0 == t.indexOf("Permission denied: ")
                                ? e._firemap.checkPassword(e._showSharedRuns, t.substring("Permission denied: ".length), e)
                                : alert("Error accessing shared fires: " + t);
                    })
                    .done(function (t) {
                        var i = t.responses,
                            a = [];
                        for (var r in i) a.push([i[r].ensembleId, i[r].fireName, i[r].incidentId, i[r].description, i[r].startTime, i[r].userFirstLastName, i[r].groupName]);
                        $.fn.DataTable.isDataTable("#sharedRunsTable")
                            ? ($("#sharedRunsTable").DataTable().clear(), $("#sharedRunsTable").DataTable().rows.add(a), $("#sharedRunsTable").DataTable().draw())
                            : ($("#sharedRunsTable").dataTable({
                                  data: a,
                                  columns: [{ visible: !1 }, { width: "50px" }, { width: "70px" }, { width: "200px" }, { className: "dt-center", width: "70px" }, { width: "70px" }, { width: "50px", name: "group" }],
                                  info: !1,
                                  autoWidth: !1,
                                  scrollY: "350px",
                                  scrollX: !1,
                                  paging: !1,
                                  responsive: !0,
                                  order: [[4, "desc"]],
                              }),
                              $("#sharedRunsTable tbody").on("click", "tr", function () {
                                  $(this).toggleClass("selected"), (document.getElementById("loadSharedButton").disabled = 0 === $("#sharedRunsTable").DataTable().cells(".selected", 0).data().length);
                              })),
                            e.resizeOverlays(),
                            e._overlay.swap("passwordOverlay", "showSharedRuns", { position: { top: 60 } }),
                            document.getElementById("loadGroup").onchange();
                    });
        },
        showFirePerimeter: function () {
            this._overlay.close("queryPopulationOverlayRect"), this._overlay.close("queryPopulationOverlayPolygon"), this._map.removeLayer(this._globalLayer), this._createIgnitionLayer(this._globalLayer);
        },
        setNoEnsemble: function () {
            this._ignitionLayer &&
                this._ignitionLayer.ensembleLayer &&
                (delete this._ignitionLayer.ensembleLayer.parentLayer,
                this._ignitionLayer.ensembleLayer.eachLayer(function (e) {
                    delete e.parentLayer;
                }),
                this._ignitionLayer.ensembleLayer.clearLayers(),
                this._map.removeLayer(this._ignitionLayer.ensembleLayer),
                delete this._ignitionLayer.ensembleLayer),
                this._updateFireConfigEnsembleStatus();
        },
        closeSetupPerimeterEnsemble: function () {
            this._overlay.swap("setupPerimeterEnsembleOverlay", "advancedFireOverlay"), this._updateFireConfigEnsembleStatus();
        },
        randomizePerimeterEnsemble: function (e) {
            function t(e) {
                var t = document.getElementById(e),
                    i = parseInt(t.value),
                    a = document.getElementById(e).min,
                    r = document.getElementById(e).max;
                return i < a ? (t.value = a) : i > r && (t.value = r), parseInt(t.value);
            }
            var i = t("perimeterEnsembleSizeVal") - 1,
                a = t("perimeterEnsembleVarianceVal") / Constants.M_TO_FT;
            if (this._ignitionLayer.ensembleLayer) {
                var r = this._ignitionLayer.ensembleLayer.getLayers().length;
                if (e || i === r)
                    this._ignitionLayer.ensembleLayer.eachLayer(function (e) {
                        delete e.parentLayer;
                    }),
                        this._ignitionLayer.ensembleLayer.clearLayers();
                else if (i < r) {
                    for (var n = this._ignitionLayer.ensembleLayer.getLayers(); n.length > i; ) delete (m = n.pop()).parentLayer, this._ignitionLayer.ensembleLayer.removeLayer(m);
                    return;
                }
            } else this._createIgnitionEnsembleLayer(this._ignitionLayer);
            var s = this._ignitionLayer.toGeoJSON(),
                o = JSON.stringify(s),
                l = proj4(proj4.defs("EPSG:3785"));
            function d(e) {
                var t = l.forward(e);
                return (t[0] += Math.round(Math.random() * a) * (Math.random() < 0.5 ? -1 : 1)), (t[1] += Math.round(Math.random() * a) * (Math.random() < 0.5 ? -1 : 1)), l.inverse(t);
            }
            for (; this._ignitionLayer.ensembleLayer.getLayers().length < i; ) {
                var m,
                    c = JSON.parse(o);
                if ("Point" === s.geometry.type) {
                    var u = d(s.geometry.coordinates);
                    m = L.marker([u[1], u[0]]);
                } else {
                    for (var h in s.geometry.coordinates[0]) c.geometry.coordinates[0][h] = d(s.geometry.coordinates[0][h]);
                    m = L.geoJson(c);
                }
                (m.parentLayer = this._ignitionLayer), this._ignitionLayer.ensembleLayer.addLayer(m), this._drawnLayers.addLayer(m);
            }
            this._addIgnitionEnsembleToMap(this._ignitionLayer);
        },
        downloadFireRun: function (e) {
            var t,
                i,
                a,
                r,
                n,
                s,
                o,
                l = this._selectedFire.layer,
                d = this._barrierLayers.active.toGeoJSON(),
                m = document.getElementById("downloadFilename").value,
                c = this;
            for (r in (this._selectedFire.ensembleFireLayers
                ? ((i = { type: "FeatureCollection", features: [] }),
                  (t = { type: "FeatureCollection", features: [] }),
                  (o = 0),
                  this._selectedFire.ensembleFireLayers.eachLayer(function (e) {
                      var a = e.toGeoJSON();
                      for (r in a.features) delete a.features[r].id, (a.features[r].properties.fire = o);
                      (t.features = t.features.concat(a.features)), ((a = e.ignitionLayer.toGeoJSON()).properties.fire = o), (i.features = i.features.concat(a)), o++;
                  }))
                : ((t = l.toGeoJSON()), (i = this._ignitionLayer.toGeoJSON())),
            t.features))
                (n = t.features[r].properties),
                    "shp" === e && (t.features[r].geometry.type = "MultiLineString"),
                    (n.name = this._selectedFire.startTime.clone().add(n.Elapsed_Mi, "minutes").format("HH:mm")),
                    (n.color = this._fireColors[((n.Elapsed_Mi - this._selectedFire.timestep.v) / this._selectedFire.timestep.v) % this._fireColors.length]),
                    (n.timestamp = this._selectedFire.startTime.clone().add(n.Elapsed_Mi, "minutes").format("YYYY-MM-DDTHH:mm:ssZ")),
                    delete n.Month,
                    delete n.Day,
                    delete n.Hour;
            for (r in i.features) ((n = i.features[r].properties).name = "Ignition"), (n.color = this._selectedIgnitionStyle.color);
            for (r in d.features) ((n = d.features[r].properties).name = "Barrier"), (n.color = this._activeBarrierStyle.color);
            m ? ((m = m.trim()), (r = m.indexOf(".")) > -1 && (m = m.substring(0, r))) : (m = "Fire"),
                (s = this._firemap.disableButtons(!0, { id: "downloadOverlay", spinner: !0 })),
                this._webview
                    .run({ reqType: "POST", wf_name: "ExportRun", wf_param: { type: e, filename: m, perimeters: JSON.stringify(t), ignition: JSON.stringify(i), barriers: JSON.stringify(d), group: "fire" } })
                    .always(function () {
                        c._firemap.disableButtons(!1, { id: "downloadOverlay", spinner: s });
                    })
                    .fail(function (e) {
                        alert("Error converting fire perimeters: " + e);
                    })
                    .done(function (t) {
                        var i, r;
                        "kml" === e ? ((a = "kml"), (i = "application/vnd.google-earth.kml+xml"), (r = "text/plain")) : ((a = "zip"), (i = r = "application/zip")),
                            (m += "." + a),
                            download("data:" + r + ";base64," + t.responses[0].data, m, i);
                    }),
                this._overlay.close("downloadOverlay");
        },
        pasteFireSettings: function () {
            this.setFireConditions("paste"),
                this.setFuelMoistureConditions("paste"),
                (document.getElementById("emberval").value = this._fireOptions.emberProbability.v = this._copiedFireOptions.emberProbability.v),
                (document.getElementById("perimeterResolution").value = this._fireOptions.perimeterResolution = this._copiedFireOptions.perimeterResolution);
        },
        _getPopulation: function (e, t, i) {
            var a,
                r,
                n,
                s,
                o,
                l,
                d = this,
                m = e.pop();
            if ("rect" === t)
                (a = m._latlngs[0].lat),
                    (r = m._latlngs[0].lng),
                    (n = m._latlngs[1].lat),
                    (s = m._latlngs[2].lng),
                    (o = Constants.urls.pylaski + "population?selection=boundingBox&minLat=" + a + "&minLon=" + r + "&maxLat=" + n + "&maxLon=" + s);
            else
                for (l in ((a = r = 99999), (n = s = -99999), (o = Constants.urls.pylaski + "population?selection=polygon&points="), m._latlngs))
                    (o += m._latlngs[l].lat + "," + m._latlngs[l].lng + ","),
                        m._latlngs[l].lat > n && (n = m._latlngs[l].lat),
                        m._latlngs[l].lat < a && (a = m._latlngs[l].lat),
                        m._latlngs[l].lng > s && (s = m._latlngs[l].lng),
                        m._latlngs[l].lng < r && (r = m._latlngs[l].lng);
            $.ajax({ url: o, type: "GET", dataType: "jsonp", jsonpCallback: "getJsonPopulation" })
                .fail(function (e, t) {
                    console.log(e + " " + t);
                })
                .done(function (o) {
                    var l, c;
                    if (o.features) {
                        function u(e) {
                            return e.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                        }
                        l =
                            "<div style='text-align:center;font-weight:bold; font-size:20px'>2010 Census Information</div><div class='subTitle'>Population: &emsp; &emsp; &nbsp;" +
                            u((c = o.features[0].properties)["total-population"]) +
                            "</div><div class='subTitle'>Housing units:  &emsp; &nbsp;" +
                            u(c["total-housing"]) +
                            "</div>";
                    } else l = "<div style='text-align:center; font-weight:bold; font-size:20px'>No Data Found</div><p>Data is only available in California and Nevada</p>";
                    if ((m.unbindPopup().bindPopup(l), i)) {
                        var h = L.latLng((a + n) / 2, (r + s) / 2);
                        m.openPopup(h);
                    }
                    e.length > 0 && d._getPopulation(e, t);
                });
        },
        showPopulation: function (e) {
            this._overlay.close("queryPopulationOverlayRect"),
                this._overlay.close("queryPopulationOverlayPolygon"),
                this._map.removeLayer(this._globalLayer),
                this._createPopulationLayer(this._globalLayer),
                this._getPopulation([this._globalLayer], e, !0);
        },
        _setSelectedPopulationStyle: function (e) {
            this._setIgnitionStyle(e, this._selectedPopulationStyle, this._selectedEnsIgnitionPointIcon);
        },
        _createPopulationLayer: function (e) {
            this._setSelectedPopulationStyle(e), (e.isPopulationLayer = !0), e.addTo(this._map);
        },
        createSatelliteDetectionsEnsemble: function () {
            var e = this;
            this._overlay.close("queryPopulationOverlayRect"),
                this._map.removeLayer(this._globalLayer),
                $.ajax({
                    url:
                        Constants.urls.wfs +
                        "/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=WIFIRE:active_perimeters&cql_filter=bbox(geom, " +
                        this._globalLayer.getBounds().toBBoxString() +
                        ")&propertyname=geom&outputFormat=text/javascript&format_options=callback:asdasd",
                    type: "GET",
                    dataType: "jsonp",
                    jsonp: "callback",
                    jsonpCallback: "asdasd",
                    timeout: 1e4,
                })
                    .fail(function (e, t) {
                        "abort" !== t && alert("Error retrieving active perimeters: " + t);
                    })
                    .done(function (t) {
                        L.geoJson(t).eachLayer(function (t) {
                            e._createBarrierLayer(t);
                        }),
                            $.ajax({
                                url:
                                    Constants.urls.wfs +
                                    "/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=WIFIRE:view_viirs_iband&cql_filter=bbox(location, " +
                                    e._globalLayer.getBounds().toBBoxString() +
                                    ") and seconds_ago < 46800 and confidence <> 'low'&propertyname=location&outputFormat=text/javascript&format_options=callback:asdasd",
                                type: "GET",
                                dataType: "jsonp",
                                jsonp: "callback",
                                jsonpCallback: "asdasd",
                                timeout: 1e4,
                            })
                                .fail(function (e, t) {
                                    "abort" !== t && alert("Error retrieving active perimeters: " + t);
                                })
                                .done(function (t) {
                                    var i,
                                        a = L.geoJson(t).getLayers(),
                                        r = a.length;
                                    if (r > 0) {
                                        for (e.addIgnitionPoint(a[0]), e._createIgnitionEnsembleLayer(a[0]), i = 1; i < r; i++) (a[i].parentLayer = a[0]._ignitionLayer), a[0].ensembleLayer.addLayer(a[i]);
                                        e._addIgnitionEnsembleToMap(a[0]);
                                    }
                                });
                    });
        },
        _import: function (e) {
            var t = this;
            if (((this._selectedImportLayerName = e.name), !this._importedLayers[this._selectedImportLayerName])) {
                (this._importedLayers[this._selectedImportLayerName] = L.layerGroup().addTo(this._map)),
                    (this._importedFilteredLayers[this._selectedImportLayerName] = L.layerGroup()),
                    (this._reverseImportedIgnitionsVal[this._selectedImportLayerName] = !1);
                let e = document.getElementById("importFilterSelect"),
                    t = document.createElement("option");
                (t.text = t.value = this._selectedImportLayerName), e.add(t), (e.selectedIndex = e.length - 1);
            }
            this._importedLayers[this._selectedImportLayerName].eachLayer(function (e) {
                t._mapLayers.removeLayer(e), t._barrierLayers.active.removeLayer(e), t._barrierLayers.inactive.removeLayer(e);
            }),
                e.directory
                    ? ((this._importDirectory = e.directory),
                      $.ajax({ url: e.directory, type: "GET", timeout: 1e4, dataType: "json" })
                          .fail(function (e, i) {
                              alert("Error retrieving " + name + ": " + i), t._importLayersButton.enable();
                          })
                          .done(function (i) {
                              var a,
                                  r,
                                  n = [];
                              if (!i.hasOwnProperty(e.directory)) return console.log("Error: returned object missing requested directory: " + e.directory), console.log(i), void t._importLayersButton.enable();
                              for (a in (r = i[e.directory])) r[a].lastModified && n.push([r[a].name.substring(r[a].name.lastIndexOf("/") + 1), moment(r[a].lastModified).format("YYYY-MM-DD HH:mm")]);
                              (document.getElementById("loadFileToImportButton").disabled = !0),
                                  t.resizeOverlays(),
                                  t._overlay.swap("passwordOverlay", "showFilesToImport", { position: { top: 60 } }),
                                  $("#showFilesToImportTable").dataTable({ data: n, columns: [null, { width: "80px" }], info: !1, autoWidth: !1, scrollY: "350px", scrollX: !1, paging: !1, responsive: !0, order: [[1, "desc"]] }),
                                  t.resizeOverlays(),
                                  $("#showFilesToImportTable tbody").on("click", "tr", function () {
                                      $(this).toggleClass("selected"), (document.getElementById("loadFileToImportButton").disabled = 0 === $("#showFilesToImportTable").DataTable().cells(".selected", 0).data().length);
                                  });
                          }))
                    : (this._addAgolFeatures(e.name), this._importLayersButton.enable());
        },
        getFilesToImport: function () {
            var e,
                t = $("#showFilesToImportTable").DataTable().cells(".selected", 0).data();
            if (($("#showFilesToImportTable").DataTable().destroy(), $("#showFilesToImportTable tbody").off("click", "tr"), this.closeFilesToImport(), t.length < 1)) alert("Error: No runs selected.");
            else {
                for (this._filesToImport = [], e = 0; e < t.length; e++) this._filesToImport.push(t[e]);
                this._showSelectImportFileTypeOverlay();
            }
        },
        _showSelectImportFileTypeOverlay: function (e) {
            var t,
                i = this,
                a = this._filesToImport[0],
                r = document.getElementById("importTypeButtons");
            if (((r.innerHTML = ""), /\.json$/i.test(a) || /\.geojson$/i.test(a)))
                (document.getElementById("importTypeVal").innerHTML = a + " is:"),
                    ((t = document.createElement("button")).className = "fireButton"),
                    (t.innerHTML = "Ignition/Perimeter"),
                    (t.onclick = function () {
                        i._selectFileImportType("ignition", e);
                    }),
                    r.appendChild(t),
                    r.appendChild(document.createElement("br")),
                    ((t = document.createElement("button")).className = "fireButton"),
                    (t.innerHTML = "Barrier"),
                    (t.onclick = function () {
                        i._selectFileImportType("barrier", e);
                    }),
                    r.appendChild(t),
                    r.appendChild(document.createElement("br")),
                    ((t = document.createElement("button")).className = "fireButton"),
                    (t.innerHTML = "Cancel"),
                    (t.onclick = function () {
                        i._selectFileImportType("skip", e);
                    }),
                    r.appendChild(t);
            else {
                if (/\.tiff?$/i.test(a)) return void this._selectFileImportType("image", e);
                (document.getElementById("importTypeVal").innerHTML = a + " is unknown type."),
                    ((t = document.createElement("button")).className = "fireButton"),
                    (t.innerHTML = "OK"),
                    (t.onclick = function () {
                        i._selectFileImportType("skip");
                    }),
                    r.appendChild(t);
            }
            this._overlay.show("importTypeOverlay");
        },
        _selectFileImportType: function (e, t) {
            var i = this,
                a = this._filesToImport.shift();
            if ("ignition" === e || "barrier" === e) {
                let r = e,
                    n = a.substring(0, a.lastIndexOf("."));
                $.ajax({ url: this._importDirectory + "/" + a, type: "GET", timeout: 1e4, dataType: "json" })
                    .fail(function (e, t) {
                        i._overlay.showMessageOverlay("Error retrieving " + n + ": " + t), i._importLayersButton.enable();
                    })
                    .done(function (e) {
                        var a = L.geoJson(e);
                        "ignition" === r
                            ? a.eachLayer(function (e) {
                                  i._importedLayers[i._selectedImportLayerName].addLayer(e), i._createIgnitionLayer(e, n);
                              })
                            : "barrier" === r &&
                              ((a = L.geoJson(e)).setStyle(i._activeBarrierStyle),
                              a.eachLayer(function (e) {
                                  i._createBarrierLayer(e);
                              })),
                            t ? t.extend(a.getBounds()) : (t = a.getBounds()),
                            i._filesToImport.length > 0 ? i._showSelectImportFileTypeOverlay(t) : (i._overlay.close("importTypeOverlay"), i._importLayersButton.enable());
                    });
            } else
                "image" === e
                    ? this._webview
                          .run({ reqType: "POST", app_name: "GetImage", app_param: { dir: this._importDirectory, name: a } })
                          .fail(function (e) {
                              i._overlay.showMessageOverlay("Error loading " + a), i._importLayersButton.enable();
                          })
                          .done(function (e) {
                              var r = e.responses[0],
                                  n = [
                                      [r.minLat, r.minLon],
                                      [r.maxLat, r.maxLon],
                                  ],
                                  s = L.imageOverlay(r.image, n).addTo(i._map);
                              i._mapLayers.addNestedOverlay(s, a, "Imported Imagery"),
                                  t ? t.extend(n) : (t = L.latLngBounds(n)),
                                  i._map.fitBounds(t, { maxZoom: 14 }),
                                  i._filesToImport.length > 0 ? i._showSelectImportFileTypeOverlay(t) : (i._overlay.close("importTypeOverlay"), i._importLayersButton.enable());
                          })
                    : "skip" === e
                    ? i._filesToImport.length > 0
                        ? this._showSelectImportFileTypeOverlay(t)
                        : (this._overlay.close("importTypeOverlay"), this._importLayersButton.enable())
                    : (console.log("Unknown import file type: " + e), this._importLayersButton.enable());
        },
        _featureServiceIsPerimeter: function (e, t) {
            return "LAFD Collector" !== e || !!(t.hasOwnProperty("Incident_name") || (t.Zone_Type && "Fire Perimeter" == t.Zone_Type));
        },
        _featureServiceIsBarrier: function (e, t) {
            return "LAFD Collector" !== e || !(!t.Line_type || ("Fire_Line" != t.Line_type && "Retardent" !== t.Line_type));
        },
        _addAgolFeatures: function (e) {
            var t = this;
            this._webview
                .run({ reqType: "POST", app_name: "LoadFromAGOL", app_param: { name: e } })
                .fail(function (i) {
                    t._overlay.showMessageOverlay("Error importing from " + e + ".");
                })
                .done(function (i) {
                    var a,
                        r,
                        n,
                        s,
                        o,
                        l = [];
                    for (a in (i = i.responses))
                        for (r in i[a].features)
                            if (i[a].features[r].geometry) {
                                let d = (n = { crs: i[a].crs, type: i[a].type, features: [i[a].features[r]] }).features[0];
                                n.features &&
                                    d.properties &&
                                    ((s = d.properties),
                                    t._featureServiceIsPerimeter(e, s)
                                        ? ("Point" === n.features[0].geometry.type
                                              ? ((o = L.marker([d.geometry.coordinates[1], d.geometry.coordinates[0]], { icon: t._selectedIgnitionPointIcon })).feature = { properties: s })
                                              : "LineString" === d.geometry.type
                                              ? d.geometry.coordinates[0][0] == d.geometry.coordinates[d.geometry.coordinates.length - 1][0] &&
                                                d.geometry.coordinates[0][1] == d.geometry.coordinates[d.geometry.coordinates.length - 1][1] &&
                                                ((d.geometry.type = "Polygon"),
                                                (d.geometry.coordinates = [d.geometry.coordinates]),
                                                L.geoJson(n).eachLayer(function (e) {
                                                    o = e;
                                                }))
                                              : L.geoJson(n).eachLayer(function (e) {
                                                    o = e;
                                                }),
                                          (o.feature.properties._import_name = e),
                                          l.push(o))
                                        : t._featureServiceIsBarrier(e, s) &&
                                          (o = L.geoJson(n)).eachLayer(function (e) {
                                              t._importedLayers[t._selectedImportLayerName].addLayer(e), t._createBarrierLayer(e);
                                          }));
                            }
                    if (l.length > 0)
                        for (a in (l.sort(function (e, t) {
                            return t.feature.properties.created_date - e.feature.properties.created_date;
                        }),
                        l))
                            t._importedLayers[t._selectedImportLayerName].addLayer(l[a]), t._createIgnitionLayer(l[a], e, t._getImportedIgnitionName(l[a], !0));
                    t._importedLayers[t._selectedImportLayerName].getLayers().length > 0 &&
                        (t._lastImportedIgnitionsSlider.noUiSlider.updateOptions({ range: { min: 1, max: t._importedLayers[t._selectedImportLayerName].getLayers().length } }),
                        t._updateShownImportedIgnitions(),
                        t._lastImportedIgnitionsSlider.noUiSlider.set(10),
                        t._overlay.show("importsFilterControl"));
                });
        },
        resizeOverlays: function () {
            var e,
                t,
                i,
                a,
                r = document.getElementById("fuelMoistureOverlay");
            (e = window.innerWidth - 20), (r.style.width = e < 395 ? e : 395);
            var n = document.getElementById("fireAreaOverlay");
            (t = (e = window.innerWidth - 20) < Constants.chartWidth.max ? e : Constants.chartWidth.max),
                this._overlay.isShown("fireAreaOverlay") && (t = n.offsetWidth < t ? n.offsetWidth : t),
                (document.getElementById("fireAreaChart").style.width = t + "px");
            var s = document.getElementById("dragWeatherText"),
                o = document.getElementById("fireTempChart"),
                l = document.getElementById("fireHumidChart"),
                d = document.getElementById("fireWindSpeedChart"),
                m = document.getElementById("fireWindDirectionChart"),
                c = document.getElementById("fireWeather"),
                u = (window.innerHeight - s.scrollHeight - 20) / 4;
            (a = u < 130 ? u : 130),
                (t = (e = window.innerWidth - 20) < Constants.chartWidth.max ? e : Constants.chartWidth.max),
                this._overlay.isShown("fireWeather") && (t = c.offsetWidth < t ? c.offsetWidth : t),
                (s.style.width = o.style.width = l.style.width = d.style.width = m.style.width = t + "px"),
                (o.style.height = l.style.height = d.style.height = m.style.height = a + "px"),
                (t = (e = window.innerWidth - 50) < 800 ? e : 800),
                (a = (i = window.innerHeight - 50) < 510 ? i : 510),
                (document.getElementById("showSharedRuns").style.width = t + "px"),
                (t = e < 550 ? e : 550),
                (document.getElementById("showFilesToImportTable").style.width = t + "px"),
                $(".dataTables_scrollBody").css("height", a - 160 + "px"),
                (document.getElementById("windspeedCell").style.display = document.getElementById("temperatureCell").style.display = document.getElementById("winddirCell").style.display = document.getElementById(
                    "humidityCell"
                ).style.display = document.getElementById("timeCell").style.display = e < 626 ? "none" : "");
        },
        showFuelMoistureOverlay: function () {
            var e = this;
            this._overlay.swap("manualFireOverlay", "fuelMoistureOverlay"),
                (this._fuelMoistureTable = new Tabulator("#fuelMoistureTable", {
                    columns: [
                        {
                            title: "Fuel Model",
                            field: "model",
                            headerSort: !1,
                            validator: "required",
                            editor: "select",
                            editorParams: { values: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] },
                            editable: function (e) {
                                return 0 != e.getRow().getPosition();
                            },
                            formatter: function (e) {
                                return 0 === e.getValue() ? "Default" : e.getValue();
                            },
                        },
                        {
                            title: "1 HR",
                            field: "one_hr",
                            headerSort: !1,
                            validator: ["required", "integer", "min:" + this._fuelMoistureRanges.one_hr.min, "max:" + this._fuelMoistureRanges.one_hr.max],
                            editor: "number",
                            editorParams: { min: this._fuelMoistureRanges.one_hr.min, max: this._fuelMoistureRanges.one_hr.max, step: 1 },
                        },
                        {
                            title: "10 HR",
                            field: "ten_hr",
                            headerSort: !1,
                            validator: ["required", "integer", "min:" + this._fuelMoistureRanges.ten_hr.min, "max:" + this._fuelMoistureRanges.ten_hr.max],
                            editor: "number",
                            editorParams: { min: this._fuelMoistureRanges.ten_hr.min, max: this._fuelMoistureRanges.ten_hr.max, step: 1 },
                        },
                        {
                            title: "100 HR",
                            field: "hundred_hr",
                            headerSort: !1,
                            validator: ["required", "integer", "min:" + this._fuelMoistureRanges.hundred_hr.min, "max:" + this._fuelMoistureRanges.hundred_hr.max],
                            editor: "number",
                            editorParams: { min: this._fuelMoistureRanges.hundred_hr.min, max: this._fuelMoistureRanges.hundred_hr.max, step: 1 },
                        },
                        {
                            title: "Live Herb",
                            field: "live_herb",
                            headerSort: !1,
                            validator: ["required", "integer", "min:" + this._fuelMoistureRanges.live_herb.min, "max:" + this._fuelMoistureRanges.live_herb.max],
                            editor: "number",
                            editorParams: { min: this._fuelMoistureRanges.live_herb.min, max: this._fuelMoistureRanges.live_herb.max, step: 1 },
                        },
                        {
                            title: "Live Woody",
                            field: "live_woody",
                            headerSort: !1,
                            validator: ["required", "integer", "min:" + this._fuelMoistureRanges.live_woody.min, "max:" + this._fuelMoistureRanges.live_woody.max],
                            editor: "number",
                            editorParams: { min: this._fuelMoistureRanges.live_woody.min, max: this._fuelMoistureRanges.live_woody.max, step: 1 },
                        },
                    ],
                    validationFailed: function (e) {
                        document.getElementById("fuelMoistureDoneButton").disabled = !0;
                    },
                    data: this._fireOptions.fuelMoisture.v.slice(),
                    resizableColumns: !1,
                    responsiveLayout: "collapse",
                    selectable: !1,
                    dataEdited: function (t) {
                        (document.getElementById("fuelMoistureDoneButton").disabled = !1),
                            (e._fireOptions.fuelMoisture.v = t.slice()),
                            e._changeButtonSelection("selFireButton", [], "fuelMoistureOverlay"),
                            e._utils.updateStatus("fuelMoistureStatus", "manually updated.");
                    },
                }));
        },
        _updateShownImportedIgnitions: function () {
            let e = this;
            if (((this._lastImportedIgnitionsVal = this._lastImportedIgnitionsSlider.noUiSlider.get()), this._importedLayers[this._selectedImportLayerName])) {
                let t = this._importedLayers[this._selectedImportLayerName].getLayers(),
                    i = function (t, i) {
                        return e._reverseImportedIgnitionsVal[e._selectedImportLayerName] ? t.feature.properties.created_date - i.feature.properties.created_date : i.feature.properties.created_date - t.feature.properties.created_date;
                    };
                if (t.length > 0 && this._importedLayers[this._selectedImportLayerName].getLayers().length > this._lastImportedIgnitionsVal)
                    for (t.sort(i); this._importedLayers[this._selectedImportLayerName].getLayers().length > this._lastImportedIgnitionsVal; ) {
                        let e = t.pop();
                        this._importedLayers[this._selectedImportLayerName].removeLayer(e), this._importedFilteredLayers[this._selectedImportLayerName].addLayer(e), this._mapLayers.removeLayer(e);
                    }
                let a = this._importedFilteredLayers[this._selectedImportLayerName].getLayers();
                if (a.length > 0 && this._importedLayers[this._selectedImportLayerName].getLayers().length < this._lastImportedIgnitionsVal)
                    for (a.sort(i); this._importedLayers[this._selectedImportLayerName].getLayers().length < this._lastImportedIgnitionsVal; ) {
                        let e = a.shift(),
                            t = e.feature.properties;
                        this._importedFilteredLayers[this._selectedImportLayerName].removeLayer(e),
                            this._importedLayers[this._selectedImportLayerName].addLayer(e),
                            this._mapLayers.addNestedOverlay(e, this._getImportedIgnitionName(e, !0), t._import_name);
                    }
            }
            this._overlay.isShown("importsLegend") && this._updateImportsLegend();
        },
        _getImportedIgnitionName: function (e, t) {
            if (e.feature && e.feature.properties) {
                let i = e.feature.properties,
                    a = i.Incident_name || i.IncidentName || i.incident_name || i.mission || "unknown";
                return (
                    (match = a.match(/(.*)_?(\d{12}z)/)),
                    match
                        ? t
                            ? i.created_date
                                ? match[1].replace(/_*$/, "") + " " + moment.utc(i.created_date).local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")
                                : match[1].replace(/_*$/, "") + " " + moment.utc(match[2], "MMDDYYYYHHmmz").local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")
                            : match[1].replace(/_*$/, "")
                        : t && i.created_date
                        ? a + " " + moment.utc(i.created_date).local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")
                        : a.replace(/_\d+z$/, "")
                );
            }
            return "unknown";
        },
        _reverseImportedIgnitions: function () {
            let e = this,
                t = this._reverseImportedIgnitionsButtonVal;
            if (t != this._reverseImportedIgnitionsVal[this._selectedImportLayerName]) {
                this._reverseImportedIgnitionsVal[this._selectedImportLayerName] = t;
                let i = this._importedLayers[this._selectedImportLayerName].getLayers(),
                    a = this._importedFilteredLayers[this._selectedImportLayerName].getLayers(),
                    r = function (e, t) {
                        return t.feature.properties.created_date - e.feature.properties.created_date;
                    };
                i.sort(r),
                    a.sort(r),
                    this._importedLayers[this._selectedImportLayerName].eachLayer(function (t) {
                        e._mapLayers.removeLayer(t);
                    }),
                    this._importedLayers[this._selectedImportLayerName].clearLayers(),
                    this._importedFilteredLayers[this._selectedImportLayerName].clearLayers(),
                    (this._importedFilteredLayers[this._selectedImportLayerName] = L.featureGroup(i.concat(a))),
                    this._lastImportedIgnitionsSlider.noUiSlider.set(this._importedFilteredLayers[this._selectedImportLayerName].getLayers().length - this._lastImportedIgnitionsSlider.noUiSlider.get() - 2),
                    (document.getElementById("lastImportedIgnitionsFirstLastVal").innerHTML = this._reverseImportedIgnitionsVal[this._selectedImportLayerName] ? "first" : "last");
            }
        },
        _updateImportsLegend: function () {
            var e,
                t,
                i = document.getElementById("importsLegend"),
                a = this._map.getBounds(),
                r = document.getElementById("importsLegendTable").tBodies[0];
            document.getElementById("importsLegendTitle").innerHTML = this._selectedImportLayerName;
            let n = this._importedLayers[this._selectedImportLayerName].getLayers();
            for (let e = 0; e < r.rows.length; e++) {
                if (-1 === r.rows[e]._id) continue;
                let t = !1;
                for (let i in n)
                    if (n[i].feature.id === r.rows[e]._id && this._layerInBounds(n[i], a)) {
                        t = !0;
                        break;
                    }
                t || (r.deleteRow(e), e--);
            }
            for (let i in n) {
                let s = n[i],
                    o = !0;
                for (let e = 0; e < r.rows.length; e++)
                    if (r.rows[e]._id === s.feature.id) {
                        o = !1;
                        break;
                    }
                if (!o || !this._layerInBounds(s, a) || !s.feature.geometry) continue;
                let l = s.toGeoJSON(),
                    d = null,
                    m = "unknown",
                    c = this._getImportedIgnitionName(s);
                d = "Point" === l.geometry.type ? "NA" : Math.round(turf.area.default(s.toGeoJSON()) * Constants.SQM_TO_ACRES);
                let u = s.feature.properties;
                u.created_date ? (m = moment(u.created_date).local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")) : u.creationdate && (m = moment(u.creationdate).local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")),
                    ((e = document.createElement("tr"))._id = s.feature.id),
                    (e._layer = s),
                    (e.onmouseover = this._legendRowMouseOver),
                    (e.onmouseout = this._legendRowMouseOut),
                    ((t = document.createElement("td")).innerHTML = m),
                    e.appendChild(t),
                    ((t = document.createElement("td")).innerHTML = '<div style="text-align:left;">' + c + "</div>"),
                    e.appendChild(t),
                    ((t = document.createElement("td")).innerHTML = '<div style="text-align:right;">' + d + "</div>"),
                    e.appendChild(t),
                    r.appendChild(e);
            }
            if (0 === r.rows.length) ((e = document.createElement("tr"))._id = -1), ((t = document.createElement("td")).colSpan = 3), (t.style.width = "450px"), (t.innerHTML = "No features on map."), e.appendChild(t), r.appendChild(e);
            else if (r.rows.length > 1) {
                -1 === r.rows[0]._id && r.deleteRow(0);
                let e = Array.prototype.slice.call(r.rows);
                e.sort(function (e, t) {
                    return e.cells[0].innerHTML.localeCompare(t.cells[0].innerHTML);
                });
                let t = document.createElement("tbody");
                for (let i in e) t.appendChild(e[i]);
                document.getElementById("importsLegendTable").replaceChild(t, r);
            }
            this._overlay.isShown(i.id) || this._overlay.show(i.id, { position: "rightcenter" });
        },
        _legendRowMouseOver: function (e) {
            let t = e.target.parentNode;
            "DIV" === e.target.nodeName && (t = t.parentNode),
                (t.style.background = "#b3b3b3"),
                (t._saveStyle = { color: t._layer.options.color, fillColor: t._layer.options.fillColor }),
                t._layer.setStyle && t._layer.setStyle({ color: "red", fillColor: "#ffb84d" });
        },
        _legendRowMouseOut: function (e) {
            let t = e.target.parentNode;
            "DIV" === e.target.nodeName && (t = t.parentNode), (t.style.background = ""), t._layer.setStyle && t._layer.setStyle(t._saveStyle), (t._saveStyle = null);
        },
        _layerInBounds: function (e, t) {
            return e.getBounds ? e.getBounds().intersects(t) : t.contains(e.getLatLng());
        },
    }),
    "9443" == location.port && (console.log("Loading devel overrides."), (Constants.urls.pylaski = "https://firemap.sdsc.edu/pylaski/"), (Constants.webview.port = 9443), (Constants.camimg_html = "camimg-devel.html"));
var firemap = (function () {
    var e,
        t,
        a,
        r,
        n,
        s,
        o,
        d,
        m,
        c,
        u,
        h,
        p,
        _,
        y,
        f,
        g,
        v,
        w,
        b = new LoadJS(),
        S = !1,
        x = [],
        T = !1,
        C = new Utils();
    function I() {
        webview
            .login()
            .fail(function (e) {
                "Unauthorized" === e
                    ? firemap.checkPassword(I, "Wrong username or password.")
                    : "Account not yet approved." === e || "Account has expired." === e
                    ? firemap.checkPassword(I, e)
                    : firemap.overlay.showMessageOverlay("Failed to login: " + e);
            })
            .done(function (e) {
                F(e);
            });
    }
    function F(i) {
        var s, o, l, d, m;
        (S = !0),
            (document.getElementById("passwordStatus").innerHTML = "Please enter your password."),
            p.getContainer() && p.removeFrom(e),
            v.getContainer() && v.removeFrom(e),
            y.getContainer() && y.removeFrom(e),
            f && f.getContainer() && f.removeFrom(e),
            g.getContainer() && g.removeFrom(e),
            _.addTo(e),
            firemap.overlay.close("passwordOverlay"),
            (i.channels = []),
            (i.admins = []);
        let c = !1;
        if (i.admin) for (s in i.admin) "*" === i.admin[s] && (c = !0);
        for (s in i.groups)
            firemap.fire ||
                (!c && "firemod" !== i.groups[s]) ||
                ((firemap.fire = new FireModeling({ map: e, mapLayers: t, firemap: firemap, webview: webview, copiedFireOptions: T, WeatherStationsLayer: a, WeatherForecastLayer: r, user: i })),
                firemap.fire.enable(),
                n.setCameraClickListener(function (e) {
                    firemap.fire.addIgnitionPoint(e);
                }),
                n.setAdvanced(!0));
        if (i.metadata)
            for (s in i.metadata)
                i.metadata[s].wmsName || i.metadata[s].betterWms
                    ? i.metadata[s].wmsName &&
                      ((d = i.metadata[s].wmsURL || Constants.urls.wms),
                      (l = { layers: i.metadata[s].wmsName, format: "image/png8", transparent: !0, version: "1.1.0", attribution: "", zIndex: i.metadata[s].zindex || 9999, detectRetina: retina }),
                      (i.metadata[s].hasOwnProperty("cache") && !0 !== i.metadata[s].cache) || (l.tiled = !0),
                      i.metadata[s].betterwms
                          ? ((l.jsonpCallback = i.metadata[s].betterwms.callback),
                            (l.boldNames = i.metadata[s].betterwms.boldNames),
                            (l.title = i.metadata[s].name),
                            (l.updateProperties = userMetadataLayers.updateProperties(i.metadata[s].name)),
                            (o = L.tileLayer.betterWms(d, l)))
                          : (o = L.tileLayer.wms(d, l)),
                      i.metadata[s].legend && ((m = i.metadata[s].legend).title || (m.title = i.metadata[s].name), new LegendOverlay(e, o, firemap.overlay, m)),
                      t.addNestedOverlay(o, i.metadata[s].name, i.metadata[s].category),
                      x.push(o))
                    : i.metadata[s].layerFunction && ((o = new Function("return new " + i.metadata[s].layerFunction + "()")()), t.addNestedOverlay(o, i.metadata[s].name, i.metadata[s].category), x.push(o));
        x.length > 0 && h.loadLayers(), v.addTo(e), y.addTo(e), f && f.addTo(e), g.addTo(e), C.adjustIconsInButtons();
    }
    function O(i) {
        S = !1;
        var a = h.getIgnoreLayer();
        for (l in (h.ignoreLayer(function (e) {
            return !0;
        }),
        (firemap.user.name = null),
        (firemap.user.password = null),
        webview.setUsername(null),
        webview.setPassword(null),
        x))
            e.removeLayer(x[l]), t.removeLayer(x[l]);
        (x = []),
            firemap.fire && (firemap.fire.disable(), (firemap.fire = null), n.setCameraClickListener(null), n.setAdvanced(!1)),
            h.ignoreLayer(a),
            _.getContainer() && _.removeFrom(e),
            _.getContainer() && y.removeFrom(e),
            v.getContainer() && v.removeFrom(e),
            f && f.getContainer() && f.removeFrom(e),
            _.getContainer() && g.removeFrom(e),
            p.addTo(e),
            v.addTo(e),
            y.addTo(e),
            f && f.addTo(e),
            g.addTo(e),
            C.adjustIconsInButtons();
    }
    return (
        (retina = !0),
        (webview = new WebView(Constants.webview.host, Constants.webview.port, !0)),
        (userMetadataLayers = new UserMetadataLayers()),
        (EULA_VERSION = "3"),
        (wxTypes = ["Air Temperature", "Humidity", "Fuel Moisture", "Wind", "Gust"]),
        (aqTypes = ["PM2.5", "PM10", "NO2", "SO2", "Ozone", "CO", "Black Carbon"]),
        (yourLocationIcon = L.AwesomeMarkers.icon({ markerColor: "blue", icon: "dot-circle-o", prefix: "fa" })),
        (addressSearchIcon = L.AwesomeMarkers.icon({ icon: "search", prefix: "fa" })),
        $(document).ready(function () {
            var l = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
                    attribution: "Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012",
                    maxZoom: 18,
                    zIndex: -999,
                }),
                c = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", {
                    attribution: "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community",
                    maxZoom: 18,
                    zIndex: -999,
                }),
                S = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
                    attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
                    detectRetina: retina,
                    maxZoom: 18,
                    zIndex: -999,
                }),
                x = L.tileLayer.wms("https://swat.sdsc.edu/geoserver/wms", {
                    layers: "WIFIRE:osm_roads",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "&copy; OpenStreetMap contributors",
                    zIndex: Constants.zLayers.roads,
                    detectRetina: retina,
                }),
                T = L.featureGroup(),
                M = C.createSlider({ id: "wxType", start: 0, step: 1, min: 0, max: wxTypes.length - 1, textId: ["wxTypeVal"], formatMap: wxTypes });
            M.noUiSlider.on("set", function () {
                e.hasLayer(a) && a.redraw();
            }),
                (a = new WeatherStations({ wxTypeSlider: M, wxErrorZoomIn: "wxErrorZoomIn", wxChartControl: "wxChartControl", wxTypeControl: "wxTypeControl" }, { overlay: firemap.overlay, zIndex: Constants.zLayers.wxStation })),
                (firemap.cameras = n = new PTZCameraStations({ overlay: firemap.overlay })),
                (s = new FixedCameraStations({ overlay: firemap.overlay })),
                (o = new RealTimeWeatherStations({ wxTypeSlider: M, wxTypeControl: "wxTypeControl" }, { overlay: firemap.overlay, zIndex: Constants.zLayers.realTimeWxStation }));
            var E = C.createSlider({ id: "aqType", start: 0, step: 1, min: 0, max: aqTypes.length - 1, textId: ["aqTypeVal"], formatMap: aqTypes });
            E.noUiSlider.on("set", function () {
                e.hasLayer(AirQualityStationsLayer) && AirQualityStationsLayer.redraw();
            }),
                (AirQualityStationsLayer = new AirQualityStations({ aqTypeSlider: E, aqChartControl: "aqChartControl", aqTypeControl: "aqTypeControl" }, { overlay: firemap.overlay })),
                (d = new HistoricalFires({ overlay: firemap.overlay, utils: C })),
                (LandfireFuel2014Layer = new LandfireFuel({ overlay: firemap.overlay }));
            var B = new LandfireVegetation(),
                k = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:conus-cc-2014",
                    jsonpCallback: "getJsonCanopyCover",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.0",
                    attribution: 'Canopy Cover Courtesy of <a href="http://landfire.gov">USGS Landfire Program</a>',
                    zIndex: Constants.zLayers.canopyCover,
                    detectRetina: retina,
                    title: "Canopy Cover",
                    tiled: !0,
                    updateProperties: function (e) {
                        (e.Cover = e.GRAY_INDEX + "%"), delete e.GRAY_INDEX;
                    },
                }),
                P = function (e) {
                    (e.acq_datetime = moment(e.acq_date + " " + e.acq_time, "YYYY-MM-DDZ HH:mm:ssZ ")
                        .tz(Constants.tz)
                        .format("YYYY-MM-DD HH:mm z")),
                        delete e.acq_date,
                        delete e.acq_time,
                        delete e.seconds_ago;
                },
                D = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:view_viirs_iband",
                    jsonpCallback: "getJsonViirs",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "NASA VIIRS",
                    zIndex: Constants.zLayers.viirsFire,
                    detectRetina: retina,
                    cql_filter: "seconds_ago < 604800",
                    title: "VIIRS Detection",
                    boldNames: ["acq_datetime"],
                    updateProperties: P,
                }),
                A = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:view_viirs_nf30",
                    jsonpCallback: "getJsonViirsNF",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "NOAA VIIRS Nightfire",
                    zIndex: Constants.zLayers.viirsFire + 1,
                    detectRetina: retina,
                    cql_filter: "seconds_ago < 604800",
                    title: "VIIRS Nightfire Detection",
                    boldNames: ["date_proc"],
                    updateProperties: function (e) {
                        (e.date_proc = moment(e.date_proc).tz(Constants.tz).format("YYYY-MM-DD HH:mm z")),
                            delete e.seconds_ago,
                            delete e.id_key,
                            delete e.qf_detect,
                            delete e.qf_fit,
                            delete e.diameter,
                            (e.ir_source_temp = ((9 * (e.temp_bb - 273.15)) / 5 + 32).toFixed(0) + " F"),
                            delete e.temp_bb,
                            (e.earth_temp = ((9 * (e.temp_bkg - 273.15)) / 5 + 32).toFixed(0) + " F"),
                            delete e.temp_bkg,
                            (e.area_bb += " m2"),
                            (e.area_pixel += " m2"),
                            999999 === e.methane_eq && delete e.methane_eq,
                            999999 === e.co2_eq && delete e.co2_eq;
                    },
                }),
                R = L.featureGroup([D, A]);
            R.setOpacity = function (e) {
                this.eachLayer(function (t) {
                    t.setOpacity(e);
                });
            };
            var N = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:view_modis_c6",
                    jsonpCallback: "getJsonModis",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "NASA MODIS",
                    zIndex: Constants.zLayers.modisFire,
                    detectRetina: retina,
                    cql_filter: "seconds_ago < 604800",
                    title: "MODIS Detection",
                    boldNames: ["acq_datetime"],
                    updateProperties: P,
                }),
                W = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:nws_watches_warnings_kml_view",
                    jsonpCallback: "getJsonNWSWatchesWarnings",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "NWS",
                    zIndex: Constants.zLayers.redFlag,
                    detectRetina: retina,
                    opacity: 0.8,
                    title: "NWS Watches and Warnings",
                    boldNames: ["type"],
                    updateProperties: function (e) {
                        delete e.created_time,
                            delete e.id,
                            delete e.last_modified,
                            (e.issued_by = e.issued_by.substring(e.issued_by.indexOf("Nat"), e.issued_by.length)),
                            "Fire Weather Warning" == e.type && (e.type = "Red Flag Warning"),
                            (e.expiration = moment(e.expiration).tz(Constants.tz).format("YYYY-MM-DD HH:mm z"));
                    },
                }),
                H = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:nifc_active",
                    jsonpCallback: "getJsonActivePerimeter",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "NIFC",
                    zIndex: Constants.zLayers.activeFires,
                    detectRetina: retina,
                    title: "Active Perimeters",
                    boldNames: ["incidentname"],
                }),
                z = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:hms_smoke",
                    jsonpCallback: "getJsonSmoke",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "NOAA Hazard Mapping System",
                    zIndex: Constants.zLayers.modisFire,
                    detectRetina: retina,
                    cql_filter: "end_time > '" + moment().utc().format("MMM DD, YYYY") + "' and start_time < '" + moment().utc().add(1, "days").format("MMM DD, YYYY") + "'",
                    title: "Smoke Analysis",
                    updateProperties: function (e) {
                        delete e.created_time, delete e.density, delete e.start_time, (e.end_time = moment.utc(e.end_time).local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z"));
                    },
                }),
                Y = L.tileLayer.betterWms(Constants.urls.wms, {
                    layers: "WIFIRE:goes_channel7_cmi_view",
                    jsonpCallback: "getJsonGoesC7Polygon",
                    format: "image/png8",
                    transparent: !0,
                    version: "1.1.1",
                    attribution: "",
                    zIndex: 99999,
                    detectRetina: !0,
                    cql_filter: "seconds_ago < 21600",
                    title: "GOES SWIR",
                    boldNames: ["time"],
                    updateProperties: function (e) {
                        var t = /OR_ABI-L1b-RadC-M6C07_G(\d+)_s\d+_e\d+_c(\d+).nc/.exec(e.source);
                        (e.source = "GOES" + t[1]),
                            (e.time = moment.utc(t[2], "YYYYDDDHHmmssSSS").local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")),
                            delete e.id,
                            delete e.seconds_ago,
                            delete e.file_timestamp,
                            (e.created_time = moment.utc(e.created_time).local().tz(Constants.tz).format("YYYY-MM-DD HH:mm z")),
                            (e.temperature = (1.8 * (e.temperature - 273) + 32).toFixed(0) + " F");
                    },
                }),
                U = new GOESGeoColor({ overlay: firemap.overlay });
            (m = new NASAGIBS({ overlay: firemap.overlay })), (r = new WeatherForecast());
            var j,
                V,
                G = L.layerGroup();
            if (
                ((e = new L.Map("map", { zoomControl: !1, maxBounds: L.latLngBounds(L.latLng(-90, -180), L.latLng(90, 180)), minZoom: 5 })),
                (t = L.control.layers
                    .treeopacity(
                        { Streets: l, Topography: c, Satellite: S },
                        {
                            "Boundaries and Regions": {},
                            Infrastructure: {},
                            Weather: { "Weather Stations": a, "HPWREN Real-time Weather Stations": o, "Air Quality Stations": AirQualityStationsLayer, "Watches and Warnings": W, "Weather Forecast": r },
                            Cameras: { "ALERTWildfire PTZ Cameras": n, "HPWREN Fixed Cameras": s },
                            Fuels: { "Surface Fuels": LandfireFuel2014Layer, "Vegetation Type": B, "Canopy Cover": k },
                            Fires: { "Active Perimeters": H, "Historical Fires": d, "Satellite Fire Detections - VIIRS": R, "Satellite Fire Detections - MODIS": N, "Satellite SWIR - GOES": Y, "Smoke Analysis": z },
                            "Satellite Imagery": { "GOES GeoColor": U, "NASA GIBS": m },
                            Barriers: {},
                            Experimental: {},
                            "Street Names": T,
                            "Your Location": G,
                        },
                        { autoZIndex: !1, collapsed: !0, opacity: !0 }
                    )
                    .addTo(e)),
                (h = L.mapState(e, { zoom: 9, lat: 33.580865, lng: -117.13408, layerControl: t }).ignoreLayer(function (e) {
                    return -1 !== e.name.search("Ignition") || -1 !== e.name.search("Fire Model Perimeters");
                })),
                firemap.overlay.setState(h),
                location.search)
            )
                for (i in (j = location.search.substring(1).split("&")))
                    "c" === (V = j[i].split(/[=,]/))[0] ? (3 !== V.length ? console.log("need lat,lon with center: " + V) : e.setView([V[1], V[2]])) : console.log("unknown url parameter: " + V[0]);
            var q = L.control({ position: "topleft" });
            (q.onAdd = function (e) {
                var t = document.createElement("div");
                return (t.innerHTML = '<a href="http://wifire.ucsd.edu" target="#"><img class="logos" src="lib/images/wifire-nsf.png"></a>'), t;
            }),
                q.addTo(e),
                L.Browser.touch || L.control.zoom({ position: "topleft" }).addTo(e),
                L.control.mousePosition({ position: "bottomright" }).addTo(e),
                L.control.scale({ position: "bottomright" }).addTo(e);
            var Z,
                J,
                Q = e._createPane("leaflet-top-pane", e.getPanes().mapPane);
            Q.style.pointerEvents = "none";
            let X = function (t) {
                let i;
                e.hasLayer(x) && (i = Z !== S || e.hasLayer(LandfireFuel2014Layer) || e.hasLayer(B) ? "osm_roads_florent_black" : "osm_roads_florent") != J && (x.setParams({ styles: i }), (J = i));
            };
            e.on("baselayerchange", function (e) {
                (Z = e.layer), X();
            })
                .on("overlayadd", function (t) {
                    t.layer == R || t.layer == N
                        ? firemap.overlay.show("satelliteLegend")
                        : t.layer == W
                        ? firemap.overlay.show("wxHazWarnLegend")
                        : t.layer.ensembleLayer
                        ? this.addLayer(t.layer.ensembleLayer)
                        : t.layer == G
                        ? (e.locate({ setView: !1, enableHighAccuracy: !0 }),
                          (u = window.setInterval(function () {
                              e.locate({ setView: !1 });
                          }, 3e4)))
                        : t.layer === T && (x.addTo(e), Q.appendChild(x.getContainer())),
                        X();
                })
                .on("overlayremove", function (t) {
                    (t.layer != R && t.layer != N) || e.hasLayer(R) || e.hasLayer(N)
                        ? t.layer == W
                            ? firemap.overlay.close("wxHazWarnLegend")
                            : t.layer == G
                            ? (G.clearLayers(), window.clearInterval(u))
                            : t.layer === T && (Q.appendChild(x.getContainer()), e.removeLayer(x))
                        : firemap.overlay.close("satelliteLegend"),
                        X();
                })
                .on("locationfound", function (e) {
                    var t,
                        i,
                        a = G.getLayers();
                    0 == a.length
                        ? (G.addLayer(L.marker(e.latlng, { icon: yourLocationIcon, title: "You are here." })), G.addLayer(L.circle(e.latlng, e.accuracy, { weight: 2 })))
                        : (a[0].setLatLng(e.latlng), a[1].setLatLng(e.latlng).setRadius(e.accuracy)),
                        (t = "You are here.<br/>Last updated: " + moment(e.timestamp).format("HH:mm:ss MMM d YYYY") + "<br/>"),
                        e.accuracy && ((i = e.accuracy * Constants.M_TO_FT) > Constants.MI_TO_FT ? (t += "Accuracy: " + (i / Constants.MI_TO_FT).toFixed(2) + " miles.") : (t += "Accuracy: " + i.toFixed(2) + " feet.")),
                        e.speed && (t += "Speed: " + e.speed * Constants.MPS_TO_MPH + "mph<br/>"),
                        G.getLayers()[0].unbindPopup().bindPopup(t);
                })
                .on("locationerror", function (e) {
                    console.log("location error: " + e.message);
                })
                .on("click", function (e) {
                    this.contextmenu.hide();
                });
            var K = L.control({ position: "bottomright" });
            (K.onAdd = function (e) {
                var t = document.createElement("div");
                return $("#wxStatusControl").appendTo(t), t;
            }),
                e.addControl(K),
                (p = L.easyButton(
                    "fa-sign-in fa-lg easyButtonLg",
                    function (e, t) {
                        firemap.checkPassword(I);
                    },
                    "Login"
                )),
                (_ = L.easyButton(
                    "fa-sign-out fa-lg easyButtonLg",
                    function (e, t) {
                        webview
                            .logout()
                            .fail(function (e) {
                                console.log(e), alert("Unable to logout: " + e);
                            })
                            .done(O);
                    },
                    "Logout"
                )),
                h.loadLayers("Streets"),
                (v = new L.esri.Geocoding.Controls.Geosearch({ useMapBounds: !1, useArcgisWorldGeocoder: !1, providers: [new L.esri.Geocoding.Controls.Geosearch.Providers.WIFIRE()] }));
            var ee,
                te = L.layerGroup().addTo(e);
            (v.on("results", function (e) {
                for (i in (te.clearLayers(), e.results)) te.addLayer(L.marker(e.results[i].latlng, { icon: addressSearchIcon, title: "Search Location" }).bindPopup('<div class="subTitle">' + e.results[i].text + "</div>"));
            }),
            (y = L.easyButton(
                "fa-dot-circle-o fa-lg easyButtonLg",
                function (e, t) {
                    t.hasLayer(G) || t.addLayer(G), t.locate({ setView: !0 });
                },
                "Find your location."
            )),
            (L.Browser.edge = "msLaunchUri" in navigator && !("documentMode" in document)),
            L.Browser.edge && (L.Browser.ie = !0),
            (!L.Browser.chrome && !L.Browser.gecko) ||
                L.Browser.edge ||
                ((w = L.easyPrint({ hidden: !0, exportOnly: !0, hideClasses: ["leaflet-control-layers", "leaflet-control-zoom", "easy-button-container", "leaflet-bar"], sizeModes: ["Current"] }).addTo(e)),
                (f = L.easyButton(
                    "fa-print fa-lg easyButtonLg",
                    function (e, t) {
                        firemap.overlay.show("screenCapOverlay");
                    },
                    "Create screen capture image."
                ))),
            (g = L.easyButton(
                "fa-question fa-lg ",
                function (e, t) {
                    firemap.overlay.show("aboutFiremap");
                },
                "About this map."
            )),
            firemap.disableButtons(!1),
            firemap.disableButtons(!1, { id: "downloadOverlay" }),
            document.getElementById("usernameInput").addEventListener("keyup", function (e) {
                e.preventDefault(), 13 === e.keyCode && document.getElementById("passwordInput").focus();
            }),
            document.getElementById("passwordInput").addEventListener("keyup", function (e) {
                e.preventDefault(), 13 === e.keyCode && firemap.submitPassword();
            }),
            (h.load("eula") || "") != EULA_VERSION &&
                $.ajax("liability.txt").done(function (e) {
                    (document.getElementById("eulaText").innerHTML = e), firemap.overlay.show("eulaOverlay");
                }),
            L.DomEvent.disableClickPropagation(document.getElementsByClassName("leaflet-control-container")[0]),
            b.load("lib/v.lazy.js", function () {
                Highcharts.setOptions({ global: { timezoneOffset: new Date().getTimezoneOffset() } }),
                    firemap.overlay.allowDrag({ ignore: ".btn, .rs-handle, .fireButton, select, .slider, .dataTables_scrollBody, .tabulator-cell, [not-draggable], .highcharts-tracker, input, textarea" });
            }),
            webview
                .login()
                .fail(function (e) {
                    O();
                })
                .done(function (e) {
                    F(e);
                }),
            L.Icon.Default.imagePath) ||
                ((ee = location.pathname.lastIndexOf("/") === location.pathname.length - 1 ? location.pathname : location.pathname.substring(0, location.pathname.lastIndexOf("/") + 1)),
                (L.Icon.Default.imagePath = ee + "lib/vendor/images"));
        }),
        {
            overlay: new Overlay(),
            fire: !1,
            cameras: !1,
            user: { name: null, password: null },
            _spinners: {},
            disableButtons: function (e, t) {
                var i,
                    a,
                    r,
                    n,
                    s = "manualFireOverlay";
                for (n in (t && (t.id && (s = t.id), (i = t.except)), (r = (a = document.getElementById(s)).querySelectorAll(".fireButton"))))
                    "manualFireOverlay" == s && "Paste" == r[n].innerHTML ? (r[n].disabled = !T) : i && r[n].innerHTML === i ? (r[n].disabled = !e) : (r[n].disabled = e);
                if (t) {
                    if ("boolean" == typeof t.spinner && t.spinner) return this._spinners[s] ? this._spinners[s] : (this._spinners[s] = new Spinner().spin(a));
                    t.spinner && t.spinner.stop && (t.spinner.stop(), this._spinners[s] && delete this._spinners[s]);
                }
            },
            checkPassword: function (e, t, i) {
                (!firemap.user.password && !S) || t
                    ? ((c = e),
                      t && (document.getElementById("passwordStatus").innerHTML = t),
                      firemap.overlay.show("passwordOverlay"),
                      window.setTimeout(function () {
                          firemap.user.name ? document.getElementById("passwordInput").focus() : document.getElementById("usernameInput").focus();
                      }, 100))
                    : "string" == typeof e
                    ? firemap.overlay.show(e)
                    : e.call(i);
            },
            submitPassword: function () {
                (firemap.user.name = document.getElementById("usernameInput").value || " "),
                    (firemap.user.password = document.getElementById("passwordInput").value || " "),
                    webview.setUsername(firemap.user.name),
                    webview.setPassword(firemap.user.password),
                    "string" == typeof c ? firemap.overlay.swap("passwordOverlay", c) : c();
            },
            screenCapture: function (e) {
                var t = document.getElementById("screenCapFilename").value;
                t && 0 !== t.length ? (w.printMap("Current", t), this.overlay.close("screenCapOverlay")) : this.overlay.showMessageOverlay("Must specify file name.");
            },
            acceptEULA: function () {
                this.overlay.close("eulaOverlay"), h.save("eula", EULA_VERSION);
            },
            showNASAGIBS: function (t, i, a) {
                var r = moment(t, "YYYY-MM-DDZ").toDate();
                e.hasLayer(d) && e.removeLayer(d), e.setView([i, a], 9), e.addLayer(m), m.setDate(r);
            },
        }
    );
})();
