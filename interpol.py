from audioop import avg
from fileinput import filename
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

def load_sts(filename):
    gpx_file = open(filename, 'r')
    gpx = gpxpy.parse(gpx_file)
    sts = []

    for track in gpx.tracks:
        for segment in track.segments:
            prevtime = segment.points[0].time
            for point in segment.points:
                #extracted = '({0},{1}) {2}'.format(point.longitude, point.latitude, point.time)
                #print(extracted)
                #sts += [(point.longitude,point.latitude,point.time.strftime("%H:%M:%S"))]
                sts += [(point.longitude,point.latitude,point.time)]
    
    return sts


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
        xy_grid = str(int(x_grid)) + "$" + str(int(y_grid))

        #for verification
        #xy_grid = str(UPPER_LEFT_X + x_grid * DIFF_X) + "-" + str(UPPER_LEFT_Y - y_grid * DIFF_Y) 
        
        if len(cts) == 0:
            cts.append((xy_grid,(point[2],point[2])))
        elif cts[-1][0] != xy_grid:
            cts[-1] = (cts[-1][0],(cts[-1][1][0],point[2]))
            cts.append((xy_grid,(point[2],point[2])))
    return cts

def avg_cell_time(cts):
    gaps = []
    #gapswithzone = []

    for cell in cts:
        gaps += [(cell[1][1] - cell[1][0]).seconds]
    #   gapswithzone += [(cell[0],(cell[1][1] - cell[1][0]).seconds)]
    #   filtered = filter(lambda item: item[1] >= 120, gapswithzone)

    #print(list(filtered))
    return sum(gaps)/len(gaps)

def divide_cts(cts,seq_thresh):
    
    cts_list = []
    curr_cts = []
    for cell in cts:
        cur_val = (cell[0],int(cell[1][0].timestamp()*1000))
        curr_cts.append(cur_val)
        if (cell[1][1] - cell[1][0]).seconds > seq_thresh:
            cts_list.append(list(curr_cts))
            curr_cts.clear()
            curr_cts.append(cur_val)
    return cts_list


# main code
file = 'DS2-0420.gpx'

sts = load_sts(file)
#print(sts)
cts1 = interpolation(sts)
#print(cts1)
avg_cell = avg_cell_time(cts1)
seq_thresh = 2*avg_cell
divided_cts_1 = divide_cts(cts1,seq_thresh)

for cts in divided_cts_1:
    print("20000005", end = '')
    for cell in cts:
        print("," + str(cell[0]) + "@" + str(cell[1]) , end = '')
    print('')   

print("file used: " + file)
print("Average time per cell: " + str(avg_cell))
print("Number of sequences: " + str(len(divided_cts_1)))
print("Sequence threshold: " + str(seq_thresh))
lengths = [len(i) for i in divided_cts_1]
print("Average sequence length: " + str(float(sum(lengths)) / len(lengths))) 
