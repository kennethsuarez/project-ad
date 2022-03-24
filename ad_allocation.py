from calendar import c
import csv
import functools
import json
from cmath import nan
import math
from scipy.stats import t
import collections
import warnings
import numpy as np

warnings.filterwarnings("ignore",category =RuntimeWarning)
# disable scipy warnings for the meantime
# RuntimeWarning: invalid value encountered in multiply
#   lower_bound = _a * scale + loc

class Outgoing:
    def __init__(self, loc):
        # self.pairs = [loc]   # contains destination location along with interval
        self.intervals = [loc[1]]
        self.outliers = []
        self.ave = 0
        self.sd = 0
        self.lb = 0

    def addLoc(self, loc):
        # self.pairs.append(loc)    # use for testing - to see time to each dest.
        self.intervals.append(loc[1])

    def getAverage(self):
        total = 0

        for value in self.intervals:
            interval = int(value)
            
            if interval < 0:            # ignore negative time intervals
                continue

            total += interval
            ave = total/len(self.intervals)

            self.ave = ave
    
    def getSD(self):
        # only call after calling getAverage()
        num = 0

        for value in self.intervals:
            num += (float(value) - self.ave) ** 2

        sd = math.sqrt(num/len(self.intervals))
        self.sd = sd

    def getLowerBound(self):
        # only call after calling getSD()
        temp = t.ppf(0.2, len(self.intervals) - 1, loc = self.ave, scale = self.sd)
        if temp < 10.0 or self.sd == 0:
            temp = 10.0
        self.lb = temp

    def removeOutliers(self):
        arr = np.array(self.intervals)
        
        q1 = np.quantile(arr, 0.25)
        q3 = np.quantile(arr, 0.75)
        med = np.median(arr)
        
        iqr = q3-q1
        
        upper_bound = q3 + (1.5 * iqr)
        lower_bound = q1 - (1.5 * iqr)
        
        self.outliers = arr[(arr <= lower_bound) | (arr >= upper_bound)]

        self.intervals = [x for x in self.intervals if x > lower_bound and x < upper_bound]
        # print(str(self.intervals) + "\n")
        # print('The following are the outliers in the boxplot:{}'.format(outliers))

# initialize important values 
UPPER_LEFT_X = 120.90541
UPPER_LEFT_Y = 14.785505
DIFF_X = 0.002747
DIFF_Y = 0.002657
OPER_TIME = 28800   # 8 hours (28,800 sec)
AD_SLOT_TIME = 5    # 5 second slot
avail_slots = OPER_TIME/AD_SLOT_TIME    # number of total slots (global time)

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
                outgoing[loc1].addLoc([loc2, interval])
            else:
                outgoing[loc1] = Outgoing([loc2, interval])

################################### initial setup ###################################
location_long_map = open("TTDM/output/location_long_map", "r")
loc_long_dict = {}
# load corresponding index for each grid-coordinate
for x in location_long_map:
    zone, long_z = x.split()
    loc_long_dict[zone] = long_z

#print(loc_long_dict)

outgoing = {}       # x1$y1 : [[x2$y2 : interval1], [x3$y3 : interval2], ...]

# perform data computation
PATH = 'TTDM/input/Taxi_Train_Data.csv'
with open(PATH, newline="") as taxi_graph:

    data = csv.reader(open(PATH))
    generateListFromData(data, outgoing, loc_long_dict)
    #outgoing = collections.OrderedDict(sorted(outgoing.items())) # sort dictionary by key

    # filter outliers
    for key in outgoing: 
        if len(outgoing[key].intervals) > 2:
            outgoing[key].removeOutliers()

    # get average of each outgoing locations
    for key in outgoing: 
        outgoing[key].getAverage()

    # get standard deviation of each outgoing locations
    for key in outgoing: 
        outgoing[key].getSD()

    for key in outgoing:
        outgoing[key].getLowerBound()

# testing key-value intervals
# for key, value in outgoing.items():
#     print(str(key) + ", " + "average: " + str(value.ave) + " sd: " + str(value.sd) + " lower bound: " + str(value.lb) 
#         + "\n" + str(value.intervals) + "\n" + "outliers: " + str(value.outliers) + "\n" )

################## input #########################

#### load the zones ####
priority_zones_json = open('priority_zones2.json')
priority_zones = json.load(priority_zones_json)
#print(priority_zones)

