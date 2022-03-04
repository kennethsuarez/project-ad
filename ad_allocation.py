from calendar import c
import csv
import functools
import json

UPPER_LEFT_X = 120.90541
UPPER_LEFT_Y = 14.785505
DIFF_X = 0.002747
DIFF_Y = 0.002657

def convertToGrid(coords):
    lon, lat = coords
    x_grid = (float(lon) - UPPER_LEFT_X) // DIFF_X
    y_grid = (UPPER_LEFT_Y - float(lat)) // DIFF_Y
    return str(int(x_grid)) + "$" + str(int(y_grid))


################################### initial setup ###################################
location_long_map = open("TTDM/output/location_long_map", "r")
loc_long_dict = {}

for x in location_long_map:
    zone, long_z = x.split()
    loc_long_dict[zone] = long_z

#print(loc_long_dict)

graph_dict = {}
zone_min_dict = {}

with open("TTDM/output/graph/Taxi_graph.csv", newline="") as taxi_graph:
    graph = csv.reader(taxi_graph, skipinitialspace=True, delimiter=' ', quotechar='|')
    number = next(graph)[0]
    graph_dict = {k: [] for k in range(1,int(number)+1)}
    zone_min_dict = {k: [] for k in range(1,int(number)+1)}
    next(graph)
    for row in graph:
        #print(row)
        graph_dict[int(row[0])].append((int(row[1]),float(row[2])))

#print(graph_dict)

for src, content in graph_dict.items():
    zone_min_dict[src] = min(list(map(lambda x : x[1], content)))

#print(zone_min_dict)

#zones = {k: [] for k in range(1,len(zone_min_dict)+1)}

################## input #########################

#### load the zones ####
priority_zones_json = open('priority_zones2.json')
priority_zones = json.load(priority_zones_json)
#print(priority_zones)

#### load the ad lengths ####
ad_list_json = open('ad_list.json')
ad_lengths = json.load(ad_list_json)

#print(ad_lengths)

#for abc in range(3):
coords = input()
ad_len = float(input())
ad_name = input()

past_total = 0
if priority_zones.get(coords): #if that coordinate is a priority zone
    for ad in priority_zones[coords]:
        past_total += ad_lengths[ad]
else:
    priority_zones[coords] = []

if past_total + ad_len < zone_min_dict[int(loc_long_dict[coords])]:
    print("ad {0} was ACCEPTED".format(ad_name))
    print("time left: {0}".format(zone_min_dict[int(loc_long_dict[coords])]-(past_total + ad_len)))
    priority_zones[coords].append(ad_name+".mp4")
    ad_lengths[ad_name+".mp4"] = ad_len
else:
    print("ad {0} was REJECTED".format(ad_name))
    print("available time is {0}".format(zone_min_dict[int(loc_long_dict[coords])] - past_total))

#print(priority_zones)
#print(ad_lengths)


#prep for output
priority_zones_json.close()
ad_list_json.close()

with open('priority_zones2.json', 'w') as outfile:
    json.dump(priority_zones, outfile)
    
with open('ad_list.json', 'w') as outfile:
    json.dump(ad_lengths, outfile)




