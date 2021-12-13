// initialize map
var map = L.map('map').setView([14.552562, 120.997557], 16);
var marker = L.marker([14.552562, 120.997557]).addTo(map);
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: 'Map data &copy; <a href="http://www.osm.org">OpenStreetMap</a>',
  maxNativeZoom:19,
  maxZoom:25
}).addTo(map);

/*var gpx = 'DS2-0420.gpx';

new L.GPX(gpx, {async: true}).on('loaded', function(e) {
    map.fitBounds(e.target.getBounds());
}).addTo(map);*/

L.GridLayer.GridDebug = L.GridLayer.extend({
  createTile: function (coords) {
    const tile = document.createElement('div');
    tile.style.outline = '1px solid green';
    tile.style.fontWeight = 'bold';
    tile.style.fontSize = '14pt';
    
    var size = this.getTileSize();
    var nwPoint = coords.scaleBy(size);
  
    // calculate geographic coordinates of top left tile pixel
    var nw = map.unproject(nwPoint, coords.z);
    tile.innerHTML = [coords.z, nw.lat.toFixed(6), nw.lng.toFixed(6)].join('/');
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