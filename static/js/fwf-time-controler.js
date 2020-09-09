function formatDate(date) {
    var d = new Date(date),
        hour = '' + d.getUTCHours(),
        day = '' + d.getUTCDate(),
        month = '' + (d.getUTCMonth() + 1),
        year = d.getUTCFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
    hour = 3.0*Math.floor(parseInt(hour)/3.0)
    hour = hour.toString()
    var UTCTimeMap = [year, month, day].join('-')
    UTCTimeMap = [UTCTimeMap,hour].join('T')
    UTCTimeMap = UTCTimeMap + ':00:00Z'

    return UTCTimeMap
}

var now = new Date;
UTCTimeMap = formatDate(now);
console.log(UTCTimeMap);

function formatDate(date) {
    var d = new Date(date),
        hour = '' + d.getUTCHours(),
        day = '' + d.getUTCDate(),
        month = '' + (d.getUTCMonth() + 1),
        year = d.getUTCFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;
    var UTCTimePlot = [year, month, day].join('-')
    UTCTimePlot = [UTCTimePlot,hour].join('T')
    UTCTimePlot = UTCTimePlot + ':00:00Z'

    return UTCTimePlot
}

var now = new Date;
UTCTimePlot = formatDate(now);
console.log(UTCTimePlot);