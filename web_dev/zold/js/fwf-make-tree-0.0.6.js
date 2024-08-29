var redIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});
let intimeutc = tinital;
const buffer = 0.5;
var point_list = [],
  file_list = [];
map.doubleClickZoom.disable(), (div2.className = "wx-plot2"), div2.setAttribute("id", "wx_plot2");
var btn_fire2 = document.createElement("BUTTON");
btn_fire2.setAttribute("id", "button"), (btn_fire2.className = "btn_fire2"), (btn_fire2.innerHTML = "Fire Weather"), div2.appendChild(btn_fire2);
var btn_wx2 = document.createElement("BUTTON");
btn_wx2.setAttribute("id", "button"), (btn_wx2.className = "btn_wx2"), (btn_wx2.innerHTML = "Weather"), div2.appendChild(btn_wx2);
var btn_fbp = document.createElement("BUTTON");
btn_fbp.setAttribute("id", "button"), (btn_fbp.className = "btn_fbp"), (btn_fbp.innerHTML = "Fire Behavior"), div2.appendChild(btn_fbp), (div3 = div.cloneNode(!0)), (div3.className = "wx-plot3"), div3.setAttribute("id", "wx_plot3");
var btn_fire3 = document.createElement("BUTTON");
btn_fire3.setAttribute("id", "button"), (btn_fire3.className = "btn_fire3"), (btn_fire3.innerHTML = "Fire Weather"), div3.appendChild(btn_fire3);
var btn_wx3 = document.createElement("BUTTON");
btn_wx3.setAttribute("id", "button"), (btn_wx3.className = "btn_wx3"), (btn_wx3.innerHTML = "Weather"), div3.appendChild(btn_wx3);
var btn_fbp3 = document.createElement("BUTTON");
let fwfclicklocation;
btn_fbp3.setAttribute("id", "button"), (btn_fbp3.className = "btn_fbp3"), (btn_fbp3.innerHTML = "Fire Behavior"), div3.appendChild(btn_fbp3), (fwfclicklocation = new L.marker());
var filedate = tinital.slice(0, 4) + tinital.slice(5, 7) + tinital.slice(8, 10) + tinital.slice(11, 13),
  searchboxControl = createSearchboxControl();
