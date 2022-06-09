import gpxpy
import gpxpy.gpx
from datetime import datetime
import time

# parse

gpx_file = open('gpx_test/DS2-0420.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        prevtime = segment.points[0].time
        for point in segment.points:
            currtime = point.time
            delta = currtime - prevtime
            time.sleep(delta.seconds)
            print('({0},{1}) {2}'.format(point.latitude, point.longitude, point.time))
            prevtime = currtime