#### load the ad lengths ####
ad_list_json = open('ad_list.json')
ad_list = json.load(ad_list_json)

# subtract total play time of each ad to the global time (slot-based
ad_slots_dict = {} # for storing the baselines
for ad in ad_list:
    # we add new value to dictionary for baseline ad slots 
    ad_total_time = ad_list[ad]['len'] * ad_list[ad]['count']
    ad_slots_dict[ad] = (ad_total_time / AD_SLOT_TIME) * (1/0.2)

#print(ad_lengths)

#for abc in range(3):
coords = input('Enter coordinates (x$y): ')
ad_len = float(input('Enter ad length: '))
ad_name = input('Enter ad name: ')
ad_count = int(input('Enter required number of plays: '))

# for testing
# coords = "34$86"
# ad_len = 6.0
# ad_name = "test"
# ad_count = 100

past_total = 0
# verify if coordinates of input is a priority zone
if priority_zones.get(coords): 
    for ad in priority_zones[coords]:
        past_total += ad_list[ad]['len']
else:
    priority_zones[coords] = []

# check if requested ad can be allocated
# 1st condition: specified zone still has space for new ad
if past_total + ad_len < outgoing[loc_long_dict[coords]].lb:

    # 2nd condition: requested number of plays feasible for the day
        
    #check for baseline number of ads, for new ad.
    curr_slots  = ((int(ad_len) * int(ad_count)) / AD_SLOT_TIME) * (1/0.2)
    
    # For each zone we need to subtract the allocated
    for zone_name, zone_ads in priority_zones.items():

        if loc_long_dict.get(zone_name):
            zone_slots = (8 * outgoing[loc_long_dict[zone_name]].ave) / AD_SLOT_TIME # very rough hard code
        else:
            zone_slots = (8 * 10) / AD_SLOT_TIME
    

        zone_ads_total = 0
        for ad in zone_ads:
            zone_ads_total += ad_list[ad]['len']
        
        if zone_name == coords and ad_name not in zone_ads: # only ad to length if that ad didn't exist
           zone_ads_total += ad_len

        # subtract the ads that were already allocated before
        for ad in zone_ads:
            ad_slots_dict[ad] -= (ad_list[ad]['len']/zone_ads_total) * zone_slots

        # if we are in the currently being checked zone, then we also subtract.
        if zone_name == coords and ad_name not in zone_ads: 
            # the ad must not already exist in the zone, otherwise we are subtracting twice.
            curr_slots -= (ad_len/zone_ads_total) * zone_slots

    ad_total_slots = 0
    for ad in ad_slots_dict:
        ad_total_slots += ad_slots_dict[ad]

    ad_total_slots += curr_slots
    print("{0}/{1}".format(ad_total_slots,avail_slots))

    if avail_slots > ad_total_slots:
        avail_slots -= ad_total_slots   # deduct allocated slots to available slots
        print("ad {0} was ACCEPTED".format(ad_name))
        print("remaining slots: {0}".format(avail_slots))
        print("time left: {0}".format(outgoing[loc_long_dict[coords]].lb - (past_total + ad_len)))

        ad_name += ".mp4"
        # add new ad to priority zones json file
        if ad_name not in priority_zones[coords]:   # only add same ad in zone once
            priority_zones[coords].append(ad_name)   

        # add new ad to ad_list
        if ad_name not in ad_list:
            ad_list[ad_name] = {"len":ad_len,"count": ad_count}
        else:   
            old_ad_len = ad_list[ad_name]['len']    # assume len does not change for same ad
            new_ad_count = ad_count + ad_list[ad_name]['count'] # increment count if already existing in ad list
            ad_list[ad_name] = {"len":old_ad_len, "count": new_ad_count}
    else: 
        print("ad {0} was REJECTED".format(ad_name))
        print("global time exceeded")
        print("available slots are {0}".format(avail_slots))
else:
    print("ad {0} was REJECTED".format(ad_name))
    print("zone does not have remaining space")
    print("available zone time is {0}".format(outgoing[loc_long_dict[coords]].lb - past_total))

#print(priority_zones)
#print(ad_lengths)

#prep for output
priority_zones_json.close()
ad_list_json.close()

with open('priority_zones2.json', 'w') as outfile:
    json.dump(priority_zones, outfile)
    
with open('ad_list.json', 'w') as outfile:
    json.dump(ad_list, outfile)
