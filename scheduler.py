import subprocess
import os
import json
from datetime import datetime
import time
import math
import numpy as np
import jpype
import jpype.imports
from jpype.types import *
import csv
import functools

if not os.path.exists('output'):
    os.makedirs('output')

text_file = open("output/Output.txt", "w")

UPPER_LEFT_X = 120.90541
UPPER_LEFT_Y = 14.785505
DIFF_X = 0.002747
DIFF_Y = 0.002657

def convertToGrid(coords):
    lon, lat = coords
    x_grid = (float(lon) - UPPER_LEFT_X) // DIFF_X
    y_grid = (UPPER_LEFT_Y - float(lat)) // DIFF_Y
    return str(int(x_grid)) + "$" + str(int(y_grid))

#def generateNextQueue(pred_loc,default_ad_list): deprecated
#    ads = []
#    
#    if priority_zones.get(pred_loc):
#        ads = priority_zones[pred_loc]
#    else:
#        return default_ad_list
#    temp = []
#    for file_name in ads:
#        temp.append(file_name)
#    #print("temp gnQ")
#    #print(temp)
#    return temp

def ubs_utility_func(count_t,count):
    lambda_a = 1000 # not yet sure
    theta_a = 0 # not yet sure
    gamma_a = 0.00015 # from the paper
    return lambda_a * ((1/(1+math.e ** (-gamma_a*(count_t-count))))-theta_a)

def ubs(given_ad_list,ad_play_counts,ad_list,time,has_prio):
    playlist = []
    incr = 0.2
    if has_prio:
        incr = 1

    count_in_playlist = {}          
    for ad in given_ad_list:              
        count_in_playlist[ad] = 0
        
    playlist_duration = 0
    print("time is")
    print(time)

    while playlist_duration < time:
        utility_gain = {}
        for ad in given_ad_list:
            utility_gain[ad] = 0
    
        for ad in given_ad_list:
            temp_1 = math.log(ubs_utility_func(ad_play_counts[ad] + count_in_playlist[ad] + incr,ad_list[ad]['count']))
            temp_2 = math.log(ubs_utility_func(ad_play_counts[ad] + count_in_playlist[ad], ad_list[ad]['count']))
            utility_gain[ad] = temp_1 - temp_2
        k = max(utility_gain, key=utility_gain.get)
        playlist.append(k)
        count_in_playlist[k] += incr
        playlist_duration += ad_list[ad]['len']
        print("playlist duration is")
        print(playlist_duration)

    return playlist


def play_video(video, folderPath):
    if video.endswith(".mp4"):
        path = os.path.join(folderPath, video)

        text_file.write("now playing: {0}\n".format(video))
        text_file.flush()
        print("\nnow playing: {0}".format(video))

        omx = subprocess.run(["omxplayer", "-o", "local", path])    # play video

def upc(video, video_points,play_counts,ad_list,coords): # could maybe make priority regions an input too
    priority_multiplier = 1
    play_multiplier = 0.2 
    if priority_zones.get(coords):
        if video in priority_zones[coords]: 
            text_file.write("in priority fence\n")
            text_file.flush()
            priority_multiplier = 1    # may not be necessary
            play_multiplier = 1
        

    new_count_utility =  math.log(ubs_utility_func(play_counts[video] + play_multiplier,ad_list[video]['count']))
    old_count_utility = math.log(ubs_utility_func(play_counts[video],ad_list[video]['count']))
    count_utility_gained = (new_count_utility - old_count_utility) * 10000 #to put things in a workable range

    video_points[video] += (count_utility_gained * priority_multiplier)
    play_counts[video] += (1 * play_multiplier)


#############################  main code #################################

#### temporarily placing the code to get minimum average time per zone. ####

location_long_map = open("TTDM/output/location_long_map", "r")
loc_long_dict = {}

for x in location_long_map:
    zone, long_z = x.split()
    loc_long_dict[zone] = long_z

graph_dict = {}
zone_min_avg_dict = {}

with open("TTDM/output/graph/Taxi_graph.csv", newline="") as taxi_graph:
    graph = csv.reader(taxi_graph, skipinitialspace=True, delimiter=' ', quotechar='|')
    number = next(graph)[0]
    graph_dict = {k: [] for k in range(1,int(number)+1)}
    zone_min_avg_dict = {k: [] for k in range(1,int(number)+1)}
    next(graph)
    for row in graph:
        graph_dict[int(row[0])].append((int(row[1]),float(row[2])))
        #if float(row[2]) >= 5: #minimum threshold          # Actual values give worse fairness.
        #    graph_dict[str(row[0]) + ">" +  str(row[1])] = float(row[2])
        #else:
        #    graph_dict[str(row[0]) + ">" + str(row[1])] = 5

for src, content in graph_dict.items():
    zone_min_avg_dict[src] = min(list(filter(lambda x: x >= 0, map(lambda x: x[1], content)))) #temp fix for negs

##########################################################################

# begin by running gps supplier
log = open('output/gpx_loc.txt', 'a+') 
proc = subprocess.Popen(["python3", "-u", "gpxplayer.py"], stdout=log)

folderPath = "/home/pi/Videos"
queue = []
nextQueue = []
video_points = {}
play_counts = {}
reqd_counts = {}
default_queue = [] # this will get modified, but will always be accessible via default_queue

next_has_prio_ads = 0
zone_has_prio_ads = 0

# setup priority zones with point counter
priority_zones_json = open('priority_zones2.json')
priority_zones = json.load(priority_zones_json)

# load ad lengths
ad_list_json = open('ad_list.json')
ad_list = json.load(ad_list_json)

