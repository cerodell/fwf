
var json_kdtree = 'json/plotly/fwf-kdtree.json';




require(['kdbush'], function (kdbush) {
    //foo is now loaded.
});

const KDBush = require('kdbush');

fetch(json_kdtree).then(function(response){
    return response.json();
  }).then(function(json){


    var xlat  = json.XLAT
    var xlng = json.XLONG
    var listlat = [];
    var listlng = [];

    var dimensions = [ xlat.length, xlat[0].length ];
    // console.log(dimensions);
    var dimensions = [dimensions[1],dimensions[0]]
    // console.log(dimensions);

    for(var i = 0; i < xlat.length; i++)
    {
        listlat = listlat.concat(xlat[i]);
    }

    for(var i = 0; i < xlng.length; i++)
    {
        listlng = listlng.concat(xlng[i]);
    }

    var points = listlat.map(function(e, i) {
    return [e, listlng[i]];
    });
    const index = new KDBush(points);
    for (const {x, y} of points) index.add(x, y);
    index.finish();


    console.log(index);
    return index
  });