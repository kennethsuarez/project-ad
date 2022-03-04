// converter function
const UPPER_LEFT_X = 120.90541
const UPPER_LEFT_Y = 14.785505
const DIFF_X = 0.002747
const DIFF_Y = 0.002657

function convertLonX(lon) {
  return Math.floor((lon - UPPER_LEFT_X) / DIFF_X) 
}

function convertLatY(lat) {
  return Math.floor((UPPER_LEFT_Y - lat) / DIFF_Y)
}

// initialize map
var map = L.map('map').setView([14.552562, 120.997557], 17);
var marker = L.marker([14.552562, 120.997557]).addTo(map);
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>',
  minNativeZoom:17,
  minZoom:17,
  maxNativeZoom:17,
  maxZoom:17
}).addTo(map);

/*var gpx = 'gpx_test/DS2-0420.gpx';

new L.GPX(gpx, {async: true}).on('loaded', function(e) {
    map.fitBounds(e.target.getBounds());
}).addTo(map);*/

L.GridLayer.GridDebug = L.GridLayer.extend({
  createTile: function (coords) {
    const tile = document.createElement('div');
    tile.style.outline = '1px solid green';
    tile.style.fontWeight = 'light';
    tile.style.fontSize = '30pt';
    
    var size = this.getTileSize();
    var nwPoint = coords.scaleBy(size);
  
    // calculate geographic coordinates of top left tile pixel
    var nw = map.unproject(nwPoint, coords.z);
    tile.innerHTML = [convertLonX(nw.lng.toFixed(6)), convertLatY(nw.lat.toFixed(6))].join('$');
    return tile;
  },
});

L.gridLayer.gridDebug = function (opts) {
  return new L.GridLayer.GridDebug(opts);
};

map.addLayer(L.gridLayer.gridDebug());

function drawMetroManilaBoundary()
{
    url = 'https://nominatim.openstreetmap.org/search.php?q=Metro_Manila+Philippines&polygon_geojson=1&format=json'
    fetch(url).then(function(response) {
    return response.json();
  })
  .then(function(json) {
    geojsonFeature = json[0].geojson;
    L.geoJSON(geojsonFeature).addTo(map);
  });
}

drawMetroManilaBoundary()
