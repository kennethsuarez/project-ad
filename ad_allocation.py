from calendar import c
import csv
import functools
import json
from cmath import nan
import math
from scipy.stats import t
import collections

class Outgoing:
    def __init__(self, loc):
        self.pairs = [loc]
        self.ave = 0
        self.sd = 0
        self.lb = 0

    def addLoc(self, loc):
        self.pairs.append(loc)

    def getAverage(self):
        total = 0

        for value in self.pairs:
            interval = int(value[1])    # value[1] contains time interval
            
            if interval < 0:            # ignore negative time intervals
                continue

            total += interval
            ave = total/len(self.pairs)

            self.ave = ave
    
    def getSD(self):
        # only call after calling getAverage()
        num = 0

        for value in self.pairs:
            num += (float(value[1]) - self.ave) ** 2

        sd = math.sqrt(num/len(self.pairs))
        self.sd = sd

    def getLowerBound(self):
        # only call after calling getSD()
        temp = t.ppf(0.2, len(self.pairs) - 1, loc = self.ave, scale = self.sd)
        if temp < 10.0 or self.sd == 0:
            temp = 10.0
        self.lb = temp

UPPER_LEFT_X = 120.90541
UPPER_LEFT_Y = 14.785505
DIFF_X = 0.002747
DIFF_Y = 0.002657

def convertToGrid(coords):
    lon, lat = coords
    x_grid = (float(lon) - UPPER_LEFT_X) // DIFF_X
    y_grid = (UPPER_LEFT_Y - float(lat)) // DIFF_Y
    return str(int(x_grid)) + "$" + str(int(y_grid))

def generateListFromData(data, outgoing, loc_long_dict):
    for line in data:
        # start from left until length - 1
        # ignore reference value
        for i in range(1, len(line)-1):
            
            # convert grid coordinates into index-based 
            traj1_data = line[i].split('@')
            loc1 = loc_long_dict[traj1_data[0]]

            traj2_data = line[i+1].split('@')
            loc2 = loc_long_dict[traj2_data[0]]

            # should always be positive
            interval = int((float(traj2_data[1]) - float(traj1_data[1]))/1000)
            if interval < 0:
                continue    # skip pair if negative 

            # add outgoing from current point i
            if loc1 in outgoing:
                outgoing[loc1].addLoc([loc2,interval])
            else:
                outgoing[loc1] = Outgoing([loc2, interval])

################################### initial setup ###################################
location_long_map = open("TTDM/output/location_long_map", "r")
loc_long_dict = {}
# load corresponding index for each grid-coordinate
for x in location_long_map:
    zone, long_z = x.split()
    loc_long_dict[zone] = long_z

outgoing = {}       # x1$y1 : [[x2$y2 : interval1], [x3$y3 : interval2], ...]

# perform data computation
PATH = 'TTDM/input/Taxi_Train_Data.csv'
with open(PATH, newline="") as taxi_graph:

    data = csv.reader(open(PATH))
    generateListFromData(data, outgoing, loc_long_dict)
    #outgoing = collections.OrderedDict(sorted(outgoing.items())) # sort dictionary by key

    # get average of each outgoing locations
    for key in outgoing: 
        outgoing[key].getAverage()

    # get standard deviation of each outgoing locations
    for key in outgoing: 
        outgoing[key].getSD()

    for key in outgoing:
        outgoing[key].getLowerBound()


for key, value in outgoing.items():
    print(str(key) + ", " + "average: " + str(value.ave) + " sd: " + str(value.sd) + " lower bound: " + str(value.lb) + "\n")

################## input #########################

#### load the zones ####
priority_zones_json = open('priority_zones2.json')
priority_zones = json.load(priority_zones_json)
#print(priority_zones)

#### load the ad lengths ####
ad_list_json = open('ad_list.json')
ad_list = json.load(ad_list_json)

#print(ad_lengths)

#for abc in range(3):
coords = input()
ad_len = float(input())
ad_name = input()
ad_count = input() # currently not really handled

past_total = 0
# verify if coordinates of input is a priority zone
if priority_zones.get(coords): 
    for ad in priority_zones[coords]:
        past_total += ad_list[ad]['len']
else:
    priority_zones[coords] = []

# check if requested ad can be allocated
if past_total + ad_len < outgoing[loc_long_dict[coords]].lb:
    print("ad {0} was ACCEPTED".format(ad_name))
    print("time left: {0}".format(outgoing[loc_long_dict[coords]].lb - (past_total + ad_len)))
    priority_zones[coords].append(ad_name+".mp4")
    ad_list[ad_name+".mp4"] = {"len":ad_len,"count": ad_count}
else:
    print("ad {0} was REJECTED".format(ad_name))
    print("available time is {0}".format(outgoing[loc_long_dict[coords]].lb - past_total))

#print(priority_zones)
#print(ad_lengths)

#prep for output
priority_zones_json.close()
ad_list_json.close()

with open('priority_zones2.json', 'w') as outfile:
    json.dump(priority_zones, outfile)
    
with open('ad_list.json', 'w') as outfile:
    json.dump(ad_list, outfile)
