# WEBPAGE GUIDE NM

## Structure
Hello! I recommend having a directory structure like the one here.

- Have a static folder containing js, css, img scripts/files.
- you will see a lot of scripts in each...most are dependencies to have leaflet work and are called in index.html
- most all the js are scripts i worte are used in the body of index html
- all css are in the head of index.html

 - The index.html is a kdtree free version of mine... a decent starting point but needs work.



## Basemap

If you like the basemap check out
https://openmaptiles.org/docs/website/leaflet/

Here is a fun webpage to make the josn file that styles the map.
https://maputnik.github.io/editor/#1.28/0/0

- You will see in the nm folder a topo.joson file...that its what i use to style to fwf map and in `static/js/fwf-basemaps-0.0.3.js`
- you will need to make an account with https://cloud.maptiler.com/auth/widget?mode=select&next=https%3A%2F%2Fcloud.maptiler.com%2Faccount%2Fanalytics and get an access token....please dont use mine as you only get so many free ones..not to worry cause I removed mine anyway :)
- youll see in topo.josn `<your access token>`


## Popups
You said you had the most interest in the weather station popup?
- I have added comments and cleaned that script. Look under `static/js/fwf-wxstations-nm.js `
- also look at `static/css/fwf-popup-0.0.1.css` to make the popups pretty.
