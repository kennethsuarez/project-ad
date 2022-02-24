import csv
import functools

location_long_map = open("TTDM/output/location_long_map", "r")
loc_long_dict = {}

for x in location_long_map:
    zone, long = x.split()
    loc_long_dict[zone] = long

print(loc_long_dict)

graph_dict = {}
zone_min_dict = {}

with open("TTDM/output/graph/Taxi_graph.csv", newline="") as taxi_graph:
    graph = csv.reader(taxi_graph, skipinitialspace=True, delimiter=' ', quotechar='|')
    number = next(graph)[0]
    graph_dict = {k: [] for k in range(1,int(number)+1)}
    zone_min_dict = {k: [] for k in range(1,int(number)+1)}
    next(graph)
    for row in graph:
        print(row)
        graph_dict[int(row[0])].append((int(row[1]),float(row[2])))

#print(graph_dict)

for src, content in graph_dict.items():
    zone_min_dict[src] = min(list(map(lambda x : x[1], content)))

print(zone_min_dict)

zones = {k: [] for k in range(1,len(zone_min_dict)+1)}

for abc in range(3):
    zone = int(loc_long_dict[input()])
    ad_len = float(input())
    ad_name = input()

    past_total = 0
    if zones[zone]:
        times = list(map(lambda x : x[0], zones[zone]))
        past_total = functools.reduce(lambda a, b: a+b, times)

    if past_total + ad_len < zone_min_dict[zone]:
        print("ad {0} was ACCEPTED".format(ad_name))
        print("time left: {0}".format(zone_min_dict[zone]-(past_total + ad_len)))
        zones[zone].append((ad_len,ad_name))
    else:
        print("ad {0} was REJECTED".format(ad_name))
        print("available time is {0}".format(zone_min_dict[zone] - past_total))

print(zones)