const control = new searchboxControl({
  sidebarTitleText: "Information",
  sidebarMenuItems: {
      Items: [
          { type: "link", name: "Smoke Forecasts", href: "https://firesmoke.ca/", icon: "icon-fire" },
          { type: "link", name: "Weather Forecast Research Team", href: "https://wfrt.eoas.ubc.ca/", icon: "icon-cloudy" },
          { type: "link", name: "Contact Inforamtion", href: "https://firesmoke.ca/contact/", icon: "icon-phone" },
          { type: "link", name: "Documentation", href: "https://cerodell.github.io/fwf-docs/index.html", icon: "icon-git" },
          { type: "link", name: "User Guide", href: "https://www.youtube.com/watch?v=XYlh09mXPbo", icon: "icon-youtube" },
          { type: "link", name: "fwf-daily-d02", href: "fwf-daily-d02-" + filedate + ".nc", download: "fwf-daily-d02", icon: "icon-data" },
          { type: "link", name: "fwf-hourly-d02", href: "fwf-hourly-d02-" + filedate + ".nc", download: "fwf-hourly-d02", icon: "icon-data" },
          { type: "link", name: "fwf-daily-d03", href: "fwf-daily-d03-" + filedate + ".nc", download: "fwf-daily-d03", icon: "icon-data" },
          { type: "link", name: "fwf-hourly-d03", href: "fwf-hourly-d03-" + filedate + ".nc", download: "fwf-hourly-d03s", icon: "icon-data" },
          { type: "link", name: "ReadMe", href: "https://cerodell.github.io/fwf-docs/build/html/view.html#general", icon: "icon-info" },
          {
              type: "text",
              name:
                  "<br> The Fire Weather Forecasts are experimental in that they are produced by a system that is part of an ongoing research project. They are subject to uncertainties in both the weather forecasts and in the empirical formulas used to derive fuel moisture content.",
          },
      ],
  },
});
function makeplotly(e) {
  let t = 13;
  var o = e.target,
      n = o.options.customId,
      i = o.options.customIdx,
      r = o._latlng;
  (btn_fire2.onclick = f),
      (btn_wx2.onclick = function () {
          fetch(n)
              .then(function (e) {
                  return e.json();
              })
              .then(function (e) {
                  var o = i,
                      n = e.XLAT[o],
                      r = e.XLONG[o],
                      f = e.TZONE[o],
                      c = e.FUEL[o],
                      m = ObjectFun.confuels(c),
                      s = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                      u = [s, "UTC", "Geo Local"],
                      h = document.createElement("select");
                  h.setAttribute("id", "mySelect"), (h.className = "time_wx"), div2.appendChild(h);
                  for (var p = 0; p < u.length; p++) {
                      var b = document.createElement("option");
                      b.setAttribute("value", u[p]), (b.text = u[p]), h.appendChild(b);
                  }
                  var g = {},
                      y = (e, t) => e.map((e) => e[t]);
                  for (var x of ((keys = ["dsr", "ffmc", "rh", "isi", "fwi", "temp", "ws", "wdir", "precip", "dc", "dmc", "bui"]), keys)) {
                      var u = JSON.parse(e[x]),
                          u = y(u, o);
                      g[x] = u;
                  }
                  for (g.time = e.Time, g.day = e.Day, local_list2 = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) {
                      d = g.time[p];
                      var v = moment.utc(d).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                          _ = v.slice(0, 16);
                      local_list2.push(_);
                  }
                  for (g.geo_time = local_list2, local_list = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) (a = new Date(g.time[p] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
                  if (
                      ((g.local_time = local_list),
                      (h.onchange = function () {
                          var e = this.value;
                          if ("UTC" == e) F(g.time, UTCTimeMap, intimeutc, UTCTimePlot);
                          else if ("Geo Local" == e) {
                              var t = moment.utc(UTCTimeMap).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  o = t.slice(0, 16),
                                  n = moment.utc(intimeutc).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  i = n.slice(0, 16),
                                  a = moment.utc(UTCTimePlot).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  r = a.slice(0, 16);
                              F(g.geo_time, o, i, r);
                          } else if (e == s) {
                              UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                              var l = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  c = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  m = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                              F(g.local_time, l, c, m);
                          }
                      }),
                      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                  )
                      var M = 320,
                          Y = 400,
                          T = 50,
                          w = 30,
                          D = 60,
                          z = 68,
                          L = 1,
                          C = 6,
                          H = 9,
                          k = 8,
                          U = 8;
                  else
                      var M = 700,
                          Y = 500,
                          T = 60,
                          w = 30,
                          D = 80,
                          z = 100,
                          L = 2,
                          C = 11,
                          H = 11.5,
                          k = 10,
                          U = 14;
                  function F(e, o, i, a) {
                      (N = [
                          (temp = { x: e, y: g.temp, mode: "lines", line: { color: "d62728" }, yaxis: "y5", hoverlabel: { font: { size: t } }, hovertemplate: "<b> Temp </b><br>%{y:.2f} (C)<br><extra></extra>" }),
                          (rh = { x: e, y: g.rh, mode: "lines", line: { color: "1f77b4" }, yaxis: "y4", hoverlabel: { font: { size: t } }, hovertemplate: "<b> RH </b><br>%{y:.2f} (%)<br><extra></extra>" }),
                          (ws = { x: e, y: g.ws, mode: "lines", line: { color: "202020" }, yaxis: "y3", hoverlabel: { font: { size: t } }, hovertemplate: "<b> WSP </b><br>%{y:.2f} (km/hr)<br><extra></extra>" }),
                          (wdir = { x: e, y: g.wdir, mode: "lines", line: { color: "7f7f7f" }, yaxis: "y2", hoverlabel: { font: { size: t } }, hovertemplate: "<b> WDIR </b><br>%{y:.2f} (deg)<br><extra></extra>" }),
                          (precip = { x: e, y: g.precip, mode: "lines", line: { color: "2ca02c" }, yaxis: "y1", hoverlabel: { font: { size: t } }, hovertemplate: "<b> Precip </b><br>%{y:.2f} (mm)<br><extra></extra>" }),
                      ]),
                          (S = {
                              autosize: !1,
                              width: M,
                              height: Y,
                              margin: { l: T, r: w, b: D, t: z, pad: L },
                              title: { text: "UBC Weather Forecast <br>Lat: " + n.toString().slice(0, 6) + ", Lon: " + r.toString().slice(0, 8) + "<br>Fuel Type: " + m.toString(), x: 0.05 },
                              titlefont: { color: "#444444", size: U },
                              showlegend: !1,
                              yaxis5: { domain: [0.8, 0.98], title: { text: "Temp<br>(C)", font: { size: H, color: "d62728" } }, tickfont: { size: k, color: "d62728" } },
                              yaxis4: { domain: [0.6, 0.78], title: { text: "RH<br>(%)", font: { size: H, color: "1f77b4" } }, tickfont: { size: k, color: "1f77b4" } },
                              yaxis3: { domain: [0.4, 0.58], title: { text: "WSP<br>(km/hr)", font: { size: H, color: "202020" } }, tickfont: { size: k, color: "202020" } },
                              yaxis2: { domain: [0.2, 0.38], title: { text: "WDIR<br>(deg)", font: { size: H, color: "7f7f7f" } }, tickfont: { size: k, color: "7f7f7f" }, range: [0, 360], tickvals: [0, 90, 180, 270, 360] },
                              yaxis1: { domain: [0, 0.18], title: { text: "Precip<br>(mm)", font: { size: H, color: "2ca02c" } }, tickfont: { size: k, color: "2ca02c" } },
                              xaxis: { tickfont: { size: C, color: "444444" } },
                              shapes: [
                                  { type: "line", x0: o, y0: 0, x1: o, yref: "paper", y1: 0.98, line: { color: "grey", width: 1.5, dash: "dot" } },
                                  { type: "rect", xref: "x", yref: "paper", x0: i, y0: 0, x1: a, y1: 0.98, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                              ],
                          }),
                          Plotly.newPlot(l, N, S);
                  }
                  UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                  var A = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      O = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      P = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                  F(g.local_time, A, O, P);
              });
      }),
      (btn_fbp.onclick = function () {
          fetch(n)
              .then(function (e) {
                  return e.json();
              })
              .then(function (e) {
                  var o = i,
                      n = e.XLAT[o],
                      r = e.XLONG[o],
                      f = e.TZONE[o],
                      c = e.FUEL[o],
                      m = ObjectFun.confuels(c),
                      s = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                      u = [s, "UTC", "Geo Local"],
                      h = document.createElement("select");
                  h.setAttribute("id", "mySelect"), (h.className = "time_wx"), div2.appendChild(h);
                  for (var p = 0; p < u.length; p++) {
                      var b = document.createElement("option");
                      b.setAttribute("value", u[p]), (b.text = u[p]), h.appendChild(b);
                  }
                  var g = {},
                      y = (e, t) => e.map((e) => e[t]);
                  for (var x of ((keys = ["dsr", "ffmc", "rh", "isi", "fwi", "temp", "ws", "wdir", "precip", "dc", "dmc", "bui", "hfi", "ros", "cfb", "sfc", "tfc"]), keys)) {
                      var u = JSON.parse(e[x]),
                          u = y(u, o);
                      g[x] = u;
                  }
                  for (g.time = e.Time, g.day = e.Day, local_list2 = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) {
                      d = g.time[p];
                      var v = moment.utc(d).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                          _ = v.slice(0, 16);
                      local_list2.push(_);
                  }
                  for (g.geo_time = local_list2, local_list = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) (a = new Date(g.time[p] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
                  if (
                      ((g.local_time = local_list),
                      (h.onchange = function () {
                          var e = this.value;
                          if ("UTC" == e) F(g.time, UTCTimeMap, intimeutc, UTCTimePlot);
                          else if ("Geo Local" == e) {
                              var t = moment.utc(UTCTimeMap).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  o = t.slice(0, 16),
                                  n = moment.utc(intimeutc).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  i = n.slice(0, 16),
                                  a = moment.utc(UTCTimePlot).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  r = a.slice(0, 16);
                              F(g.geo_time, o, i, r);
                          } else if (e == s) {
                              UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                              var l = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  c = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  m = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                              F(g.local_time, l, c, m);
                          }
                      }),
                      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                  )
                      var M = 320,
                          Y = 400,
                          T = 50,
                          w = 30,
                          D = 60,
                          z = 68,
                          L = 1,
                          C = 6,
                          H = 9,
                          k = 8,
                          U = 8;
                  else
                      var M = 700,
                          Y = 500,
                          T = 60,
                          w = 30,
                          D = 80,
                          z = 100,
                          L = 2,
                          C = 11,
                          H = 11.5,
                          k = 10,
                          U = 14;
                  function F(e, o, i, a) {
                      (N = [
                          (temp = { x: e, y: g.hfi, mode: "lines", line: { color: "9e1809" }, yaxis: "y5", hoverlabel: { font: { size: t, color: "ffffff" } }, hovertemplate: "<b> HFI </b><br>%{y:.2f} (kW/m)<br><extra></extra>" }),
                          (rh = { x: e, y: g.ros, mode: "lines", line: { color: "21245b" }, yaxis: "y4", hoverlabel: { font: { size: t, color: "ffffff" } }, hovertemplate: "<b> ROS </b><br>%{y:.2f} (m/min))<br><extra></extra>" }),
                          (ws = { x: e, y: g.cfb, mode: "lines", line: { color: "c99725" }, yaxis: "y3", hoverlabel: { font: { size: t, color: "ffffff" } }, hovertemplate: "<b> CFB </b><br>%{y:.2f} (%)<br><extra></extra>" }),
                          (wdir = {
                              x: e,
                              y: g.sfc,
                              mode: "lines",
                              line: { color: "689783" },
                              yaxis: "y2",
                              hoverlabel: { font: { size: t, color: "ffffff" } },
                              hovertemplate: "<b> SFC </b><br>%{y:.2f} (kg/m<sup>2</sup>)<br><extra></extra>",
                          }),
                          (precip = {
                              x: e,
                              y: g.tfc,
                              mode: "lines",
                              line: { color: "384a39" },
                              yaxis: "y1",
                              hoverlabel: { font: { size: t, color: "ffffff" } },
                              hovertemplate: "<b> TFC </b><br>%{y:.2f} (kg/m<sup>2</sup>)<br><extra></extra>",
                          }),
                      ]),
                          (S = {
                              autosize: !1,
                              width: M,
                              height: Y,
                              margin: { l: T, r: w, b: D, t: z, pad: L },
                              title: { text: "UBC Fire Behavior Forecast <br>Lat: " + n.toString().slice(0, 6) + ", Lon: " + r.toString().slice(0, 8) + "<br>Fuel Type: " + m.toString(), x: 0.05 },
                              titlefont: { color: "#444444", size: U },
                              showlegend: !1,
                              yaxis5: { domain: [0.8, 0.98], title: { text: "HFI<br>(kW/m)", font: { size: H, color: "9e1809" } }, tickfont: { size: k, color: "9e1809" } },
                              yaxis4: { domain: [0.6, 0.78], title: { text: "ROS<br>(m/min)", font: { size: H, color: "21245b" } }, tickfont: { size: k, color: "21245b" } },
                              yaxis3: { domain: [0.4, 0.58], title: { text: "CFB<br>(%)", font: { size: H, color: "c99725" } }, tickfont: { size: k, color: "c99725" } },
                              yaxis2: { domain: [0.2, 0.38], title: { text: "SFC<br>(kg/m<sup>2</sup>)", font: { size: H, color: "689783" } }, tickfont: { size: k, color: "689783" } },
                              yaxis1: { domain: [0, 0.18], title: { text: "TFC<br>(kg/m<sup>2</sup>)", font: { size: H, color: "384a39" } }, tickfont: { size: k, color: "384a39" } },
                              xaxis: { tickfont: { size: C, color: "444444" } },
                              shapes: [
                                  { type: "line", x0: o, y0: 0, x1: o, yref: "paper", y1: 1, line: { color: "grey", width: 1.5, dash: "dot" } },
                                  { type: "rect", xref: "x", yref: "paper", x0: i, y0: 0, x1: a, y1: 1, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                              ],
                          }),
                          Plotly.newPlot(l, N, S);
                  }
                  UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                  var A = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      O = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      P = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                  F(g.local_time, A, O, P);
              });
      });
  r.lat, r.lng;
  var l = document.getElementById("wx_plot2");
  function f() {
      fetch(n)
          .then(function (e) {
              return e.json();
          })
          .then(function (e) {
              var o = i,
                  n = e.XLAT[o],
                  r = e.XLONG[o],
                  f = e.TZONE[o],
                  c = e.FUEL[o],
                  m = ObjectFun.confuels(c),
                  s = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                  u = [s, "UTC", "Geo Local"],
                  h = document.createElement("select");
              h.setAttribute("id", "mySelect"), (h.className = "time_wx"), div2.appendChild(h);
              for (var p = 0; p < u.length; p++) {
                  var b = document.createElement("option");
                  b.setAttribute("value", u[p]), (b.text = u[p]), h.appendChild(b);
              }
              var g = {},
                  y = (e, t) => e.map((e) => e[t]);
              for (var x of ((keys = ["dsr", "ffmc", "rh", "isi", "fwi", "temp", "ws", "wdir", "precip", "dc", "dmc", "bui"]), keys)) {
                  console.log('ERROR');
                  console.log(x);
                  console.log(e[x]);
                  u = y((u = JSON.parse(e[x])), o);
                  console.log(u);
                  g[x] = u;
              }
              for (g.time = e.Time, g.day = e.Day, local_list2 = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) {
                  d = g.time[p] + ":00:00.000Z";
                  var v = moment.utc(d).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16);
                  local_list2.push(v);
              }
              for (g.geo_time = local_list2, local_list = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) (a = new Date(g.time[p] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
              function _(e, o, i, a) {
                  if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                      var f = 320,
                          c = 400,
                          s = 50,
                          d = 30,
                          u = 60,
                          h = 68,
                          p = 1,
                          b = 6,
                          y = 9,
                          x = 8,
                          v = 8,
                          _ = 16,
                          M = 18,
                          Y = 8;
                  else (f = 700), (c = 500), (s = 60), (d = 30), (u = 80), (h = 100), (p = 2), (b = 11), (y = 11.5), (x = 10), (v = 14), (_ = 20), (M = 22), (Y = 12);
                  (T = [
                      ["DMC", "DC", "BUI", "FWI", "DSR"],
                      [g.dmc[0], g.dc[0], g.bui[0], g.fwi[0], g.dsr[0]],
                      [g.dmc[1], g.dc[1], g.bui[1], g.fwi[1], g.dsr[1]],
                  ]),
                      (N =
                          ((ffmc = {
                              x: e,
                              y: g.ffmc,
                              mode: "lines",
                              line: { color: "ff7f0e" },
                              yaxis: "y2",
                              hoverlabel: { font: { size: t, color: "#ffffff" }, bordercolor: "#ffffff" },
                              hovertemplate: "<b> FFMC </b><br>%{y:.2f} <br><extra></extra>",
                          }),
                          (isi = { x: e, y: g.isi, mode: "lines", line: { color: "9467bd" }, yaxis: "y1", hoverlabel: { font: { size: t } }, hovertemplate: "<b> ISI </b><br>%{y:.2f} <br><extra></extra>" }),
                          [
                              {
                                  type: "table",
                                  header: { values: [["Index/Code"], [g.day[0]], [g.day[1]]], align: "center", height: _, line: { color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: Y, color: "white" } },
                                  cells: {
                                      values: T,
                                      align: "center",
                                      height: M,
                                      line: { color: "444444", width: 1 },
                                      fill: { color: [["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] },
                                      font: { family: "inherit", size: 11, color: [["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]] },
                                  },
                                  xaxis: "x",
                                  yaxis: "y",
                                  domain: { x: [0, 1], y: [0.54, 1] },
                              },
                              ffmc,
                              isi,
                          ])),
                      (S = {
                          autosize: !1,
                          width: f,
                          height: c,
                          margin: { l: s, r: d, b: u, t: h, pad: p },
                          title: { text: "UBC Fire Weather Forecast <br>Lat: " + n.toString().slice(0, 6) + ", Lon: " + r.toString().slice(0, 8) + "<br>Fuel Type: " + m.toString(), x: 0.05 },
                          titlefont: { color: "#444444", size: v },
                          showlegend: !1,
                          yaxis2: { domain: [0.27, 0.54], title: { text: "FFMC", font: { size: y, color: "ff7f0e" } }, tickfont: { size: x, color: "ff7f0e" } },
                          yaxis1: { domain: [0, 0.26], title: { text: "ISI", font: { size: y, color: "9467bd" } }, tickfont: { size: x, color: "9467bd" } },
                          xaxis: { tickfont: { size: b, color: "444444" } },
                          shapes: [
                              { type: "line", x0: o, y0: 0, x1: o, yref: "paper", y1: 0.54, line: { color: "grey", width: 1.5, dash: "dot" } },
                              { type: "rect", xref: "x", yref: "paper", x0: i, y0: 0, x1: a, y1: 0.54, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                          ],
                      }),
                      Plotly.newPlot(l, N, S);
              }
              (g.local_time = local_list),
                  (h.onchange = function () {
                      var e = this.value;
                      if ("UTC" == e) _(g.time, UTCTimeMap, intimeutc, UTCTimePlot);
                      else if ("Geo Local" == e) {
                          var t = moment.utc(UTCTimeMap).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16),
                              o = moment.utc(intimeutc).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16),
                              n = moment.utc(UTCTimePlot).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16);
                          _(g.geo_time, t, o, n);
                      } else if (e == s) {
                          UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                          var i = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                              a = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                              r = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                          _(g.local_time, i, a, r);
                      }
                  }),
                  UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
              var M = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                  Y = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                  w = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
              _(g.local_time, M, Y, w);
          });
  }
  f();
}
function makeplotly3(e) {
  let t = 13;
  var o = e.customId,
      n = e.customIdx;
  (btn_fire3.onclick = r),
      (btn_wx3.onclick = function () {
          fetch(o)
              .then(function (e) {
                  return e.json();
              })
              .then(function (e) {
                  var o = n,
                      r = e.XLAT[o],
                      l = e.XLONG[o],
                      f = e.TZONE[o],
                      c = e.FUEL[o],
                      m = ObjectFun.confuels(c),
                      s = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                      u = [s, "UTC", "Geo Local"],
                      h = document.createElement("select");
                  h.setAttribute("id", "mySelect"), (h.className = "time_wx"), div3.appendChild(h);
                  for (var p = 0; p < u.length; p++) {
                      var b = document.createElement("option");
                      b.setAttribute("value", u[p]), (b.text = u[p]), h.appendChild(b);
                  }
                  var g = {},
                      y = (e, t) => e.map((e) => e[t]);
                  for (var x of ((keys = ["dsr", "ffmc", "rh", "isi", "fwi", "temp", "ws", "wdir", "precip", "dc", "dmc", "bui"]), keys)) {
                      var u = JSON.parse(e[x]),
                          u = y(u, o);
                      g[x] = u;
                  }
                  for (g.time = e.Time, g.day = e.Day, local_list2 = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) {
                      d = g.time[p];
                      var v = moment.utc(d).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                          _ = v.slice(0, 16);
                      local_list2.push(_);
                  }
                  for (g.geo_time = local_list2, local_list = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) (a = new Date(g.time[p] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
                  if (
                      ((g.local_time = local_list),
                      (h.onchange = function () {
                          var e = this.value;
                          if ("UTC" == e) F(g.time, UTCTimeMap, intimeutc, UTCTimePlot);
                          else if ("Geo Local" == e) {
                              var t = moment.utc(UTCTimeMap).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  o = t.slice(0, 16),
                                  n = moment.utc(intimeutc).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  i = n.slice(0, 16),
                                  a = moment.utc(UTCTimePlot).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  r = a.slice(0, 16);
                              F(g.geo_time, o, i, r);
                          } else if (e == s) {
                              UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                              var l = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  c = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  m = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                              F(g.local_time, l, c, m);
                          }
                      }),
                      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                  )
                      var M = 320,
                          Y = 400,
                          T = 50,
                          w = 30,
                          D = 60,
                          z = 68,
                          L = 1,
                          C = 6,
                          H = 9,
                          k = 8,
                          U = 8;
                  else
                      var M = 700,
                          Y = 500,
                          T = 60,
                          w = 30,
                          D = 80,
                          z = 100,
                          L = 2,
                          C = 11,
                          H = 11.5,
                          k = 10,
                          U = 14;
                  function F(e, o, n, a) {
                      (N = [
                          (temp = { x: e, y: g.temp, mode: "lines", line: { color: "d62728" }, yaxis: "y5", hoverlabel: { font: { size: t } }, hovertemplate: "<b> Temp </b><br>%{y:.2f} (C)<br><extra></extra>" }),
                          (rh = { x: e, y: g.rh, mode: "lines", line: { color: "1f77b4" }, yaxis: "y4", hoverlabel: { font: { size: t } }, hovertemplate: "<b> RH </b><br>%{y:.2f} (%)<br><extra></extra>" }),
                          (ws = { x: e, y: g.ws, mode: "lines", line: { color: "202020" }, yaxis: "y3", hoverlabel: { font: { size: t } }, hovertemplate: "<b> WSP </b><br>%{y:.2f} (km/hr)<br><extra></extra>" }),
                          (wdir = { x: e, y: g.wdir, mode: "lines", line: { color: "7f7f7f" }, yaxis: "y2", hoverlabel: { font: { size: t } }, hovertemplate: "<b> WDIR </b><br>%{y:.2f} (deg)<br><extra></extra>" }),
                          (precip = { x: e, y: g.precip, mode: "lines", line: { color: "2ca02c" }, yaxis: "y1", hoverlabel: { font: { size: t } }, hovertemplate: "<b> Precip </b><br>%{y:.2f} (mm)<br><extra></extra>" }),
                      ]),
                          (S = {
                              autosize: !1,
                              width: M,
                              height: Y,
                              margin: { l: T, r: w, b: D, t: z, pad: L },
                              title: { text: "UBC Weather Forecast <br>Lat: " + r.toString().slice(0, 6) + ", Lon: " + l.toString().slice(0, 8) + "<br>Fuel Type: " + m.toString(), x: 0.05 },
                              titlefont: { color: "#444444", size: U },
                              showlegend: !1,
                              yaxis5: { domain: [0.8, 0.98], title: { text: "Temp<br>(C)", font: { size: H, color: "d62728" } }, tickfont: { size: k, color: "d62728" } },
                              yaxis4: { domain: [0.6, 0.78], title: { text: "RH<br>(%)", font: { size: H, color: "1f77b4" } }, tickfont: { size: k, color: "1f77b4" } },
                              yaxis3: { domain: [0.4, 0.58], title: { text: "WSP<br>(km/hr)", font: { size: H, color: "202020" } }, tickfont: { size: k, color: "202020" } },
                              yaxis2: { domain: [0.2, 0.38], title: { text: "WDIR<br>(deg)", font: { size: H, color: "7f7f7f" } }, tickfont: { size: k, color: "7f7f7f" }, range: [0, 360], tickvals: [0, 90, 180, 270, 360] },
                              yaxis1: { domain: [0, 0.18], title: { text: "Precip<br>(mm)", font: { size: H, color: "2ca02c" } }, tickfont: { size: k, color: "2ca02c" } },
                              xaxis: { tickfont: { size: C, color: "444444" } },
                              shapes: [
                                  { type: "line", x0: o, y0: 0, x1: o, yref: "paper", y1: 0.98, line: { color: "grey", width: 1.5, dash: "dot" } },
                                  { type: "rect", xref: "x", yref: "paper", x0: n, y0: 0, x1: a, y1: 0.98, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                              ],
                          }),
                          Plotly.newPlot(i, N, S);
                  }
                  UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                  var A = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      O = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      P = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                  F(g.local_time, A, O, P);
              });
      }),
      (btn_fbp3.onclick = function () {
          fetch(o)
              .then(function (e) {
                  return e.json();
              })
              .then(function (e) {
                  var o = n,
                      r = e.XLAT[o],
                      l = e.XLONG[o],
                      f = e.TZONE[o],
                      c = e.FUEL[o],
                      m = ObjectFun.confuels(c),
                      s = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                      u = [s, "UTC", "Geo Local"],
                      h = document.createElement("select");
                  h.setAttribute("id", "mySelect"), (h.className = "time_wx"), div3.appendChild(h);
                  for (var p = 0; p < u.length; p++) {
                      var b = document.createElement("option");
                      b.setAttribute("value", u[p]), (b.text = u[p]), h.appendChild(b);
                  }
                  var g = {},
                      y = (e, t) => e.map((e) => e[t]);
                  for (var x of ((keys = ["dsr", "ffmc", "rh", "isi", "fwi", "temp", "ws", "wdir", "precip", "dc", "dmc", "bui", "hfi", "ros", "cfb", "sfc", "tfc"]), keys)) {
                      var u = JSON.parse(e[x]),
                          u = y(u, o);
                      g[x] = u;
                  }
                  for (g.time = e.Time, g.day = e.Day, local_list2 = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) {
                      d = g.time[p];
                      var v = moment.utc(d).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                          _ = v.slice(0, 16);
                      local_list2.push(_);
                  }
                  for (g.geo_time = local_list2, local_list = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) (a = new Date(g.time[p] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
                  if (
                      ((g.local_time = local_list),
                      (h.onchange = function () {
                          var e = this.value;
                          if ("UTC" == e) F(g.time, UTCTimeMap, intimeutc, UTCTimePlot);
                          else if ("Geo Local" == e) {
                              var t = moment.utc(UTCTimeMap).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  o = t.slice(0, 16),
                                  n = moment.utc(intimeutc).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  i = n.slice(0, 16),
                                  a = moment.utc(UTCTimePlot).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z"),
                                  r = a.slice(0, 16);
                              F(g.geo_time, o, i, r);
                          } else if (e == s) {
                              UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                              var l = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  c = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                  m = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                              F(g.local_time, l, c, m);
                          }
                      }),
                      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                  )
                      var M = 320,
                          Y = 400,
                          T = 50,
                          w = 30,
                          D = 60,
                          z = 68,
                          L = 1,
                          C = 6,
                          H = 9,
                          k = 8,
                          U = 8;
                  else
                      var M = 700,
                          Y = 500,
                          T = 60,
                          w = 30,
                          D = 80,
                          z = 100,
                          L = 2,
                          C = 11,
                          H = 11.5,
                          k = 10,
                          U = 14;
                  function F(e, o, n, a) {
                      (N = [
                          (temp = { x: e, y: g.hfi, mode: "lines", line: { color: "9e1809" }, yaxis: "y5", hoverlabel: { font: { size: t, color: "ffffff" } }, hovertemplate: "<b> HFI </b><br>%{y:.2f} (kW/m)<br><extra></extra>" }),
                          (rh = { x: e, y: g.ros, mode: "lines", line: { color: "21245b" }, yaxis: "y4", hoverlabel: { font: { size: t, color: "ffffff" } }, hovertemplate: "<b> ROS </b><br>%{y:.2f} (m/min))<br><extra></extra>" }),
                          (ws = { x: e, y: g.cfb, mode: "lines", line: { color: "c99725" }, yaxis: "y3", hoverlabel: { font: { size: t, color: "ffffff" } }, hovertemplate: "<b> CFB </b><br>%{y:.2f} (%)<br><extra></extra>" }),
                          (wdir = {
                              x: e,
                              y: g.sfc,
                              mode: "lines",
                              line: { color: "689783" },
                              yaxis: "y2",
                              hoverlabel: { font: { size: t, color: "ffffff" } },
                              hovertemplate: "<b> SFC </b><br>%{y:.2f} (kg/m<sup>2</sup>)<br><extra></extra>",
                          }),
                          (precip = {
                              x: e,
                              y: g.tfc,
                              mode: "lines",
                              line: { color: "384a39" },
                              yaxis: "y1",
                              hoverlabel: { font: { size: t, color: "ffffff" } },
                              hovertemplate: "<b> TFC </b><br>%{y:.2f} (kg/m<sup>2</sup>)<br><extra></extra>",
                          }),
                      ]),
                          (S = {
                              autosize: !1,
                              width: M,
                              height: Y,
                              margin: { l: T, r: w, b: D, t: z, pad: L },
                              title: { text: "UBC Fire Behavior Forecast <br>Lat: " + r.toString().slice(0, 6) + ", Lon: " + l.toString().slice(0, 8) + "<br>Fuel Type: " + m.toString(), x: 0.05 },
                              titlefont: { color: "#444444", size: U },
                              showlegend: !1,
                              yaxis5: { domain: [0.8, 0.98], title: { text: "HFI<br>(kW/m)", font: { size: H, color: "9e1809" } }, tickfont: { size: k, color: "9e1809" } },
                              yaxis4: { domain: [0.6, 0.78], title: { text: "ROS<br>(m/min)", font: { size: H, color: "21245b" } }, tickfont: { size: k, color: "21245b" } },
                              yaxis3: { domain: [0.4, 0.58], title: { text: "CFB<br>(%)", font: { size: H, color: "c99725" } }, tickfont: { size: k, color: "c99725" } },
                              yaxis2: { domain: [0.2, 0.38], title: { text: "SFC<br>(kg/m<sup>2</sup>)", font: { size: H, color: "689783" } }, tickfont: { size: k, color: "689783" } },
                              yaxis1: { domain: [0, 0.18], title: { text: "TFC<br>(kg/m<sup>2</sup>)", font: { size: H, color: "384a39" } }, tickfont: { size: k, color: "384a39" } },
                              xaxis: { tickfont: { size: C, color: "444444" } },
                              shapes: [
                                  { type: "line", x0: o, y0: 0, x1: o, yref: "paper", y1: 1, line: { color: "grey", width: 1.5, dash: "dot" } },
                                  { type: "rect", xref: "x", yref: "paper", x0: n, y0: 0, x1: a, y1: 1, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                              ],
                          }),
                          Plotly.newPlot(i, N, S);
                  }
                  UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                  var A = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      O = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                      P = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                  F(g.local_time, A, O, P);
              });
      });
  e.lat, e.lng;
  var i = document.getElementById("wx_plot3");
  function r() {
      fetch(o)
          .then(function (e) {
              return e.json();
          })
          .then(function (e) {
              var o = n,
                  r = e.XLAT[o],
                  l = e.XLONG[o],
                  f = e.TZONE[o],
                  c = e.FUEL[o],
                  m = ObjectFun.confuels(c),
                  s = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                  u = [s, "UTC", "Geo Local"],
                  h = document.createElement("select");
              h.setAttribute("id", "mySelect"), (h.className = "time_wx"), div3.appendChild(h);
              for (var p = 0; p < u.length; p++) {
                  var b = document.createElement("option");
                  b.setAttribute("value", u[p]), (b.text = u[p]), h.appendChild(b);
              }
              var g = {},
                  y = (e, t) => e.map((e) => e[t]);
              for (var x of ((keys = ["dsr", "ffmc", "rh", "isi", "fwi", "temp", "ws", "wdir", "precip", "dc", "dmc", "bui"]), keys)) {
                  u = y((u = JSON.parse(e[x])), o);
                  g[x] = u;
              }
              for (g.time = e.Time, g.day = e.Day, local_list2 = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) {
                  d = g.time[p] + ":00:00.000Z";
                  var v = moment.utc(d).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16);
                  local_list2.push(v);
              }
              for (g.geo_time = local_list2, local_list = [], arrayLength = g.time.length, p = 0; p < arrayLength; p++) (a = new Date(g.time[p] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
              function _(e, o, n, a) {
                  if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                      var f = 320,
                          c = 400,
                          s = 50,
                          d = 30,
                          u = 60,
                          h = 68,
                          p = 1,
                          b = 6,
                          y = 9,
                          x = 8,
                          v = 8,
                          _ = 16,
                          M = 18,
                          Y = 8;
                  else (f = 700), (c = 500), (s = 60), (d = 30), (u = 80), (h = 100), (p = 2), (b = 11), (y = 11.5), (x = 10), (v = 14), (_ = 20), (M = 22), (Y = 12);
                  (T = [
                      ["DMC", "DC", "BUI", "FWI", "DSR"],
                      [g.dmc[0], g.dc[0], g.bui[0], g.fwi[0], g.dsr[0]],
                      [g.dmc[1], g.dc[1], g.bui[1], g.fwi[1], g.dsr[1]],
                  ]),
                      (N =
                          ((ffmc = {
                              x: e,
                              y: g.ffmc,
                              mode: "lines",
                              line: { color: "ff7f0e" },
                              yaxis: "y2",
                              hoverlabel: { font: { size: t, color: "#ffffff" }, bordercolor: "#ffffff" },
                              hovertemplate: "<b> FFMC </b><br>%{y:.2f} <br><extra></extra>",
                          }),
                          (isi = { x: e, y: g.isi, mode: "lines", line: { color: "9467bd" }, yaxis: "y1", hoverlabel: { font: { size: t } }, hovertemplate: "<b> ISI </b><br>%{y:.2f} <br><extra></extra>" }),
                          [
                              {
                                  type: "table",
                                  header: { values: [["Index/Code"], [g.day[0]], [g.day[1]]], align: "center", height: _, line: { color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: Y, color: "white" } },
                                  cells: {
                                      values: T,
                                      align: "center",
                                      height: M,
                                      line: { color: "444444", width: 1 },
                                      fill: { color: [["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] },
                                      font: { family: "inherit", size: 11, color: [["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]] },
                                  },
                                  xaxis: "x",
                                  yaxis: "y",
                                  domain: { x: [0, 1], y: [0.54, 1] },
                              },
                              ffmc,
                              isi,
                          ])),
                      (S = {
                          autosize: !1,
                          width: f,
                          height: c,
                          margin: { l: s, r: d, b: u, t: h, pad: p },
                          title: { text: "UBC Fire Weather Forecast <br>Lat: " + r.toString().slice(0, 6) + ", Lon: " + l.toString().slice(0, 8) + "<br>Fuel Type: " + m.toString(), x: 0.05 },
                          titlefont: { color: "#444444", size: v },
                          showlegend: !1,
                          yaxis2: { domain: [0.27, 0.54], title: { text: "FFMC", font: { size: y, color: "ff7f0e" } }, tickfont: { size: x, color: "ff7f0e" } },
                          yaxis1: { domain: [0, 0.26], title: { text: "ISI", font: { size: y, color: "9467bd" } }, tickfont: { size: x, color: "9467bd" } },
                          xaxis: { tickfont: { size: b, color: "444444" } },
                          shapes: [
                              { type: "line", x0: o, y0: 0, x1: o, yref: "paper", y1: 0.54, line: { color: "grey", width: 1.5, dash: "dot" } },
                              { type: "rect", xref: "x", yref: "paper", x0: n, y0: 0, x1: a, y1: 0.54, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                          ],
                      }),
                      Plotly.newPlot(i, N, S);
              }
              (g.local_time = local_list),
                  (h.onchange = function () {
                      var e = this.value;
                      if ("UTC" == e) _(g.time, UTCTimeMap, intimeutc, UTCTimePlot);
                      else if ("Geo Local" == e) {
                          var t = moment.utc(UTCTimeMap).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16),
                              o = moment.utc(intimeutc).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16),
                              n = moment.utc(UTCTimePlot).subtract({ hours: f }).format("YYYY-MM-DD HH:mm z").slice(0, 16);
                          _(g.geo_time, t, o, n);
                      } else if (e == s) {
                          UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                          var i = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                              a = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                              r = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                          _(g.local_time, i, a, r);
                      }
                  }),
                  UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
              var M = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                  Y = moment(new Date(intimeutc).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                  w = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
              _(g.local_time, M, Y, w);
          });
  }
  r();
}
var fwfmodellocation;
function makeplots(e) {
  (json_dir = "/static/json/fwf-zone-merge.json"),
      fetch(json_dir, { cache: "default" })
          .then(function (e) {
              return e.json();
          })
          .then(function (t) {
              for (var o = t.ZONE_d02, n = t.XLAT_d02, i = t.XLONG_d02, a = [], r = [], l = [(l = [n.length, n[0].length])[1], l[0]], c = 0; c < n.length; c++) a = a.concat(n[c]);
              for (c = 0; c < i.length; c++) r = r.concat(i[c]);
              (a = a.map(Number)), (r = r.map(Number));
              var m = a.map(function (e, t) {
                  return [e, r[t]];
              });
              const s = new KDBush(m);
              for (var d = t.ZONE_d03, u = t.XLAT_d03, h = t.XLONG_d03, p = [], b = [], g = [(g = [u.length, u[0].length])[1], g[0]], y = 0; y < u.length; y++) p = p.concat(u[y]);
              for (y = 0; y < h.length; y++) b = b.concat(h[y]);
              (p = p.map(Number)), (b = b.map(Number));
              var x = p.map(function (e, t) {
                  return [e, b[t]];
              });
              const v = new KDBush(x);
              if (((loaded_zones = ["he"]), (loaded_zones_d3 = ["he"]), /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))) var _ = "dblclick";
              else _ = "dblclick";
              map.on(_, function (t) {
                  null != fwfmodellocation && fwfmodellocation.remove(map), null != fwfclicklocation && fwfclicklocation.remove(map), fwfclicklocation.setLatLng(t.latlng).addTo(map);
                  var n = [parseFloat(t.latlng.lat.toFixed(4)), parseFloat(t.latlng.lng.toFixed(4))],
                      i = s.range(n[0] - buffer, n[1] - buffer, n[0] + buffer, n[1] + buffer).map((e) => m[e]);
                  (ll_diff = []),
                      (function (e, t) {
                          for (var o = 0; o < e.length; o++) {
                              var n = Math.abs(e[o][0] - t[0]) + Math.abs(e[o][1] - t[1]);
                              ll_diff.push(n);
                          }
                      })(i, n);
                  for (var a = 0, r = ll_diff[0], c = 1; c < ll_diff.length; c++) ll_diff[c] < r && ((r = ll_diff[c]), (a = c));
                  var u,
                      h,
                      p = s.range(n[0] - buffer, n[1] - buffer, n[0] + buffer, n[1] + buffer);
                  f =
                      ((h = (u = l).reduce(
                          function (e, t) {
                              return e.concat(e[e.length - 1] * t);
                          },
                          [1]
                      )),
                      function (e) {
                          return (
                              (t = e),
                              (o = h),
                              u.map(function (e, n) {
                                  return Math.round(t / o[n]) % e;
                              })
                          );
                          var t, o;
                      });
                  var b = (function (e, t) {
                          var o = e.reduce(
                              function (e, t) {
                                  return e.concat(e[e.length - 1] * t);
                              },
                              [1]
                          );
                          return e.map(function (e, n) {
                              return Math.round(t / o[n]) % e;
                          });
                      })(l, p[a], f(p[a])),
                      y = b[1],
                      _ = b[0],
                      M = o[y][_];
                  if ("d3" == M) {
                      var Y = [parseFloat(t.latlng.lat.toFixed(4)), parseFloat(t.latlng.lng.toFixed(4))],
                          T = v.range(Y[0] - buffer, Y[1] - buffer, Y[0] + buffer, Y[1] + buffer).map((e) => x[e]);
                      (ll_diff2 = []),
                          (function (e, t) {
                              for (var o = 0; o < e.length; o++) {
                                  var n = Math.abs(e[o][0] - t[0]) + Math.abs(e[o][1] - t[1]);
                                  ll_diff2.push(n);
                              }
                          })(T, Y);
                      for (var w = 0, D = ll_diff2[0], z = 1; z < ll_diff2.length; z++) ll_diff2[z] < D && ((D = ll_diff2[z]), (w = z));
                      var C,
                          H = v.range(Y[0] - buffer, Y[1] - buffer, Y[0] + buffer, Y[1] + buffer);
                      ff =
                          ((C = g).reduce(
                              function (e, t) {
                                  return e.concat(e[e.length - 1] * t);
                              },
                              [1]
                          ),
                          function (i) {
                              return C.map(function (i, a) {
                                  return Math.round(t / o[n]) % e;
                              });
                          });
                      var k = (function (e, t) {
                              var o = e.reduce(
                                  function (e, t) {
                                      return e.concat(e[e.length - 1] * t);
                                  },
                                  [1]
                              );
                              return e.map(function (e, n) {
                                  return Math.round(t / o[n]) % e;
                              });
                          })(g, H[w], ff(H[w])),
                          S = k[1],
                          U = k[0];
                      oo = Y;
                      var F = d[S][U];
                      (zone_json_d3 = e.slice(0, 14)),
                          (zone_json_d3 = zone_json_d3 + F + e.slice(16, 36)),
                          fetch(zone_json_d3)
                              .then(function (e) {
                                  return e.json();
                              })
                              .then(function (e) {
                                  for (var t = e.XLAT, o = e.XLONG, n = [], i = [], a = [(a = [t.length, t[0].length])[1], a[0]], r = 0; r < t.length; r++) n = n.concat(t[r]);
                                  for (r = 0; r < o.length; r++) i = i.concat(o[r]);
                                  var l = t.map(function (e, t) {
                                          return [e, o[t]];
                                      }),
                                      f = new KDBush(l);
                                  point_list.push(oo), file_list.push(e);
                                  var c = f.range(oo[0] - 0.2, oo[1] - 0.2, oo[0] + 0.2, oo[1] + 0.2).map((e) => l[e]);
                                  (ll_diff = []),
                                      (function (e, t) {
                                          for (var o = 0; o < e.length; o++) {
                                              var n = Math.abs(parseFloat(e[o][0]) - t[0]) + Math.abs(parseFloat(e[o][1]) - t[1]);
                                              ll_diff.push(n);
                                          }
                                      })(c, oo);
                                  var m = ll_diff.indexOf(Math.min(...ll_diff)),
                                      s = ((m = f.range(oo[0] - 0.2, oo[1] - 0.2, oo[0] + 0.2, oo[1] + 0.2)[m]), e.XLAT[m]),
                                      d = e.XLONG[m];
                                  (fwfmodellocation = new L.marker([s, d], { icon: redIcon, customId: zone_json_d3, customIdx: m })).bindPopup(div2, { maxWidth: "auto", maxHeight: "auto" }),
                                      fwfmodellocation.setZIndexOffset(1e3),
                                      fwfmodellocation.on("click", makeplotly).addTo(map);
                              }),
                          loaded_zones_d3.push(F);
                  } else
                      (t = n),
                          (zone_json = e.slice(0, 14)),
                          (zone_json = zone_json + M + e.slice(16, 30) + "2.json"),
                          fetch(zone_json)
                              .then(function (e) {
                                  return e.json();
                              })
                              .then(function (e) {
                                  for (var o = e.XLAT, n = e.XLONG, i = [], a = [], r = [(r = [o.length, o[0].length])[1], r[0]], l = 0; l < o.length; l++) i = i.concat(o[l]);
                                  for (l = 0; l < n.length; l++) a = a.concat(n[l]);
                                  var f = o.map(function (e, t) {
                                          return [e, n[t]];
                                      }),
                                      c = new KDBush(f);
                                  point_list.push(t), file_list.push(e);
                                  var m = c.range(t[0] - 0.2, t[1] - 0.2, t[0] + 0.2, t[1] + 0.2).map((e) => f[e]);
                                  (ll_diff = []),
                                      (function (e, t) {
                                          for (var o = 0; o < e.length; o++) {
                                              var n = Math.abs(parseFloat(e[o][0]) - t[0]) + Math.abs(parseFloat(e[o][1]) - t[1]);
                                              ll_diff.push(n);
                                          }
                                      })(m, t);
                                  var s = ll_diff.indexOf(Math.min(...ll_diff)),
                                      d = ((s = c.range(t[0] - 0.2, t[1] - 0.2, t[0] + 0.2, t[1] + 0.2)[s]), e.XLAT[s]),
                                      u = e.XLONG[s];
                                  (fwfmodellocation = new L.marker([d, u], { icon: redIcon, customId: zone_json, customIdx: s })).bindPopup(div2, { maxWidth: "auto", maxHeight: "auto" }),
                                      fwfmodellocation.setZIndexOffset(1e3),
                                      fwfmodellocation.on("click", makeplotly).addTo(map);
                              }),
                          loaded_zones.push(M);
              });
              const M = omnivore.kml("data/fire_locations.kml");
              var Y = L.icon({ iconUrl: "static/img/fwf-fire3.png", shadowUrl: "", iconSize: [16, 21], shadowSize: [], iconAnchor: [8, 18], shadowAnchor: [], popupAnchor: [0, -22] });
              function T(n) {
                  var i = n.target;
                  (lat = i._latlng.lat), (lng = i._latlng.lng);
                  n = [parseFloat(i._latlng.lat.toFixed(4)), parseFloat(i._latlng.lng.toFixed(4))];
                  var a = s.range(n[0] - buffer, n[1] - buffer, n[0] + buffer, n[1] + buffer).map((e) => m[e]);
                  (void 0 !== a && 0 != a.length) || map.closePopup(),
                      (ll_diff = []),
                      (function (e, t) {
                          for (var o = 0; o < e.length; o++) {
                              var n = Math.abs(e[o][0] - t[0]) + Math.abs(e[o][1] - t[1]);
                              ll_diff.push(n);
                          }
                      })(a, n);
                  for (var r = 0, c = ll_diff[0], u = 1; u < ll_diff.length; u++) ll_diff[u] < c && ((c = ll_diff[u]), (r = u));
                  var h,
                      p,
                      b = s.range(n[0] - buffer, n[1] - buffer, n[0] + buffer, n[1] + buffer);
                  f =
                      ((p = (h = l).reduce(
                          function (e, t) {
                              return e.concat(e[e.length - 1] * t);
                          },
                          [1]
                      )),
                      function (e) {
                          return (
                              (t = e),
                              (o = p),
                              h.map(function (e, n) {
                                  return Math.round(t / o[n]) % e;
                              })
                          );
                          var t, o;
                      });
                  var y = (function (e, t) {
                          var o = e.reduce(
                              function (e, t) {
                                  return e.concat(e[e.length - 1] * t);
                              },
                              [1]
                          );
                          return e.map(function (e, n) {
                              return Math.round(t / o[n]) % e;
                          });
                      })(l, b[r], f(b[r])),
                      _ = y[1],
                      M = y[0],
                      Y = o[_][M];
                  if ("d3" == Y) {
                      var T = [parseFloat(i._latlng.lat.toFixed(4)), parseFloat(i._latlng.lng.toFixed(4))],
                          w = v.range(T[0] - buffer, T[1] - buffer, T[0] + buffer, T[1] + buffer).map((e) => x[e]);
                      (ll_diff2 = []),
                          (function (e, t) {
                              for (var o = 0; o < e.length; o++) {
                                  var n = Math.abs(e[o][0] - t[0]) + Math.abs(e[o][1] - t[1]);
                                  ll_diff2.push(n);
                              }
                          })(w, T);
                      for (var D = 0, z = ll_diff2[0], L = 1; L < ll_diff2.length; L++) ll_diff2[L] < z && ((z = ll_diff2[L]), (D = L));
                      var C,
                          H = v.range(T[0] - buffer, T[1] - buffer, T[0] + buffer, T[1] + buffer);
                      ff =
                          ((C = g).reduce(
                              function (e, t) {
                                  return e.concat(e[e.length - 1] * t);
                              },
                              [1]
                          ),
                          function (i) {
                              return C.map(function (i, a) {
                                  return Math.round(t / o[n]) % e;
                              });
                          });
                      var k = (function (e, t) {
                              var o = e.reduce(
                                  function (e, t) {
                                      return e.concat(e[e.length - 1] * t);
                                  },
                                  [1]
                              );
                              return e.map(function (e, n) {
                                  return Math.round(t / o[n]) % e;
                              });
                          })(g, H[D], ff(H[D])),
                          S = k[1],
                          U = k[0];
                      oo = T;
                      var F = d[S][U];
                      (zone_json_d3 = e.slice(0, 14)),
                          (zone_json_d3 = zone_json_d3 + F + e.slice(16, 36)),
                          fetch(zone_json_d3)
                              .then(function (e) {
                                  return e.json();
                              })
                              .then(function (e) {
                                  for (var t = e.XLAT, o = e.XLONG, n = [], i = [], a = [(a = [t.length, t[0].length])[1], a[0]], r = 0; r < t.length; r++) n = n.concat(t[r]);
                                  for (r = 0; r < o.length; r++) i = i.concat(o[r]);
                                  var l = t.map(function (e, t) {
                                          return [e, o[t]];
                                      }),
                                      f = new KDBush(l);
                                  point_list.push(oo), file_list.push(e);
                                  var c = f.range(oo[0] - 0.2, oo[1] - 0.2, oo[0] + 0.2, oo[1] + 0.2).map((e) => l[e]);
                                  (ll_diff = []),
                                      (function (e, t) {
                                          for (var o = 0; o < e.length; o++) {
                                              var n = Math.abs(parseFloat(e[o][0]) - t[0]) + Math.abs(parseFloat(e[o][1]) - t[1]);
                                              ll_diff.push(n);
                                          }
                                      })(c, oo);
                                  var m = ll_diff.indexOf(Math.min(...ll_diff)),
                                      s = ((m = f.range(oo[0] - 0.2, oo[1] - 0.2, oo[0] + 0.2, oo[1] + 0.2)[m]), e.XLAT[m]),
                                      d = e.XLONG[m];
                                  makeplotly3({ customId: zone_json_d3, customIdx: m, lat: s, lng: d });
                              }),
                          loaded_zones_d3.push(F);
                  } else
                      (t = n),
                          (zone_json = e.slice(0, 14)),
                          (zone_json = zone_json + Y + e.slice(16, 30) + "2.json"),
                          fetch(zone_json)
                              .then(function (e) {
                                  return e.json();
                              })
                              .then(function (e) {
                                  for (var o = e.XLAT, n = e.XLONG, i = [], a = [], r = [(r = [o.length, o[0].length])[1], r[0]], l = 0; l < o.length; l++) i = i.concat(o[l]);
                                  for (l = 0; l < n.length; l++) a = a.concat(n[l]);
                                  var f = o.map(function (e, t) {
                                          return [e, n[t]];
                                      }),
                                      c = new KDBush(f);
                                  point_list.push(t), file_list.push(e);
                                  var m = c.range(t[0] - 0.2, t[1] - 0.2, t[0] + 0.2, t[1] + 0.2).map((e) => f[e]);
                                  (ll_diff = []),
                                      (function (e, t) {
                                          for (var o = 0; o < e.length; o++) {
                                              var n = Math.abs(parseFloat(e[o][0]) - t[0]) + Math.abs(parseFloat(e[o][1]) - t[1]);
                                              ll_diff.push(n);
                                          }
                                      })(m, t);
                                  var s = ll_diff.indexOf(Math.min(...ll_diff)),
                                      d = ((s = c.range(t[0] - 0.2, t[1] - 0.2, t[0] + 0.2, t[1] + 0.2)[s]), e.XLAT[s]),
                                      u = e.XLONG[s];
                                  makeplotly3({ customId: zone_json, customIdx: s, lat: d, lng: u });
                              }),
                          loaded_zones.push(Y);
              }
              M.on("ready", function () {
                  M.eachLayer(function (e) {
                      e instanceof L.Marker && (e.setIcon(Y), e.bindPopup(div3, { maxWidth: "auto", maxHeight: "auto" }), e.on("click", T));
                  }),
                      hotspotsMarkers.addLayer(M);
              }),
                  (control._searchfunctionCallBack = function (t) {
                      t || (t = "The search call back is clicked !!"),
                          (function (t) {
                              null != fwfmodellocation && fwfmodellocation.remove(map), map.flyTo(t), fwfclicklocation.setLatLng(t).addTo(map);
                              var n = [parseFloat(t[0]), parseFloat(t[1])],
                                  i = s.range(n[0] - buffer, n[1] - buffer, n[0] + buffer, n[1] + buffer).map((e) => m[e]);
                              (ll_diff = []),
                                  (function (e, t) {
                                      for (var o = 0; o < e.length; o++) {
                                          var n = Math.abs(e[o][0] - t[0]) + Math.abs(e[o][1] - t[1]);
                                          ll_diff.push(n);
                                      }
                                  })(i, n);
                              for (var a = 0, r = ll_diff[0], c = 1; c < ll_diff.length; c++) ll_diff[c] < r && ((r = ll_diff[c]), (a = c));
                              var u,
                                  h,
                                  p = s.range(n[0] - buffer, n[1] - buffer, n[0] + buffer, n[1] + buffer);
                              f =
                                  ((h = (u = l).reduce(
                                      function (e, t) {
                                          return e.concat(e[e.length - 1] * t);
                                      },
                                      [1]
                                  )),
                                  function (e) {
                                      return (
                                          (t = e),
                                          (o = h),
                                          u.map(function (e, n) {
                                              return Math.round(t / o[n]) % e;
                                          })
                                      );
                                      var t, o;
                                  });
                              var b = (function (e, t) {
                                      var o = e.reduce(
                                          function (e, t) {
                                              return e.concat(e[e.length - 1] * t);
                                          },
                                          [1]
                                      );
                                      return e.map(function (e, n) {
                                          return Math.round(t / o[n]) % e;
                                      });
                                  })(l, p[a], f(p[a])),
                                  y = b[1],
                                  _ = b[0],
                                  M = o[y][_];
                              if ("d3" == M) {
                                  var Y = [parseFloat(t[0]), parseFloat(t[1])],
                                      T = v.range(Y[0] - buffer, Y[1] - buffer, Y[0] + buffer, Y[1] + buffer).map((e) => x[e]);
                                  (ll_diff2 = []),
                                      (function (e, t) {
                                          for (var o = 0; o < e.length; o++) {
                                              var n = Math.abs(e[o][0] - t[0]) + Math.abs(e[o][1] - t[1]);
                                              ll_diff2.push(n);
                                          }
                                      })(T, Y);
                                  for (var w = 0, D = ll_diff2[0], z = 1; z < ll_diff2.length; z++) ll_diff2[z] < D && ((D = ll_diff2[z]), (w = z));
                                  var C,
                                      H = v.range(Y[0] - buffer, Y[1] - buffer, Y[0] + buffer, Y[1] + buffer);
                                  ff =
                                      ((C = g).reduce(
                                          function (e, t) {
                                              return e.concat(e[e.length - 1] * t);
                                          },
                                          [1]
                                      ),
                                      function (i) {
                                          return C.map(function (i, a) {
                                              return Math.round(t / o[n]) % e;
                                          });
                                      });
                                  var k = (function (e, t) {
                                          var o = e.reduce(
                                              function (e, t) {
                                                  return e.concat(e[e.length - 1] * t);
                                              },
                                              [1]
                                          );
                                          return e.map(function (e, n) {
                                              return Math.round(t / o[n]) % e;
                                          });
                                      })(g, H[w], ff(H[w])),
                                      S = k[1],
                                      U = k[0];
                                  oo = Y;
                                  var F = d[S][U];
                                  (zone_json_d3 = e.slice(0, 14)),
                                      (zone_json_d3 = zone_json_d3 + F + e.slice(16, 36)),
                                      fetch(zone_json_d3)
                                          .then(function (e) {
                                              return e.json();
                                          })
                                          .then(function (e) {
                                              for (var t = e.XLAT, o = e.XLONG, n = [], i = [], a = [(a = [t.length, t[0].length])[1], a[0]], r = 0; r < t.length; r++) n = n.concat(t[r]);
                                              for (r = 0; r < o.length; r++) i = i.concat(o[r]);
                                              var l = t.map(function (e, t) {
                                                      return [e, o[t]];
                                                  }),
                                                  f = new KDBush(l);
                                              point_list.push(oo), file_list.push(e);
                                              var c = f.range(oo[0] - 0.2, oo[1] - 0.2, oo[0] + 0.2, oo[1] + 0.2).map((e) => l[e]);
                                              (ll_diff = []),
                                                  (function (e, t) {
                                                      for (var o = 0; o < e.length; o++) {
                                                          var n = Math.abs(parseFloat(e[o][0]) - t[0]) + Math.abs(parseFloat(e[o][1]) - t[1]);
                                                          ll_diff.push(n);
                                                      }
                                                  })(c, oo);
                                              var m = ll_diff.indexOf(Math.min(...ll_diff)),
                                                  s = ((m = f.range(oo[0] - 0.2, oo[1] - 0.2, oo[0] + 0.2, oo[1] + 0.2)[m]), e.XLAT[m]),
                                                  d = e.XLONG[m];
                                              (fwfmodellocation = new L.marker([s, d], { icon: redIcon, customId: zone_json_d3, customIdx: m })).bindPopup(div2, { maxWidth: "auto", maxHeight: "auto" }),
                                                  fwfmodellocation.setZIndexOffset(1e3),
                                                  fwfmodellocation.on("click", makeplotly).addTo(map);
                                          }),
                                      loaded_zones_d3.push(F);
                              } else
                                  (t = n),
                                      (zone_json = e.slice(0, 14)),
                                      (zone_json = zone_json + M + e.slice(16, 30) + "2.json"),
                                      fetch(zone_json)
                                          .then(function (e) {
                                              return e.json();
                                          })
                                          .then(function (e) {
                                              for (var o = e.XLAT, n = e.XLONG, i = [], a = [], r = [(r = [o.length, o[0].length])[1], r[0]], l = 0; l < o.length; l++) i = i.concat(o[l]);
                                              for (l = 0; l < n.length; l++) a = a.concat(n[l]);
                                              var f = o.map(function (e, t) {
                                                      return [e, n[t]];
                                                  }),
                                                  c = new KDBush(f);
                                              point_list.push(t), file_list.push(e);
                                              var m = c.range(t[0] - 0.2, t[1] - 0.2, t[0] + 0.2, t[1] + 0.2).map((e) => f[e]);
                                              (ll_diff = []),
                                                  (function (e, t) {
                                                      for (var o = 0; o < e.length; o++) {
                                                          var n = Math.abs(parseFloat(e[o][0]) - t[0]) + Math.abs(parseFloat(e[o][1]) - t[1]);
                                                          ll_diff.push(n);
                                                      }
                                                  })(m, t);
                                              var s = ll_diff.indexOf(Math.min(...ll_diff)),
                                                  d = ((s = c.range(t[0] - 0.2, t[1] - 0.2, t[0] + 0.2, t[1] + 0.2)[s]), e.XLAT[s]),
                                                  u = e.XLONG[s];
                                              (fwfmodellocation = new L.marker([d, u], { icon: redIcon, customId: zone_json, customIdx: s })).bindPopup(div2, { maxWidth: "auto", maxHeight: "auto" }),
                                                  fwfmodellocation.setZIndexOffset(1e3),
                                                  fwfmodellocation.on("click", makeplotly).addTo(map),
                                                  loaded_zones.push(M);
                                          });
                          })(t.split(",").map(Number));
                  }),
                  map.addControl(control);
          });
}
(ObjectFun = {
  confuels: function (e) {
      return [
          "C1 - Spruce–Lichen Woodland",
          "C2 - Boreal Spruce",
          "C3 - Mature Jack or Lodgepole Pine",
          "C4 - Immature Jack or Lodgepole Pine",
          "C5 - Red and White Pine",
          "C6 - Conifer Plantation",
          "C7 - Ponderosa Pine–Douglas-Fir",
          "D1 - Leafless Aspen",
          "M1 C25% - Boreal Mixedwood",
          "M1/M2 C35% - Boreal Mixedwood",
          "M1/M2 C50% - Boreal Mixedwood",
          "M1/M2 C65% - Boreal Mixedwood",
          "S1 - Jack or Lodgepole Pine Slash",
          "O1a - Matted Grass",
          "O1b - Tall Grass",
          "Water",
          "Non-fuel",
          "Urban",
      ][[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19].indexOf(parseInt(e))];
  },
}),
  makeplots(json_fwf);