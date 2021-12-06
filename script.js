// initialize map
var map = L.map('map').setView([14.552562, 120.997557], 16);
var marker = L.marker([14.552562, 120.997557]).addTo(map);
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>'
}).addTo(map);

/*var gpx = 'DS2-0420.gpx';

new L.GPX(gpx, {async: true}).on('loaded', function(e) {
    map.fitBounds(e.target.getBounds());
}).addTo(map);*/

// generate grid
var countX = 10; //cells by x
var countY = 10; //cells by y
var cellWidth = 1000 / countX;
var cellHeight = 800 / countY;
var coordinates = [],
    c = {x: 0, y: 800}, //cursor
    //top-left/top-right/bottom-right/bottom-left
    tLx, tLy,   tRx, tRy,
    bRx, bRy,   bLx, bLy;

tLy = 14.723779494561555;
tLx = 120.94121867396767;
tRy = 14.763607518009065;
tRx = 121.11351929376644;
bRy = 14.511847718676204;
bRx = 121.08341607774038;
bLy = 14.50810787559866;
bLx = 120.98275298975963;
// build coordinates array, from top-left to bottom-right
// count by row

for(var iY = 0; iY < countY; iY++){
  // count by cell in row
  for(var iX = 0; iX < countX; iX++){
    tLx = bLx = c.x;
    tLy = tRy = c.y;
    tRx = bRx = c.x + cellWidth;
    bRy = bLy = c.y - cellHeight;
    var cell = [
      // top-left/top-right/bottom-right/bottom-left/top-left
      [tLx, tLy], [tRx, tRy], [bRx, bRy], [bLx, bLy], [tLx, tLy]
    ];
    coordinates.push(cell);
    // refresh cusror for cell
    c.x = c.x + cellWidth;
  }
  // refresh cursor for row
  c.x = 0;
  c.y = c.y - cellHeight;
}

var grid = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      geometry: {
        type:  'MultiPolygon',
        coordinates: [coordinates]
      }
    }
  ]
};
// add grid to map
L.geoJson(grid).addTo(map);
