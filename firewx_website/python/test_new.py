import os
import json
import requests
import folium


url = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
vis1 = json.loads(requests.get(f'{url}/vis1.json').text)
vis2 = json.loads(requests.get(f'{url}/vis2.json').text)
vis3 = json.loads(requests.get(f'{url}/vis3.json').text)





m = folium.Map(
    location=[46.3014, -123.7390],
    zoom_start=7,
    tiles='Stamen Terrain'
)
m.add_child(folium.LatLngPopup())

# folium.Marker(
#     location=[47.3489, -124.708],
#     popup=folium.Popup(max_width=450).add_child(
#         folium.Vega(vis1, width=450, height=250))
# ).add_to(m)

# folium.Marker(
#     location=[44.639, -124.5339],
#     popup=folium.Popup(max_width=450).add_child(
#         folium.Vega(vis2, width=450, height=250))
# ).add_to(m)

# folium.Marker(
#     location=[46.216, -124.1280],
#     popup=folium.Popup(max_width=450).add_child(
#         folium.Vega(vis3, width=450, height=250))
# ).add_to(m)


m.save('/Users/rodell/fireweather/html/pop_ups.html')