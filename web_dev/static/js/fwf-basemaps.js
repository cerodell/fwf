
var gl = L.mapboxGL({
	attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>',
	style: 'topo-notab.json',
}).addTo(map)


        
	var searchboxControl=createSearchboxControl();
	var control = new searchboxControl({
		sidebarTitleText: 'Header',
		sidebarMenuItems: {
			Items: [
				{ type: "link", name: "Link 1 (github.com)", href: "http://github.com", icon: "icon-local-carwash" },
				{ type: "link", name: "Link 2 (google.com)", href: "http://google.com", icon: "icon-cloudy" },
				{ type: "button", name: "Button 1", onclick: "alert('button 1 clicked !')", icon: "icon-potrait" },
				{ type: "button", name: "Button 2", onclick: "button2_click();", icon: "icon-local-dining" },
				{ type: "link", name: "Link 3 (stackoverflow.com)", href: 'http://stackoverflow.com', icon: "icon-bike" },

			]
		}
	});

	control._searchfunctionCallBack = function (searchkeywords)
	{
		if (!searchkeywords) {
			searchkeywords = "The search call back is clicked !!"
		}
		// alert(searchkeywords);
	}

	map.addControl(control);

function button2_click()
{
	alert('button 2 clicked !!!');

}