var fs = require('fs');
const path = require('path');
const KDBush = require('kdbush');

json_dir = "fwf-zone-merge.json"
var o = JSON.parse(fs.readFileSync(json_dir, 'utf8'));
for (var t = o.ZONE_d02, e = o.XLAT_d02, l = o.XLONG_d02, a = [], r = [], c = [(c = [e.length, e[0].length])[1], c[0]], i = 0; i < e.length; i++) a = a.concat(e[i]);
for (i = 0; i < l.length; i++) r = r.concat(l[i]);
(a = a.map(Number)), (r = r.map(Number));
var s = a.map(function (n, o) {
    return [n, r[o]];
});
const u = new KDBush(s);
const tree = JSON.stringify(u);

fs.writeFile('tree.json', tree, (err) => {
    if (err) {
        throw err;
    }
    console.log("JSON data is saved.");
});
