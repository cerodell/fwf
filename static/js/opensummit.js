!(function (e) {
    var t = {};
    function r(o) {
        if (t[o]) return t[o].exports;
        var n = (t[o] = { i: o, l: !1, exports: {} });
        return e[o].call(n.exports, n, n.exports, r), (n.l = !0), n.exports;
    }
    (r.m = e),
        (r.c = t),
        (r.d = function (e, t, o) {
            r.o(e, t) || Object.defineProperty(e, t, { enumerable: !0, get: o });
        }),
        (r.r = function (e) {
            "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, { value: "Module" }), Object.defineProperty(e, "__esModule", { value: !0 });
        }),
        (r.t = function (e, t) {
            if ((1 & t && (e = r(e)), 8 & t)) return e;
            if (4 & t && "object" == typeof e && e && e.__esModule) return e;
            var o = Object.create(null);
            if ((r.r(o), Object.defineProperty(o, "default", { enumerable: !0, value: e }), 2 & t && "string" != typeof e))
                for (var n in e)
                    r.d(
                        o,
                        n,
                        function (t) {
                            return e[t];
                        }.bind(null, n)
                    );
            return o;
        }),
        (r.n = function (e) {
            var t =
                e && e.__esModule
                    ? function () {
                          return e.default;
                      }
                    : function () {
                          return e;
                      };
            return r.d(t, "a", t), t;
        }),
        (r.o = function (e, t) {
            return Object.prototype.hasOwnProperty.call(e, t);
        }),
        (r.p = "/"),
        r((r.s = 0));
})({
    0: function (e, t, r) {
        r("mUkR"), r("S27s"), (e.exports = r("paDV"));
    },
    S27s: function (e, t) {},
    ls82: function (e, t, r) {
        var o = (function (e) {
            "use strict";
            var t = Object.prototype,
                r = t.hasOwnProperty,
                o = "function" == typeof Symbol ? Symbol : {},
                n = o.iterator || "@@iterator",
                a = o.asyncIterator || "@@asyncIterator",
                i = o.toStringTag || "@@toStringTag";
            function s(e, t, r, o) {
                var n = t && t.prototype instanceof u ? t : u,
                    a = Object.create(n.prototype),
                    i = new O(o || []);
                return (
                    (a._invoke = (function (e, t, r) {
                        var o = "suspendedStart";
                        return function (n, a) {
                            if ("executing" === o) throw new Error("Generator is already running");
                            if ("completed" === o) {
                                if ("throw" === n) throw a;
                                return k();
                            }
                            for (r.method = n, r.arg = a; ; ) {
                                var i = r.delegate;
                                if (i) {
                                    var s = b(i, r);
                                    if (s) {
                                        if (s === c) continue;
                                        return s;
                                    }
                                }
                                if ("next" === r.method) r.sent = r._sent = r.arg;
                                else if ("throw" === r.method) {
                                    if ("suspendedStart" === o) throw ((o = "completed"), r.arg);
                                    r.dispatchException(r.arg);
                                } else "return" === r.method && r.abrupt("return", r.arg);
                                o = "executing";
                                var u = l(e, t, r);
                                if ("normal" === u.type) {
                                    if (((o = r.done ? "completed" : "suspendedYield"), u.arg === c)) continue;
                                    return { value: u.arg, done: r.done };
                                }
                                "throw" === u.type && ((o = "completed"), (r.method = "throw"), (r.arg = u.arg));
                            }
                        };
                    })(e, r, i)),
                    a
                );
            }
            function l(e, t, r) {
                try {
                    return { type: "normal", arg: e.call(t, r) };
                } catch (e) {
                    return { type: "throw", arg: e };
                }
            }
            e.wrap = s;
            var c = {};
            function u() {}
            function p() {}
            function f() {}
            var d = {};
            d[n] = function () {
                return this;
            };
            var y = Object.getPrototypeOf,
                m = y && y(y(j([])));
            m && m !== t && r.call(m, n) && (d = m);
            var h = (f.prototype = u.prototype = Object.create(d));
            function v(e) {
                ["next", "throw", "return"].forEach(function (t) {
                    e[t] = function (e) {
                        return this._invoke(t, e);
                    };
                });
            }
            function g(e, t) {
                var o;
                this._invoke = function (n, a) {
                    function i() {
                        return new t(function (o, i) {
                            !(function o(n, a, i, s) {
                                var c = l(e[n], e, a);
                                if ("throw" !== c.type) {
                                    var u = c.arg,
                                        p = u.value;
                                    return p && "object" == typeof p && r.call(p, "__await")
                                        ? t.resolve(p.__await).then(
                                              function (e) {
                                                  o("next", e, i, s);
                                              },
                                              function (e) {
                                                  o("throw", e, i, s);
                                              }
                                          )
                                        : t.resolve(p).then(
                                              function (e) {
                                                  (u.value = e), i(u);
                                              },
                                              function (e) {
                                                  return o("throw", e, i, s);
                                              }
                                          );
                                }
                                s(c.arg);
                            })(n, a, o, i);
                        });
                    }
                    return (o = o ? o.then(i, i) : i());
                };
            }
            function b(e, t) {
                var r = e.iterator[t.method];
                if (void 0 === r) {
                    if (((t.delegate = null), "throw" === t.method)) {
                        if (e.iterator.return && ((t.method = "return"), (t.arg = void 0), b(e, t), "throw" === t.method)) return c;
                        (t.method = "throw"), (t.arg = new TypeError("The iterator does not provide a 'throw' method"));
                    }
                    return c;
                }
                var o = l(r, e.iterator, t.arg);
                if ("throw" === o.type) return (t.method = "throw"), (t.arg = o.arg), (t.delegate = null), c;
                var n = o.arg;
                return n
                    ? n.done
                        ? ((t[e.resultName] = n.value), (t.next = e.nextLoc), "return" !== t.method && ((t.method = "next"), (t.arg = void 0)), (t.delegate = null), c)
                        : n
                    : ((t.method = "throw"), (t.arg = new TypeError("iterator result is not an object")), (t.delegate = null), c);
            }
            function w(e) {
                var t = { tryLoc: e[0] };
                1 in e && (t.catchLoc = e[1]), 2 in e && ((t.finallyLoc = e[2]), (t.afterLoc = e[3])), this.tryEntries.push(t);
            }
            function x(e) {
                var t = e.completion || {};
                (t.type = "normal"), delete t.arg, (e.completion = t);
            }
            function O(e) {
                (this.tryEntries = [{ tryLoc: "root" }]), e.forEach(w, this), this.reset(!0);
            }
            function j(e) {
                if (e) {
                    var t = e[n];
                    if (t) return t.call(e);
                    if ("function" == typeof e.next) return e;
                    if (!isNaN(e.length)) {
                        var o = -1,
                            a = function t() {
                                for (; ++o < e.length; ) if (r.call(e, o)) return (t.value = e[o]), (t.done = !1), t;
                                return (t.value = void 0), (t.done = !0), t;
                            };
                        return (a.next = a);
                    }
                }
                return { next: k };
            }
            function k() {
                return { value: void 0, done: !0 };
            }
            return (
                (p.prototype = h.constructor = f),
                (f.constructor = p),
                (f[i] = p.displayName = "GeneratorFunction"),
                (e.isGeneratorFunction = function (e) {
                    var t = "function" == typeof e && e.constructor;
                    return !!t && (t === p || "GeneratorFunction" === (t.displayName || t.name));
                }),
                (e.mark = function (e) {
                    return Object.setPrototypeOf ? Object.setPrototypeOf(e, f) : ((e.__proto__ = f), i in e || (e[i] = "GeneratorFunction")), (e.prototype = Object.create(h)), e;
                }),
                (e.awrap = function (e) {
                    return { __await: e };
                }),
                v(g.prototype),
                (g.prototype[a] = function () {
                    return this;
                }),
                (e.AsyncIterator = g),
                (e.async = function (t, r, o, n, a) {
                    void 0 === a && (a = Promise);
                    var i = new g(s(t, r, o, n), a);
                    return e.isGeneratorFunction(r)
                        ? i
                        : i.next().then(function (e) {
                              return e.done ? e.value : i.next();
                          });
                }),
                v(h),
                (h[i] = "Generator"),
                (h[n] = function () {
                    return this;
                }),
                (h.toString = function () {
                    return "[object Generator]";
                }),
                (e.keys = function (e) {
                    var t = [];
                    for (var r in e) t.push(r);
                    return (
                        t.reverse(),
                        function r() {
                            for (; t.length; ) {
                                var o = t.pop();
                                if (o in e) return (r.value = o), (r.done = !1), r;
                            }
                            return (r.done = !0), r;
                        }
                    );
                }),
                (e.values = j),
                (O.prototype = {
                    constructor: O,
                    reset: function (e) {
                        if (((this.prev = 0), (this.next = 0), (this.sent = this._sent = void 0), (this.done = !1), (this.delegate = null), (this.method = "next"), (this.arg = void 0), this.tryEntries.forEach(x), !e))
                            for (var t in this) "t" === t.charAt(0) && r.call(this, t) && !isNaN(+t.slice(1)) && (this[t] = void 0);
                    },
                    stop: function () {
                        this.done = !0;
                        var e = this.tryEntries[0].completion;
                        if ("throw" === e.type) throw e.arg;
                        return this.rval;
                    },
                    dispatchException: function (e) {
                        if (this.done) throw e;
                        var t = this;
                        function o(r, o) {
                            return (i.type = "throw"), (i.arg = e), (t.next = r), o && ((t.method = "next"), (t.arg = void 0)), !!o;
                        }
                        for (var n = this.tryEntries.length - 1; n >= 0; --n) {
                            var a = this.tryEntries[n],
                                i = a.completion;
                            if ("root" === a.tryLoc) return o("end");
                            if (a.tryLoc <= this.prev) {
                                var s = r.call(a, "catchLoc"),
                                    l = r.call(a, "finallyLoc");
                                if (s && l) {
                                    if (this.prev < a.catchLoc) return o(a.catchLoc, !0);
                                    if (this.prev < a.finallyLoc) return o(a.finallyLoc);
                                } else if (s) {
                                    if (this.prev < a.catchLoc) return o(a.catchLoc, !0);
                                } else {
                                    if (!l) throw new Error("try statement without catch or finally");
                                    if (this.prev < a.finallyLoc) return o(a.finallyLoc);
                                }
                            }
                        }
                    },
                    abrupt: function (e, t) {
                        for (var o = this.tryEntries.length - 1; o >= 0; --o) {
                            var n = this.tryEntries[o];
                            if (n.tryLoc <= this.prev && r.call(n, "finallyLoc") && this.prev < n.finallyLoc) {
                                var a = n;
                                break;
                            }
                        }
                        a && ("break" === e || "continue" === e) && a.tryLoc <= t && t <= a.finallyLoc && (a = null);
                        var i = a ? a.completion : {};
                        return (i.type = e), (i.arg = t), a ? ((this.method = "next"), (this.next = a.finallyLoc), c) : this.complete(i);
                    },
                    complete: function (e, t) {
                        if ("throw" === e.type) throw e.arg;
                        return (
                            "break" === e.type || "continue" === e.type
                                ? (this.next = e.arg)
                                : "return" === e.type
                                ? ((this.rval = this.arg = e.arg), (this.method = "return"), (this.next = "end"))
                                : "normal" === e.type && t && (this.next = t),
                            c
                        );
                    },
                    finish: function (e) {
                        for (var t = this.tryEntries.length - 1; t >= 0; --t) {
                            var r = this.tryEntries[t];
                            if (r.finallyLoc === e) return this.complete(r.completion, r.afterLoc), x(r), c;
                        }
                    },
                    catch: function (e) {
                        for (var t = this.tryEntries.length - 1; t >= 0; --t) {
                            var r = this.tryEntries[t];
                            if (r.tryLoc === e) {
                                var o = r.completion;
                                if ("throw" === o.type) {
                                    var n = o.arg;
                                    x(r);
                                }
                                return n;
                            }
                        }
                        throw new Error("illegal catch attempt");
                    },
                    delegateYield: function (e, t, r) {
                        return (this.delegate = { iterator: j(e), resultName: t, nextLoc: r }), "next" === this.method && (this.arg = void 0), c;
                    },
                }),
                e
            );
        })(e.exports);
        try {
            regeneratorRuntime = o;
        } catch (e) {
            Function("r", "regeneratorRuntime = r")(o);
        }
    },
    mUkR: function (e, t, r) {
        "use strict";
        r.r(t);
        var o = r("o0o1"),
            n = r.n(o);
        function a(e, t) {
            var r = Object.keys(e);
            if (Object.getOwnPropertySymbols) {
                var o = Object.getOwnPropertySymbols(e);
                t &&
                    (o = o.filter(function (t) {
                        return Object.getOwnPropertyDescriptor(e, t).enumerable;
                    })),
                    r.push.apply(r, o);
            }
            return r;
        }
        function i(e, t, r) {
            return t in e ? Object.defineProperty(e, t, { value: r, enumerable: !0, configurable: !0, writable: !0 }) : (e[t] = r), e;
        }
        function s(e) {
            return (
                (function (e) {
                    if (Array.isArray(e)) {
                        for (var t = 0, r = new Array(e.length); t < e.length; t++) r[t] = e[t];
                        return r;
                    }
                })(e) ||
                (function (e) {
                    if (Symbol.iterator in Object(e) || "[object Arguments]" === Object.prototype.toString.call(e)) return Array.from(e);
                })(e) ||
                (function () {
                    throw new TypeError("Invalid attempt to spread non-iterable instance");
                })()
            );
        }
        var l = {
            rala: {
                key: "radar",
                display: "Radar",
                isAnimatable: !0,
                shortDisplay: "Radar",
                tiles: "rala",
                tileTypes: ["contours"],
                tileCount: 16,
                add: function (e, t) {
                    c(l.rala, e, t);
                },
                frames: [],
                idx: 0,
            },
            drrf: {
                key: "drrf",
                display: "Forecast Radar",
                isAnimatable: !0,
                isForecast: !0,
                shortDisplay: "Radar",
                tiles: "drrf",
                tileTypes: ["contours"],
                tileCount: 18,
                add: function (e, t) {
                    c(l.drrf, e, t);
                },
                frames: [],
                idx: 0,
            },
        };
        function c(e, t, r) {
            var o,
                n = e,
                c = t.params.sources[e.tiles],
                u = s(c.tiles.contours);
            if (
                ((o = e == l.rala || r ? u.length - 1 : 0),
                t.overlay == n &&
                    (t.drawLegend(c.legend),
                    t.setIsAnimatable(!0),
                    t.setOpacity(function (e) {
                        var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0.65;
                        t.map.setPaintProperty(e.id, e.opacity, r);
                    })),
                !r && n.frames.length)
            )
                return t.showMostRecent(o), void t.updateSlider(n.frames.length - 1);
            function p(e, r) {
                var o = e.index_json.name;
                t.map.addSource(
                    o,
                    (function (e) {
                        for (var t = 1; t < arguments.length; t++) {
                            var r = null != arguments[t] ? arguments[t] : {};
                            t % 2
                                ? a(Object(r), !0).forEach(function (t) {
                                      i(e, t, r[t]);
                                  })
                                : Object.getOwnPropertyDescriptors
                                ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r))
                                : a(Object(r)).forEach(function (t) {
                                      Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(r, t));
                                  });
                        }
                        return e;
                    })({}, e.index_json, { type: "vector" })
                ),
                    t.map.addLayer(
                        {
                            id: o,
                            type: "fill",
                            source: o,
                            "source-layer": e.source_layer_id,
                            layout: { visibility: t.overlay == n ? "visible" : "none", "fill-sort-key": ["get", "DN"] },
                            paint: {
                                "fill-opacity": 0,
                                "fill-opacity-transition": { duration: 0 },
                                "fill-antialias": !0,
                                "fill-outline-color": "rgba(0,0,0,0)",
                                "fill-color": ["interpolate", ["linear"], ["get", "DN"]].concat(s(t.colorInterpolate(c.legend.steps))),
                            },
                        },
                        "road-primary"
                    ),
                    (n.frames[r] = { sources: [{ id: o, timestamp: e.source_timestamp, type: "contours", layers: [{ id: o, opacity: "fill-opacity" }] }] });
            }
            p(u.splice(o, 1)[0], o),
                r ||
                    (t.showMostRecent(o),
                    u.forEach(function (e, t) {
                        return p(e, 0 == o ? t + 1 : t);
                    }),
                    t.updateSlider(n.frames.length - 1));
        }
        var u = { overlays: l };
        function p(e, t) {
            var r = Object.keys(e);
            if (Object.getOwnPropertySymbols) {
                var o = Object.getOwnPropertySymbols(e);
                t &&
                    (o = o.filter(function (t) {
                        return Object.getOwnPropertyDescriptor(e, t).enumerable;
                    })),
                    r.push.apply(r, o);
            }
            return r;
        }
        function f(e, t, r) {
            return t in e ? Object.defineProperty(e, t, { value: r, enumerable: !0, configurable: !0, writable: !0 }) : (e[t] = r), e;
        }
        function d(e) {
            return (
                (function (e) {
                    if (Array.isArray(e)) {
                        for (var t = 0, r = new Array(e.length); t < e.length; t++) r[t] = e[t];
                        return r;
                    }
                })(e) ||
                (function (e) {
                    if (Symbol.iterator in Object(e) || "[object Arguments]" === Object.prototype.toString.call(e)) return Array.from(e);
                })(e) ||
                (function () {
                    throw new TypeError("Invalid attempt to spread non-iterable instance");
                })()
            );
        }
        var y = {
                low: {
                    key: "smoke-low",
                    isForecast: !0,
                    isAnimatable: !0,
                    display: "Smoke (surface)",
                    tiles: "smoke-low",
                    tileTypes: ["contours"],
                    tileCount: 19,
                    add: function (e, t) {
                        h(y.low, e, t);
                    },
                    frames: [],
                    idx: 0,
                },
                high: {
                    key: "smoke-high",
                    isForecast: !0,
                    isAnimatable: !0,
                    display: "Smoke (sky)",
                    tiles: "smoke-high",
                    tileTypes: ["contours"],
                    tileCount: 19,
                    add: function (e, t) {
                        h(y.high, e, t);
                    },
                    frames: [],
                    idx: 0,
                },
            },
            m = { light: [0, 0, 0.1, 0.001, 1, 0.005, 5, 0.15, 50, 0.25, 100, 0.35, 250, 0.65], dark: [0, 0, 0.1, 0.001, 1, 0.005, 5, 0.05, 50, 0.1, 100, 0.25, 250, 0.65] };
        function h(e, t, r) {
            var o = t.params.sources[e.tiles],
                n = d(o.tiles.contours),
                a = "dark" == t.style.key || "satellite" == t.style.key ? m.dark : m.light;
            if (
                (t.overlay == e &&
                    (t.drawLegend(o.legend),
                    t.setIsAnimatable(!0),
                    t.setOpacity(function (e) {
                        var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0.2;
                        t.map.setPaintProperty(e.id, e.opacity, "DN" == r ? ["interpolate", ["linear"], ["get", "DN"]].concat(d(a)) : r);
                    })),
                !r && e.frames.length)
            )
                return t.showMostRecent(0), void t.updateSlider(e.frames.length - 1);
            function i(r) {
                var n = r.index_json.name;
                t.map.addSource(
                    n,
                    (function (e) {
                        for (var t = 1; t < arguments.length; t++) {
                            var r = null != arguments[t] ? arguments[t] : {};
                            t % 2
                                ? p(Object(r), !0).forEach(function (t) {
                                      f(e, t, r[t]);
                                  })
                                : Object.getOwnPropertyDescriptors
                                ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r))
                                : p(Object(r)).forEach(function (t) {
                                      Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(r, t));
                                  });
                        }
                        return e;
                    })({}, r.index_json, { type: "vector" })
                ),
                    t.map.addLayer(
                        {
                            id: n,
                            type: "fill",
                            source: n,
                            "source-layer": r.source_layer_id,
                            filter: [">", ["get", "DN"], 1],
                            layout: { "fill-sort-key": ["get", "DN"], visibility: t.overlay == e ? "visible" : "none" },
                            paint: {
                                "fill-antialias": !0,
                                "fill-outline-color": "rgba(0,0,0,0)",
                                "fill-opacity": 0,
                                "fill-opacity-transition": { duration: 250 },
                                "fill-color": ["interpolate", ["linear"], ["get", "DN"]].concat(d(t.colorInterpolate(o.legend.steps))),
                            },
                        },
                        "road-primary"
                    ),
                    e.frames.push({ timestamp: r.source_timestamp, sources: [{ id: n, timestamp: r.source_timestamp, type: "contours", layers: [{ id: n, opacity: "fill-opacity" }] }] });
            }
            r
                ? i(n.pop())
                : (i(n.shift()),
                  t.overlay == e &&
                      (t.showMostRecent(0),
                      n.forEach(function (e) {
                          return i(e);
                      }),
                      t.updateSlider(e.frames.length - 1)));
        }
        var v = { overlays: y };
        function g(e, t) {
            var r = Object.keys(e);
            if (Object.getOwnPropertySymbols) {
                var o = Object.getOwnPropertySymbols(e);
                t &&
                    (o = o.filter(function (t) {
                        return Object.getOwnPropertyDescriptor(e, t).enumerable;
                    })),
                    r.push.apply(r, o);
            }
            return r;
        }
        function b(e) {
            for (var t = 1; t < arguments.length; t++) {
                var r = null != arguments[t] ? arguments[t] : {};
                t % 2
                    ? g(Object(r), !0).forEach(function (t) {
                          w(e, t, r[t]);
                      })
                    : Object.getOwnPropertyDescriptors
                    ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r))
                    : g(Object(r)).forEach(function (t) {
                          Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(r, t));
                      });
            }
            return e;
        }
        function w(e, t, r) {
            return t in e ? Object.defineProperty(e, t, { value: r, enumerable: !0, configurable: !0, writable: !0 }) : (e[t] = r), e;
        }
        function x(e) {
            return (
                (function (e) {
                    if (Array.isArray(e)) {
                        for (var t = 0, r = new Array(e.length); t < e.length; t++) r[t] = e[t];
                        return r;
                    }
                })(e) ||
                (function (e) {
                    if (Symbol.iterator in Object(e) || "[object Arguments]" === Object.prototype.toString.call(e)) return Array.from(e);
                })(e) ||
                (function () {
                    throw new TypeError("Invalid attempt to spread non-iterable instance");
                })()
            );
        }
        var O = {
            key: "snowdepth",
            display: "Snow Depth",
            tiles: "snowdepth",
            tileTypes: ["contours"],
            tileCount: 1,
            add: function (e, t) {
                var r,
                    o,
                    n = O,
                    a = e.params.sources.snowdepth,
                    i = a.tiles.contours[0];
                e.map.getLayer("hillshade") ? ((r = "hillshade"), (o = 0.8)) : ((r = "road-primary"), (o = "zoom"));
                e.overlay == n &&
                    (e.drawLegend(a.legend),
                    e.setOpacity(function (t) {
                        var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o;
                        e.map.setPaintProperty(t.id, t.opacity, "zoom" == r ? ["interpolate", ["linear"], ["zoom"]].concat(x(e.opacityInterpolate(0.5, 0.8))) : r);
                    }));
                if (!t && n.frames.length) return void e.showMostRecent();
                var s = i.index_json.name;
                e.map.addSource(s, b({}, i.index_json, { type: "vector" })),
                    e.map.addLayer(
                        {
                            id: s,
                            type: "fill",
                            source: s,
                            "source-layer": i.source_layer_id,
                            layout: { "fill-sort-key": ["get", "DN"], visibility: e.overlay == n ? "visible" : "none" },
                            paint: { "fill-antialias": !0, "fill-outline-color": "rgba(0,0,0,0)", "fill-opacity": 0, "fill-color": ["interpolate", ["linear"], ["get", "DN"]].concat(x(e.colorInterpolate(a.legend.steps))) },
                        },
                        r
                    ),
                    e.map.addLayer(
                        {
                            id: s + "-label",
                            type: "symbol",
                            source: s,
                            "source-layer": i.source_layer_id,
                            minzoom: 8,
                            layout: {
                                "symbol-sort-key": ["*", ["get", "DN"], -1],
                                "symbol-placement": "line",
                                "symbol-spacing": 350,
                                visibility: e.overlay == n ? "visible" : "none",
                                "text-field": e.isImperial ? ["concat", ["get", "DN"], '"'] : ["concat", ["max", 1, ["*", ["round", ["/", ["*", 2.54, ["get", "DN"]], 5]], 5]], "cm"],
                                "text-font": e.textFont,
                                "text-allow-overlap": !1,
                                "text-rotation-alignment": "viewport",
                                "text-pitch-alignment": "viewport",
                                "text-max-angle": 25,
                                "text-padding": 5,
                                "text-size": ["interpolate", ["linear"], ["zoom"], 12, 16, 20, 12],
                            },
                            paint: {
                                "text-opacity": 0,
                                "text-color": ["step", ["get", "DN"], e.style.textColor, 0, e.style.textColor, 12, e.style.textColorAlt],
                                "text-halo-color": ["step", ["get", "DN"], e.style.textHalo, 0, e.style.textHalo, 12, e.style.textHaloAlt],
                                "text-halo-width": 1,
                            },
                        },
                        e.map.getLayer("point_clusters") ? "point_clusters" : void 0
                    ),
                    n.frames.push({
                        timestamp: i.source_timestamp,
                        sources: [
                            {
                                id: s,
                                timestamp: i.source_timestamp,
                                type: "contours",
                                layers: [
                                    { id: s, opacity: "fill-opacity" },
                                    { id: s + "-label", opacity: "text-opacity" },
                                ],
                            },
                        ],
                    }),
                    e.overlay == n && e.showMostRecent();
            },
            frames: [],
            idx: 0,
        };
        var j = { overlay: O };
        function k(e, t) {
            var r = Object.keys(e);
            if (Object.getOwnPropertySymbols) {
                var o = Object.getOwnPropertySymbols(e);
                t &&
                    (o = o.filter(function (t) {
                        return Object.getOwnPropertyDescriptor(e, t).enumerable;
                    })),
                    r.push.apply(r, o);
            }
            return r;
        }
        function P(e, t, r) {
            return t in e ? Object.defineProperty(e, t, { value: r, enumerable: !0, configurable: !0, writable: !0 }) : (e[t] = r), e;
        }
        function C(e) {
            return (
                (function (e) {
                    if (Array.isArray(e)) {
                        for (var t = 0, r = new Array(e.length); t < e.length; t++) r[t] = e[t];
                        return r;
                    }
                })(e) ||
                (function (e) {
                    if (Symbol.iterator in Object(e) || "[object Arguments]" === Object.prototype.toString.call(e)) return Array.from(e);
                })(e) ||
                (function () {
                    throw new TypeError("Invalid attempt to spread non-iterable instance");
                })()
            );
        }
        var S = {
                key: "temperature",
                isForecast: !0,
                isAnimatable: !0,
                display: "Temperature",
                tiles: "temps",
                tileTypes: ["points", "rasters"],
                tileCount: 19,
                add: function (e, t) {
                    var r,
                        o,
                        n = S,
                        a = e.params.sources.temps,
                        i = C(a.tiles.rasters),
                        s = C(a.tiles.points);
                    "satellite" == e.style.key ? ((r = "tunnel-primary-secondary-tertiary-case"), (o = 0.6)) : "dark" == e.style.key ? ((r = "waterway"), (o = 0.8)) : ((r = "waterway"), (o = 0.9));
                    var l = e.map.getLayer("settlement-label") ? "settlement-label" : "settlement-minor-label";
                    e.overlay == n &&
                        (e.drawLegend(a.legend),
                        e.setIsAnimatable(!0),
                        e.setOpacity(function (t) {
                            var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o;
                            "text-opacity" == t.opacity && r == o && (r = 1), e.map.setPaintProperty(t.id, t.opacity, r);
                        }));
                    if (!t && n.frames.length) return e.showMostRecent(0), void e.updateSlider(n.frames.length - 1);
                    function c(t, o) {
                        var a = t.index_json.name,
                            i = o.index_json.name;
                        e.map.addSource(a, t.index_json),
                            e.map.addSource(
                                i,
                                (function (e) {
                                    for (var t = 1; t < arguments.length; t++) {
                                        var r = null != arguments[t] ? arguments[t] : {};
                                        t % 2
                                            ? k(Object(r), !0).forEach(function (t) {
                                                  P(e, t, r[t]);
                                              })
                                            : Object.getOwnPropertyDescriptors
                                            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r))
                                            : k(Object(r)).forEach(function (t) {
                                                  Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(r, t));
                                              });
                                    }
                                    return e;
                                })({}, o.index_json, { type: "vector" })
                            ),
                            e.map.addLayer({ id: a, type: "raster", source: a, layout: { visibility: e.overlay == n ? "visible" : "none" }, paint: { "raster-opacity": 0, "raster-opacity-transition": { duration: 0, delay: 0 } } }, r),
                            e.map.addLayer(
                                {
                                    type: "symbol",
                                    id: i,
                                    source: i,
                                    "source-layer": o.source_layer_id,
                                    layout: {
                                        visibility: e.overlay == n ? "visible" : "none",
                                        "text-field": e.isCelsius ? ["concat", ["round", ["*", 5 / 9, ["-", ["get", "DN"], 32]]], "Â°"] : ["concat", ["get", "DN"], "Â°"],
                                        "text-font": e.textFont,
                                        "text-offset": [-1.7, 0],
                                        "text-allow-overlap": !1,
                                        "text-ignore-placement": !1,
                                        "text-size": 13,
                                    },
                                    paint: { "text-opacity": 0, "text-opacity-transition": { duration: 100, delay: 0 }, "text-color": e.style.textColor, "text-halo-color": e.style.textHalo, "text-halo-width": 1 },
                                },
                                E && e.map.getLayer(E) ? E : l
                            ),
                            n.frames.push({
                                timestamp: t.source_timestamp,
                                sources: [
                                    { id: a, timestamp: t.source_timestamp, type: "raster", layers: [{ id: a, opacity: "raster-opacity" }] },
                                    { id: i, timestamp: o.source_timestamp, type: "points", hideOnAnimate: !1, moveOnShow: l, layers: [{ id: i, opacity: "text-opacity" }] },
                                ],
                            }),
                            (E = i);
                    }
                    t
                        ? c(i.pop(), s.pop())
                        : (c(i.shift(), s.shift()),
                          e.overlay == n &&
                              (e.showMostRecent(0),
                              i.forEach(function (e, t) {
                                  return c(e, s[t]);
                              }),
                              e.updateSlider(n.frames.length - 1)));
                },
                frames: [],
                idx: 0,
            },
            E = null;
        var _ = { overlay: S };
        function L(e, t, r, o, n, a, i) {
            try {
                var s = e[a](i),
                    l = s.value;
            } catch (e) {
                return void r(e);
            }
            s.done ? t(l) : Promise.resolve(l).then(o, n);
        }
        function A(e) {
            return function () {
                var t = this,
                    r = arguments;
                return new Promise(function (o, n) {
                    var a = e.apply(t, r);
                    function i(e) {
                        L(a, o, n, i, s, "next", e);
                    }
                    function s(e) {
                        L(a, o, n, i, s, "throw", e);
                    }
                    i(void 0);
                });
            };
        }
        function D(e, t) {
            var r = Object.keys(e);
            if (Object.getOwnPropertySymbols) {
                var o = Object.getOwnPropertySymbols(e);
                t &&
                    (o = o.filter(function (t) {
                        return Object.getOwnPropertyDescriptor(e, t).enumerable;
                    })),
                    r.push.apply(r, o);
            }
            return r;
        }
        function T(e, t, r) {
            return t in e ? Object.defineProperty(e, t, { value: r, enumerable: !0, configurable: !0, writable: !0 }) : (e[t] = r), e;
        }
        window.Map = function (e, t) {
            var r,
                o,
                a,
                i,
                s,
                l,
                c,
                p,
                f,
                d = Cookies.get("units") || "us",
                y = "us" == d || "uk" == d,
                m = "us" !== d,
                h = /Mobi|Android/i.test(navigator.userAgent),
                g = !1,
                b = "hsl(0, 0%, 78%)",
                w = "hsla(35, 16%, 100%, 0.5)",
                x = "hsla(0, 0%, 13%, 0.75)",
                O = ["DIN Pro Medium", "Arial Unicode MS Regular"],
                k = t.debug || !1,
                P = {
                    terrain: { key: "terrain", display: "Terrain", url: "mapbox://styles/cloudninewx/ck97cbb5h1hzc1ipdneiocp98?optimize=true", textColor: "hsl(26, 20%, 36%)", textColorAlt: b, textHalo: w, textHaloAlt: x },
                    roads: { key: "roads", display: "Roads", url: "mapbox://styles/mapbox/streets-v11", textColor: "hsl(26, 20%, 36%)", textColorAlt: b, textHalo: w, textHaloAlt: x },
                    dark: { key: "dark", display: "Dark", url: "mapbox://styles/mapbox/dark-v10?optimize=true", textColor: b, textColorAlt: b, textHalo: x, textHaloAlt: x },
                    satellite: { key: "satellite", display: "Satellite", url: "mapbox://styles/mapbox/satellite-streets-v11", textColor: b, textColorAlt: b, textHalo: x, textHaloAlt: x },
                },
                C = [],
                S = {
                    none: { key: "none", shortDisplay: "None", display: "None", description: "", tiles: "none" },
                    radar: u.overlays.rala,
                    drrf: u.overlays.drrf,
                    "smoke-low": v.overlays.low,
                    "smoke-high": v.overlays.high,
                    snowdepth: j.overlay,
                    temperature: _.overlay,
                },
                E = {},
                L = new Intl.DateTimeFormat("default", { month: "short", day: "numeric", hour: "numeric", minute: "numeric", timeZoneName: "short" });
            function N() {
                r && ((i.center = r.getCenter()), (i.zoom = r.getZoom())),
                    (i.style = o.key),
                    (i.overlay = a.key),
                    (i.pointsVisible = s),
                    "none" != a.key && (i.showNew = !1),
                    window.localStorage.setItem("mapState-" + t.key, JSON.stringify(i));
            }
            function I() {
                var e = window.localStorage.getItem("mapState-" + t.key),
                    r = "dark" == $("html").attr("data-theme") ? P.dark : P.terrain;
                if (e)
                    try {
                        (i = JSON.parse(e)).fromStorage = !0;
                    } catch (e) {}
                void 0 === i.showNew && (i.showNew = !0), (o = P[i.style] || r), (a = S[i.overlay] || S.none), (s = void 0 === i.pointsVisible || i.pointsVisible);
            }
            function M() {
                var e = [];
                function r(r, o, n, a) {
                    "a" !== t.userType && r != t.pointsSource ? e.push({ shortname: r, hasLegend: !0 }) : e.push({ shortname: r, tileTypes: o, tileCount: n, getForecasts: a, hasTileIndex: !0, hasLegend: !0, tileSort: "asc" });
                }
                return (
                    r(t.pointsSource, ["points"], 1, !1),
                    Object.values(S).forEach(function (e) {
                        e.tiles && "none" != e.tiles && r(e.tiles, e.tileTypes, e.tileCount, e.isForecast);
                    }),
                    new Promise(function (t, r) {
                        $.ajax("/api/3.0/maps/sources", {
                            headers: { "X-OpenSummit-Access": "7db12174b64ac1caf4e87237462b5dfe", "content-type": "application/json" },
                            data: { inputs: JSON.stringify({ keyByShortname: !0, sources: e }) },
                            success: function (e) {
                                return t(e);
                            },
                            error: function (e, t, o) {
                                return r(o);
                            },
                        });
                    })
                );
            }
            function F() {
                "a" === t.userType &&
                    $.ajax("/api/3.0/maps/sources?shortname=rala&tileCount=1&hasTileIndex=1&getForecasts=0", {
                        headers: { "X-OpenSummit-Access": "7db12174b64ac1caf4e87237462b5dfe" },
                        success: function (e) {
                            e.forEach(function (e) {
                                var o = Object.values(S).find(function (t) {
                                        return t.tiles == e.shortname;
                                    }),
                                    n = [];
                                (t.sources[e.shortname].is_stale = e.is_stale),
                                    o.tileTypes.forEach(function (r) {
                                        var o = t.sources[e.shortname].tiles[r],
                                            a = e.tiles[r][0];
                                        if (o && a) {
                                            var i = o[o.length - 1].source_timestamp,
                                                s = a.source_timestamp;
                                            i != s && (console.log("new tiles found for ", e.shortname, r, s), o.push(a), n.push(o.shift()));
                                        }
                                    }),
                                    n.length &&
                                        o.frames.length &&
                                        (!(function (e, t) {
                                            if (!e.frames || !e.frames.length) return;
                                            t.forEach(function (t) {
                                                for (var o = 0; o < e.frames.length; o++) {
                                                    for (var n = e.frames[o], a = 0; a < n.sources.length; a++) {
                                                        var i = n.sources[a];
                                                        i.type == t.type &&
                                                            i.timestamp == t.source_timestamp &&
                                                            (i.layers.forEach(function (e) {
                                                                return r.removeLayer(e.id);
                                                            }),
                                                            r.removeSource(i.id),
                                                            n.sources.splice(a, 1),
                                                            a--);
                                                    }
                                                    if (0 == n.sources.length) {
                                                        e.frames.splice(o, 1), o--;
                                                        break;
                                                    }
                                                }
                                            });
                                        })(o, n),
                                        o.add(B(), !0),
                                        a == o && f && !c && (0 == a.idx ? te(0) : a.idx == a.frames.length - 1 ? (Q(a.idx - 1), te(a.idx)) : re()));
                            }),
                                setTimeout(F, 6e4);
                        },
                    });
            }
            function z(t, r) {
                (l = r), $(".card-holder", e).addClass("visible"), $(".forecast-card-holder", e).load("/map/card/" + t + "/" + r), q();
            }
            function R() {
                (l = null), $(".card-holder", e).removeClass("visible"), history.replaceState(null, null, " ");
            }
            function H() {
                void 0 !== a.idx && Q(a.idx),
                    a.frames &&
                        a.frames.forEach(function (e) {
                            e.sources.forEach(function (e) {
                                e.layers.forEach(function (e) {
                                    return r.setLayoutProperty(e.id, "visibility", "none");
                                });
                            });
                        }),
                    $(".legend", e).removeClass("visible"),
                    e.removeClass("legend-visible"),
                    $(".timestamp", e).removeClass("visible"),
                    X(),
                    (f = !1);
            }
            function G(e, t) {
                var r = e || 0.35,
                    o = t || 0.9;
                return [0, o, 6, o, 12, r, 22, r];
            }
            function Z(e) {
                return !e.color_dark || ("dark" != o.key && "satellite" != o.key) ? e.color : e.color_dark;
            }
            function V(e) {
                var t = [];
                return (
                    e.forEach(function (e) {
                        t.push(e.value, Z(e));
                    }),
                    t
                );
            }
            function J(e) {
                var t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 140;
                e = e.slice(1);
                var r = parseInt(e.slice(0, 2), 16),
                    o = parseInt(e.slice(2, 4), 16),
                    n = parseInt(e.slice(4, 6), 16);
                return 0.299 * r + 0.587 * o + 0.114 * n > t ? "#000000" : "#FFFFFF";
            }
            function Y(t) {
                var r = [],
                    o = t.units_abbrev;
                if (("in" != o || y || (o = "cm"), "Â°F" == o && m && (o = "Â°C"), t.groups)) {
                    var n = t.steps.map(function (e) {
                            return Z(e);
                        }),
                        a = 0;
                    t.groups.forEach(function (e) {
                        for (var o, n = 0; a < t.steps.length; a++) {
                            if (t.steps[a].value == e.maxValue) {
                                o = J(Z(t.steps[a - Math.floor(n / 2)]));
                                break;
                            }
                            n++;
                        }
                        r.push('<div style="color: '.concat(o, ';">').concat(e.label, "</div>"));
                    }),
                        $(".legend", e).attr("style", "background: linear-gradient(0.25turn, ".concat(n.join(","), ");"));
                } else
                    t.steps.forEach(function (e, n) {
                        var a = Z(e),
                            i = J(a),
                            s = e.value;
                        "cm" == o ? (s = Math.max(1, 5 * Math.round((2.54 * s) / 5))) : "Â°C" == o && (s = 2 * Math.ceil(((5 / 9) * (s - 32)) / 2)), ("in" != o && "cm" != o) || n != t.steps.length - 1 || (s += "+");
                        t.steps[n + 1] && Z(t.steps[n + 1]);
                        r.push('<div style="background: '.concat(a, "; color: ").concat(i, '">').concat(s, "</div>"));
                    }),
                        r.unshift('<div class="units">'.concat(o, "</div>"));
                $(".legend", e).html(r.join("")).addClass("visible"), e.addClass("legend-visible");
            }
            function B() {
                return {
                    overlay: a,
                    map: r,
                    params: t,
                    style: o,
                    textFont: O,
                    textColor: "hsl(26, 20%, 36%)",
                    textColorAlt: b,
                    textHalo: w,
                    textHaloAlt: x,
                    isMobile: h,
                    isImperial: y,
                    isCelsius: m,
                    drawLegend: Y,
                    updateSlider: W,
                    colorInterpolate: V,
                    opacityInterpolate: G,
                    showMostRecent: ie,
                    setOpacity: function (e) {
                        K = e;
                    },
                    setIsAnimatable: function (e) {
                        f = e;
                    },
                };
            }
            function U() {
                $(".animate-controls").addClass("visible"), e.addClass("animation-controls-visible");
            }
            function X() {
                $(".animate-controls").removeClass("visible"), e.removeClass("animation-controls-visible");
            }
            function W(e) {
                $(".slider input").attr("max", e).attr("value", e).val(a.idx);
            }
            function q() {
                $(".add-layers", e).removeClass("visible"), f && setTimeout(U, 250);
            }
            function K(e, t) {
                console.warn("please override setopacity");
            }
            function Q(e) {
                a.frames &&
                    a.frames[e] &&
                    a.frames[e].sources.forEach(function (e) {
                        e.layers.forEach(function (e) {
                            return K(e, 0);
                        });
                    });
            }
            function ee(o, n) {
                (a.idx = o),
                    a.frames[o].sources.forEach(function (e) {
                        (c && e.hideOnAnimate) ||
                            e.layers.forEach(function (t) {
                                e.moveOnShow && r.moveLayer(t.id, e.moveOnShow), K(t, n), r.setLayoutProperty(t.id, "visibility", "visible");
                            });
                    }),
                    (function (r) {
                        if (!E[r]) {
                            var o = new Date(r.split(" ").join("T") + ".000Z"),
                                n = {};
                            L.formatToParts(o).forEach(function (e) {
                                return (n[e.type] = e.value);
                            });
                            var i = "".concat(n.month, " ").concat(n.day, " ").concat(n.hour, ":").concat(n.minute).concat(n.dayPeriod.toLowerCase(), " ").concat(n.timeZoneName);
                            E[r] = i;
                        }
                        var s = a.isForecast ? "forecast" : "as of";
                        $(".timestamp", e)
                            .html(
                                '<span class="as-of">'
                                    .concat(a.shortDisplay || a.display, " ")
                                    .concat(s, "</span><span>")
                                    .concat(E[r], "</span>")
                            )
                            .addClass("visible")
                            .toggleClass("old", t.sources[a.tiles].is_stale);
                    })(a.frames[o].sources[0].timestamp);
            }
            function te(t) {
                Q(a.idx), void 0 !== t ? (a.idx = t) : (a.idx++, a.idx == a.frames.length && (a.idx = 0)), $(".slider input", e).val(a.idx), ee(a.idx), c && ne(a.idx == a.frames.length - 1 ? 1500 : 500);
            }
            function re() {
                var e = a.idx - 1;
                e < 0 && (e = a.frames.length - 1), te(e);
            }
            (c = !1), (p = null), (f = !1), (s = !0), (l = null), (i = { center: [-97, 40], zoom: 3, style: "terrain", overlay: "none", pointsVisible: !0, showNew: !0 });
            var oe = $('.animate-controls div[data-action="play"] span', e);
            function ne() {
                var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 500;
                oe.html('<i class="fas fa-pause"></i>'), (c = !0), (p = setTimeout(te, e));
            }
            function ae() {
                c && (oe.html('<i class="fas fa-play"></i>'), (c = !1), clearTimeout(p));
            }
            function ie(t) {
                ee(void 0 !== t ? t : a.frames.length - 1), f && !$(".add-layers", e).hasClass("visible") && U();
            }
            function se() {
                $(".points-toggle").html('<i class="fas fa-map-marker-alt-slash"></i>'),
                    C.forEach(function (e) {
                        r.setLayoutProperty(e, "visibility", "none");
                    }),
                    (s = !1);
            }
            function le() {
                var e = t.pointsSource || "opensummit-points-unclustered",
                    n = null;
                if (($(".points-toggle").html('<i class="fas fa-map-marker-alt"></i>'), (s = !0), r.getSource(e)))
                    C.forEach(function (e) {
                        r.setLayoutProperty(e, "visibility", "visible");
                    });
                else {
                    if ("locations" == e) (n = ""), r.addSource(e, { data: t.locations, type: "geojson" });
                    else {
                        var a = t.sources[e];
                        (n = a.tiles.points[0].source_layer_id),
                            r.addSource(
                                e,
                                (function (e) {
                                    for (var t = 1; t < arguments.length; t++) {
                                        var r = null != arguments[t] ? arguments[t] : {};
                                        t % 2
                                            ? D(Object(r), !0).forEach(function (t) {
                                                  T(e, t, r[t]);
                                              })
                                            : Object.getOwnPropertyDescriptors
                                            ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r))
                                            : D(Object(r)).forEach(function (t) {
                                                  Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(r, t));
                                              });
                                    }
                                    return e;
                                })({}, a.tiles.points[0].index_json, { type: "vector" })
                            );
                    }
                    var i = r.getLayer("settlement-label") ? "settlement-label" : "settlement-minor-label",
                        c = "dark" == o.key ? [0, 0.01, 6, 0.25, 8, 1, 11, 2] : [0, 0.25, 6, 0.5, 8, 1, 11, 2];
                    r.addLayer(
                        {
                            id: "single-points",
                            type: "circle",
                            source: e,
                            "source-layer": n,
                            paint: {
                                "circle-opacity": 1,
                                "circle-stroke-color": "#F7F2ED",
                                "circle-radius": ["interpolate", ["linear"], ["zoom"], 0, 1, 6, 2, 8, 3, 11, 5],
                                "circle-color": ["match", ["get", "type"], "trails", "#623048", "points", "#E38064", "#888888"],
                                "circle-stroke-width": ["interpolate", ["linear"], ["zoom"]].concat(c),
                            },
                        },
                        i
                    ),
                        r.addLayer(
                            {
                                id: "point-labels",
                                type: "symbol",
                                source: e,
                                minzoom: "explore" == t.key ? 10 : 2,
                                "source-layer": n,
                                layout: {
                                    "text-size": 13,
                                    "text-field": ["get", "name"],
                                    "text-anchor": "left",
                                    "text-offset": [1, 0],
                                    "text-line-height": 1.1,
                                    "text-justify": "left",
                                    "text-font": O,
                                    "text-allow-overlap": !1,
                                    "text-ignore-placement": !1,
                                },
                                paint: { "text-color": o.textColor, "text-halo-color": o.textHalo, "text-halo-width": 1 },
                            },
                            i
                        ),
                        C.push("single-points", "point-labels"),
                        ["single-points", "point-labels"].forEach(function (e) {
                            r.on("mousedown", e, u);
                        }),
                        ["single-points", "point-labels"].forEach(function (e) {
                            r.on("mouseenter", e, p), r.on("mouseleave", e, f);
                        });
                }
                function u(e) {
                    e.originalEvent.stopPropagation();
                    var t = e.features[0].properties;
                    if (l == t.id) return R();
                    (g = !0), (window.location.hash = t.type + "=" + t.id), z(t.type, t.id);
                }
                function p() {
                    r.getCanvas().style.cursor = "pointer";
                }
                function f() {
                    r.getCanvas().style.cursor = "";
                }
            }
            function ce() {
                s ? le() : se(),
                    "a" == t.userType && a.add && t.sources[a.tiles].tiles[a.tileTypes[0]].length && a.add(B()),
                    y && r.getLayer("contour-label") && r.setLayoutProperty("contour-label", "text-field", ["concat", ["number-format", ["*", ["round", ["/", ["*", 3.28084, ["get", "ele"]], 10]], 10], {}], " ft"]),
                    $(".loading-map").hide();
            }
            function ue(e, t, r, o) {
                var n = "overlay" == e && i.showNew ? '<span class="badge badge-warning badge-sm">New</span>' : "";
                "none" == r && (o = "None (".concat(Object.keys(S).length - 1, " available)")),
                    $(".layer-mini-group-".concat(e)).html(
                        "\n            "
                            .concat(n, '\n            <div class="label">')
                            .concat(t, '</div>\n            <div class="layer-mini layer-')
                            .concat(e, "-")
                            .concat(r, '"></div>\n            <div class="type">')
                            .concat(o, "</div>\n        ")
                    ),
                    "overlay" == e ? $(".layer-mini-group-".concat(e)).attr("title", a.description) : $(".layer-mini-group-".concat(e)).attr("title", "");
            }
            function pe() {
                var r = $(".layer-group.layers-base", e),
                    n = $(".layer-group.layers-overlay", e);
                function i(e, r, o, n, a) {
                    var i = o ? "selected" : "",
                        s = "",
                        l = "",
                        c = "";
                    a ? ((s = "locked"), (l = '<div class="lock"><div class="screen"></div></div>'), (c = '<span class="icon"><i class="fas fa-lock"></i></span>')) : (c = '<span class="icon"><i class="fas fa-lock-open"></i></span>');
                    var u = n ? '<span class="badge badge-allaccess">'.concat(c, '<span class="text">All-Access</span></span>') : "",
                        p = e.isAnimatable ? "<br/><br/><span data-toggle='tooltip' class='icon'><i class='fas fa-play-circle'></i></span> Loopable" : "",
                        f = "",
                        d = "";
                    if ("overlay" == r && "none" !== e.tiles) {
                        var y = t.sources[e.tiles];
                        y.description && ((f = y.description + p), (d = '<span data-toggle="tooltip" data-html="true" title="'.concat(f, '" class="icon"><i class="far fa-question-circle"></i></span>')));
                    }
                    return '\n                <div class="layer-select layer-'
                        .concat(r, " layer-")
                        .concat(r, "-")
                        .concat(e.key, " ")
                        .concat(i, " ")
                        .concat(s, '"\n                    data-')
                        .concat(r, '="')
                        .concat(e.key, '"\n                    >\n                    <div class="layer-label">\n                        <span>')
                        .concat(e.display, '</span>\n                        <div class="icons">')
                        .concat(d, "</div>\n                    </div>\n                    ")
                        .concat(l, "\n                    ")
                        .concat(u, "\n                </div>\n            ");
                }
                Object.keys(P).forEach(function (e) {
                    var n = P[e],
                        a = o === n,
                        s = "satellite" == e,
                        l = s && "a" !== t.userType;
                    r.append(i(n, "base", a, s, l)), a && ue("base", "Base Map", n.key, n.display);
                }),
                    "none" == a.key || ("a" === t.userType && t.sources[a.tiles].tiles[a.tileTypes[0]].length) || (a = S.none),
                    Object.keys(S).forEach(function (e) {
                        var r = S[e],
                            o = a === r,
                            s = "none" !== e,
                            l = s && "a" !== t.userType;
                        n.append(i(r, "overlay", o, s, l)), o && ue("overlay", "Overlay", r.key, r.display);
                    }),
                    $('[data-toggle="tooltip"]', e).tooltip(),
                    $(".layer-select .icons", e).on("click", function (e) {
                        return e.stopPropagation();
                    });
            }
            function fe() {
                var e = "f" == t.userType ? "/user/settings/upgrade" : "/user/register";
                window.location = "".concat(e, "?source=summit_map_layers");
            }
            function de() {
                $(".card-holder", e).on("click", ".card-close", R),
                    $(".controls, .layers-close", e).on("click", function () {
                        $(".add-layers", e).hasClass("visible") ? q() : ($(".add-layers", e).addClass("visible"), ae(), R(), X());
                    }),
                    $("#mapbox", e).on("mousedown", function () {
                        q(), R();
                    }),
                    $(".layers-base .layer-select", e).on("click", function (e) {
                        var t = $(e.currentTarget);
                        t.hasClass("selected") ||
                            (t.hasClass("locked")
                                ? fe()
                                : (t.siblings().removeClass("selected"),
                                  t.addClass("selected"),
                                  (o = P[t.attr("data-base")]),
                                  N(),
                                  ue("base", "Base Map", o.key, o.display),
                                  Object.values(S).forEach(function (e) {
                                      (e.frames = []), (e.idx = 0);
                                  }),
                                  r.once("styledata", ce),
                                  r.setStyle(o.url)));
                    }),
                    $(".layers-overlay .layer-select", e).on("click", function (e) {
                        var t = $(e.currentTarget);
                        if (!t.hasClass("selected")) {
                            if (t.hasClass("locked")) return fe();
                            H(), t.siblings().removeClass("selected"), t.addClass("selected"), (a = S[t.attr("data-overlay")]), N(), ue("overlay", "Overlay", a.key, a.display), a.add && a.add(B());
                        }
                    }),
                    $('.animate-controls div[data-action="back"]', e).on("click", function () {
                        ae(), re();
                    }),
                    $('.animate-controls div[data-action="play"]', e).on("click", function () {
                        R(), c ? ae() : ne();
                    }),
                    $('.animate-controls div[data-action="forward"]', e).on("click", function () {
                        ae(), te();
                    }),
                    $(".animate-controls .slider input", e).on("input", function (e) {
                        var t = e.currentTarget.value;
                        ae(), te(t);
                    }),
                    $(".animate-controls .slider input", e).on("mousedown", function (e) {
                        ae();
                    }),
                    $(window).on("keydown", function (e) {
                        $(".animate-controls").hasClass("visible") &&
                            !$("#header-search").hasClass("searching") &&
                            (37 == e.keyCode ? (e.preventDefault(), ae(), re()) : 39 == e.keyCode ? (e.preventDefault(), ae(), te()) : 32 === e.keyCode && (e.preventDefault(), c ? ae() : ne()));
                    }),
                    $(".points-toggle", e).on("click", function (e) {
                        e.stopPropagation(), s ? se() : le(), N();
                    }),
                    $(".fullscreen-toggle", e).on("click", function (e) {
                        e.stopPropagation(), $("body").toggleClass("map-fullscreen"), $(".fullscreen-toggle svg").toggleClass("fa-expand").toggleClass("fa-compress-wide"), r.resize();
                    });
            }
            function ye() {
                var e = arguments.length > 0 && void 0 !== arguments[0] && arguments[0],
                    t = window.location.hash.substring(1).split("=");
                $.ajax({
                    method: "GET",
                    url: "/map/load/",
                    dataType: "json",
                    data: { type: t[0], id: t[1] },
                    timeout: 600,
                    success: function (o) {
                        o.lon && o.lat && (e ? ((i.center = [o.lon, o.lat]), (i.zoom = 12)) : r.jumpTo({ center: [o.lon, o.lat], zoom: 12 }), z(t[0], t[1]), $("#header-search").val("").blur());
                    },
                    complete: function () {
                        e && me();
                    },
                });
            }
            function me() {
                (r = new mapboxgl.Map({
                    accessToken: "pk.eyJ1IjoiY2xvdWRuaW5ld3giLCJhIjoiY2s5N2M2Y2lkMGEzYzNsbGI3NGljZ252ZCJ9.vXw5Ok1uMKLMCgUPm2CCHA",
                    container: $("#mapbox", e).get(0),
                    style: o.url,
                    center: i.center,
                    zoom: i.zoom,
                    keyboard: !1,
                    touchPitch: !1,
                    attributionControl: !1,
                    fadeDuration: 150,
                    logoPosition: "bottom-right",
                })),
                    k && ((window.map = r), console.log(t)),
                    r.addControl(new mapboxgl.GeolocateControl({ positionOptions: { enableHighAccuracy: !0, timeout: 5e3 }, trackUserLocation: !0, fitBoundsOptions: { maxZoom: 12 } }), "top-right"),
                    r.addControl(new mapboxgl.NavigationControl({ showCompass: !1 }), "top-right"),
                    r.once("styledata", ce),
                    r.on("movestart", function () {
                        c && (ae(), r.once("moveend", ne));
                    }),
                    r.on("moveend", N),
                    r.dragRotate.disable(),
                    r.touchZoomRotate.disableRotation(),
                    t.locations &&
                        t.locations.features.length &&
                        s &&
                        r.on("load", function () {
                            return r.fitBounds(turf.bbox(t.locations), { padding: 100, maxZoom: 10 });
                        });
            }
            function he() {
                return (he = A(
                    n.a.mark(function r() {
                        return n.a.wrap(function (r) {
                            for (;;)
                                switch ((r.prev = r.next)) {
                                    case 0:
                                        return $(".loading-map", e).show(), (r.next = 3), M();
                                    case 3:
                                        if (((t.sources = r.sent), I(), pe(), de(), setTimeout(F, 6e4), !window.location.hash)) {
                                            r.next = 10;
                                            break;
                                        }
                                        return r.abrupt("return", ye(!0));
                                    case 10:
                                        if (!i.fromStorage) {
                                            r.next = 12;
                                            break;
                                        }
                                        return r.abrupt("return", me());
                                    case 12:
                                        $.ajax({
                                            url: "/map/zoom",
                                            dataType: "json",
                                            timeout: 600,
                                            success: function (e) {
                                                e.lon && e.lat && ((i.center = [e.lon, e.lat]), (i.zoom = 10));
                                            },
                                            complete: me,
                                        });
                                    case 13:
                                    case "end":
                                        return r.stop();
                                }
                        }, r);
                    })
                )).apply(this, arguments);
            }
            (window.onhashchange = function () {
                g ? (g = !1) : ye(!1);
            }),
                (function () {
                    he.apply(this, arguments);
                })();
        };
    },
    o0o1: function (e, t, r) {
        e.exports = r("ls82");
    },
    paDV: function (e, t) {},
});
//# sourceMappingURL=map.js.map
