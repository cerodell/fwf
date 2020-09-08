function getControlHrmlContent() {
    return '<div id="controlbox" ><div id="boxcontainer" class="searchbox searchbox-shadow" > <div class="searchbox-menu-container"><button aria-label="Menu" id="searchbox-menubutton" class="searchbox-menubutton"></button> <span aria-hidden="true" style="display:none">Menu</span> </div><div><input id="searchboxinput" type="text" contentEditable=true placeholder="Latitude, Longitude [ex 49.88, -119.49]" style="position: relative;"/></div><div class="searchbox-searchbutton-container"><button aria-label="search" id="searchbox-searchbutton" class="searchbox-searchbutton"></button> <span aria-hidden="true" style="display:none;">search</span> </div></div></div><div class="panel"> <div class="panel-header"> <div class="panel-header-container"> <span class="panel-header-title"></span> <button aria-label="Menu" id="panelbutton" class="panel-close-button"></button> </div></div><div class="panel-content"> </div></div>';
}
function generateHtmlContent(a) {
    for (var b = '<ul class="panel-list">', d = 0; d < a.Items.length; d++) {
        var c = a.Items[d],
            b = b + '<li class="panel-list-item"><div>';
        "link" == c.type
            ? ((b += '<span class="panel-list-item-icon ' + c.icon + '" ></span>'), (b += '<a href="' + c.href + '"target="_blank">' + c.name + "</a>"))
            : "button" == c.type && ((b += '<span class="panel-list-item-icon ' + c.icon + '" ></span>'), (b += '<button onclick="' + c.onclick + '">' + c.name + "</button>"));
        b += "</li></div>";
    }
    return b + "</ul>";
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
            _searchfunctionCallBack: function (a) {
                alert("calling the default search call back");
            },
        },
        options: { position: "topleft" },
        initialize: function (a) {
            L.Util.setOptions(this, a);
            a.sidebarTitleText && (this._sideBarHeaderTitle = a.sidebarTitleText);
            a.sidebarMenuItems && (this._sideBarMenuItems = a.sidebarMenuItems);

        },
        onAdd: function (a) {
            a = L.DomUtil.create("div");
            a.id = "controlcontainer";
            var b = this._sideBarHeaderTitle,
                d = this._sideBarMenuItems,
                c = this._searchfunctionCallBack;
            $(a).html(getControlHrmlContent());
            setTimeout(function () {
                $("#searchbox-searchbutton").click(function () {
                    var a = $("#searchboxinput").val();
                    c(a);
                });
                $("#searchbox-menubutton").click(function () {
                    $(".panel").toggle("slide", { direction: "left" }, 500);
                });
                $(".panel-close-button").click(function () {
                    $(".panel").toggle("slide", { direction: "left" }, 500);
                });
                $(".panel-header-title").text(b);
                var a = generateHtmlContent(d);
                $(".panel-content").html(a);
            }, 1);
            L.DomEvent.disableClickPropagation(a);
            return a;
        },
    });
}
