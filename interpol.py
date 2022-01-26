import subprocess
import os
import json
import gpxpy
import gpxpy.gpx
from datetime import datetime
import time

UPPER_LEFT_X = 120.90541
UPPER_LEFT_Y = 14.785505
DIFF_X = 0.002747
DIFF_Y = 0.002657

# LAT = Y LON = X

# parse
gpx_file = open('DS2-0420-trim.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

sts = []

for track in gpx.tracks:
    for segment in track.segments:
        prevtime = segment.points[0].time
        for point in segment.points:
            #extracted = '({0},{1}) {2}'.format(point.longitude, point.latitude, point.time)
            #print(extracted)
            sts += [(point.longitude,point.latitude,point.time.strftime("%H:%M:%S"))]

#print(sts)
#sts should be an array with elements that contain: lon,lat,time

# for x, we subtract reference 120.904541 from current
# for y, we subtract current from reference 14.785505

# max x: 121.132507 - 120.904541 / 0.002747 = 82.9872588278
# max y: 14.785505 - 14.349548 / 0.002657 = 164.078660143


def interpolation(sts):
    cts = []
    for point in sts:
        x_pos = point[0]
        y_pos = point[1]

        x_grid =  (x_pos - UPPER_LEFT_X) // DIFF_X
        y_grid =  (UPPER_LEFT_Y - y_pos) // DIFF_Y
        xy_grid = str(int(x_grid)) + "-" + str(int(y_grid))

        #for verification
        #xy_grid = str(UPPER_LEFT_X + x_grid * DIFF_X) + "-" + str(UPPER_LEFT_Y - y_grid * DIFF_Y) 
        
        if len(cts) == 0:
            cts.append((xy_grid,(point[2],point[2])))
        elif cts[-1][0] != xy_grid:
            cts[-1] = (cts[-1][0],(cts[-1][1][0],point[2]))
            cts.append((xy_grid,(point[2],point[2])))
        

    return cts
    
cts1 = interpolation(sts)
print(cts1)
