function getControlHrmlContent() {
  return '<div id="controlbox" ><div id="boxcontainer" class="searchbox searchbox-shadow" > <div class="searchbox-menu-container"><button aria-label="Menu" id="searchbox-menubutton" class="searchbox-menubutton"></button> <span aria-hidden="true" style="display:none">Menu</span> </div><div><input id="searchboxinput" type="text" contentEditable=true placeholder="Latitude, Longitude [ex 49.88, -119.49]" style="position: relative;"/></div><div class="searchbox-searchbutton-container"><button aria-label="search" id="searchbox-searchbutton" class="searchbox-searchbutton"></button> <span aria-hidden="true" style="display:none;">search</span> </div></div></div><div class="panel"> <div class="panel-header"> <div class="panel-header-container"> <span class="panel-header-title"></span> <button aria-label="Menu" id="panelbutton" class="panel-close-button"></button> </div></div><div class="panel-content"> </div></div>';
}
function generateHtmlContent(e) {
  for (var t = '<ul class="panel-list">', n = 0; n < e.Items.length; n++) {
      var a = e.Items[n];
      "link" == a.type
          ? ((t += '<li class="panel-list-item"><div>'), (t += '<span class="panel-list-item-icon ' + a.icon + '" ></span>'), (t += '<a href="' + a.href + '"target="_blank">' + a.name + "</a>"), (t += "</li></div>"))
          : "text" == a.type
          ? ((t += '<li class="panel-text"><div>'), (t += "<h3 <b> Disclaimer </b>  </h3>"), (t += '<p class="para-text"' + a.name + "</p>"), (t += "</li></div>"))
          : ((t += '<li class="panel-list-item"><div>'), (t += '<span class="panel-list-item-icon ' + a.icon + '" ></span>'), (t += '<button onclick="' + a.onclick + '">' + a.name + "</button>"), (t += "</li></div>"));
  }
  return t + "</ul>";
}
function createSearchboxControl() {
  return L.Control.extend({
      _sideBarHeaderTitle: "Sample Title",
      _sideBarMenuItems: {
          Items: [
              { type: "link", name: "BlueSky Canada Smoke Forecasts", href: "https://firesmoke.ca/", icon: "icon-fire" },
              { type: "link", name: "Weather Research Forecast Team", href: "https://weather.eos.ubc.ca/cgi-bin/index.cgi", icon: "icon-cloudy" },
              { type: "link", name: "Contact Inforamtion", href: "https://firesmoke.ca/contact/", icon: "icon-phone" },
              { type: "link", name: "Documentation", href: "https://cerodell.github.io/fwf-docs/index.html", icon: "icon-git" },
          ],
          _searchfunctionCallBack: function (e) {
              alert("calling the default search call back");
          },
      },
      options: { position: "topleft" },
      initialize: function (e) {
          L.Util.setOptions(this, e), e.sidebarTitleText && (this._sideBarHeaderTitle = e.sidebarTitleText), e.sidebarMenuItems && (this._sideBarMenuItems = e.sidebarMenuItems);
      },
      onAdd: function (e) {
          (e = L.DomUtil.create("div")).id = "controlcontainer";
          var t = this._sideBarHeaderTitle,
              n = this._sideBarMenuItems,
              a = this._searchfunctionCallBack;
          return (
              $(e).html(getControlHrmlContent()),
              setTimeout(function () {
                  $("#searchbox-searchbutton").click(function () {
                      var e = $("#searchboxinput").val();
                      a(e);
                  }),
                      $("#searchbox-menubutton").click(function () {
                          $(".panel").toggle("slide", { direction: "left" }, 500);
                      }),
                      $(".panel-close-button").click(function () {
                          $(".panel").toggle("slide", { direction: "left" }, 500);
                      }),
                      $(".panel-header-title").text(t);
                  var e = generateHtmlContent(n);
                  $(".panel-content").html(e);
              }, 1),
              L.DomEvent.disableClickPropagation(e),
              e
          );
      },
  });
}