for filename in os.listdir(folderPath):
    default_queue.append(filename)
    video_points[filename] = 0
    play_counts[filename] = 0

queue = default_queue.copy() #if rr we don't need to copy, since removed ad gets pushed back

print(priority_zones)
print(ad_list)

# Begin JPype and train TTDM
jpype.startJVM(classpath=['TTDM/target/classes'])
TTDM = jpype.JClass("com.mdm.sdu.mdm.model.taxi.TTDM_Taxi")
TTDM.train()

visited_list = []
last_pred = ""
update_next_queue = False 

while len(queue) > 0: # might want to revisit this condition later

    ################### current coordinates input #######################
    curr_loc = ""
    while curr_loc == "":
        with open('output/gpx_loc.txt', 'r') as f:
            curr_loc = f.readlines()[-1]
    print(curr_loc)
    parsed_loc = curr_loc.split(" ")
    lat_lon = parsed_loc[0].split(",")
    y_pos = float(lat_lon[0][1:])
    x_pos = float(lat_lon[1][0:-1])
    tim = datetime.fromisoformat(parsed_loc[1] + " " + parsed_loc[2].strip())
    tim = int(tim.timestamp()*1000)

    text_file.write("current location: {0}\n".format(curr_loc))
    text_file.flush() 

    ####################  location sequence module  ######################
    coords = convertToGrid((x_pos,y_pos))
    text_file.write("grid coords: {0}\n".format(coords))

    if len(visited_list) == 0 or visited_list[-1].split('@')[0] != coords:
        # move the queue if the sequence moved already
        if len(visited_list) != 0:
            text_file.write("clearing queue. New queue is:\n")
            text_file.flush()

            text_file.write("{0}\n".format(nextQueue))
            text_file.flush()
   
            queue = nextQueue.copy()
            nextQueue = []

        if len(visited_list) != 0 and tim - int(visited_list[-1].split('@')[1]) > (120 * 1000):
            visited_list.clear()
        visited_list.append(coords + "@" + str(tim)) 

        if next_has_prio_ads:
            zone_has_prio_ads = 1
        
        next_has_prio_ads = 0


    idx = "20000005,"
    visited_str = ",".join(visited_list)
    trajectory = jpype.java.lang.String(idx + visited_str)
    
    # predict via trajectory sequence output
    predicted = TTDM.TTDM_Instance.predictHelper(trajectory)
    text_file.write(idx + visited_str + " predicted: " + str(predicted)+"\n")
    
    ###################  Video scheduling module ###################
    
    # This is why the outer while loop may be problematic, considering setting it to just while true
    # We can consider making this depend on arg i.e. if scheduler == "rr"

     #if no next queue, or prediction changed, set to update next queue
    if not nextQueue or predicted != last_pred:
        update_next_queue = True
        

    if update_next_queue:
        #nextQueue.clear() hopefully no memory issues, but yeah garbage collect
        #tempQueue = generateNextQueue(predicted,default_queue)
        
        tempQueue = []
        if priority_zones.get(predicted):
            tempQueue = priority_zones[predicted]
        else:
            tempQueue = default_queue

        print("temp queue is")
        print(tempQueue)
        if tempQueue != default_queue:
            next_has_prio_ads = 1

        # we assume that the already scheduled playlist will finish i.e. be optimistic.
        optimistic_counts = play_counts.copy()
        
        for ad in queue:
            if zone_has_prio_ads:
                optimistic_counts[ad] += 1
            else:
                optimistic_counts[ad] += 0.2
                
        zone_time = zone_min_avg_dict[int(loc_long_dict[predicted])]
        #zone_time = graph_dict[loc_long_dict[coords] + ">" + loc_long_dict[predicted]]  #actual has worse fairness
        nextQueue = ubs(tempQueue,optimistic_counts,ad_list,zone_time,next_has_prio_ads)

        text_file.write("populated next queue (" + str(predicted) + ")  with:\n")
        text_file.write("{0}\n".format(nextQueue))
        text_file.write("based on")
        text_file.write(str(optimistic_counts) + "\n")
        text_file.flush()

        update_next_queue = False

    last_pred = predicted
        
    text_file.write("current queue: {0}\n".format(queue))
    text_file.flush()

    video = queue.pop(0)
    
    # for round robin, we can make this depend on an arg later i.e. if scheduler == "rr"
    # queue.append(video)

    play_video(video,folderPath)

    upc(video,video_points,play_counts,ad_list,coords) # Utility Point Counter

    # for UBS, generate new queue for current region if previous runs out. Moved for better accuracy
    if len(queue) == 0:
        tempQueue = []
        if priority_zones.get(coords):
            tempQueue = priority_zones[coords]
        else:
            tempQueue = default_queue

        #tempQueue = generateNextQueue(coords,default_queue)
        queue = ubs(tempQueue,play_counts,ad_list,zone_time,zone_has_prio_ads)
        
        # over prediction case - when it runs out, update next queue optimistically
        # comment out to do under prediction case
        update_next_queue = True


    #Utility and points output.

    for video in default_queue:
        text_file.write("{0}: {1} pts, {2}/{3} plays\n".format(video, video_points[video],play_counts[video],ad_list[video]['count']))
       
    vals = list(video_points.values())
    text_file.write("Util: total:{0}, mean:{1}, sd:{2}\n".format(sum(vals),np.mean(vals),np.std(vals)))
    
    vals = list(play_counts.values())
    text_file.write("Plays: total:{0}, mean:{1}, sd:{2}\n".format(sum(vals),np.mean(vals),np.std(vals)))

    text_file.write("\n")
    text_file.flush() 

text_file.close()
jpype.shutdownJVM()
