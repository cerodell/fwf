from plotly.offline import plot
from plotly.graph_objs import Scatter, Box

plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])], filename="/bluesky/fireweather/fwf/firewx_website/html/py_test.html", output_type='div')


# fig =px.offline.scatter(x=range(10), y=range(10), output_type='div')
# fig.write_html("/bluesky/fireweather/fwf/firewx_website/html/py_test.html", include_plotlyjs=False)



# scp -r /bluesky/fireweather/fwf/firewx_website/html/py_test.html /bluesky/archive/fireweather/test/