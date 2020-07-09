
var json_kdtree = '/bluesky/fireweather/fwf/data/fwf-kdtree.json';




// require(['kdbush'], function (kdbush) {
//     //foo is now loaded.
// });

const KDBush = require('kdbush');

var fs = require('fs');
var json = JSON.parse(fs.readFileSync(json_kdtree, 'utf8'));


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
// for (const {x, y} of points) index.add(x, y);
// index.finish();
// fs.writeFile('/bluesky/fireweather/fwf/data/test-tree.json', index, 'utf8');

fs.writeFile ("/bluesky/archive/fireweather/test/built-kd-tree.json", JSON.stringify(index), function(err) {
  if (err) throw err;
  console.log('complete');
  }
);


console.log(index);
