import subprocess
import os
import json
from datetime import datetime
import time
import math
import jpype
import jpype.imports
from jpype.types import *
import csv
import functools


text_file = open("Output.txt", "w")
UPPER_LEFT_X = 120.90541
UPPER_LEFT_Y = 14.785505
DIFF_X = 0.002747
DIFF_Y = 0.002657

def checkGeoFence(point, x_pos, y_pos):
    x1, y1 = point
    if ((x1 < x_pos < x1+0.002747) and (y1-0.002657 < y_pos < y1)):
        text_file.write("now inside priority fence\n")
        text_file.flush()
        return True
    return False

def convertToGrid(coords):
    lon, lat = coords
    x_grid = (float(lon) - UPPER_LEFT_X) // DIFF_X
    y_grid = (UPPER_LEFT_Y - float(lat)) // DIFF_Y
    return str(int(x_grid)) + "$" + str(int(y_grid))

def getAllAdsInZone(zone):
    ads = []
    for ad, ad_zones in priority_zones.items():
        if zone in map(convertToGrid, ad_zones):
            ads.append(ad)
    return ads

def generateNextQueue(pred_loc,default_ad_list):
    ads = getAllAdsInZone(pred_loc)
    if not ads: #empty, did not get any
        return default_ad_list
    temp = []
    for file_name in ads:
        temp.append(file_name)
    return temp

def ubs_utility_func(count_t,count):
    lambda_a = 1000 # not yet sure
    theta_a = 0 # not yet sure
    gamma_a = 0.00015 # from the paper
    return lambda_a * ((1/(1+math.e ** (-gamma_a*(count_t-count))))-theta_a)

def ubs(ad_list,ad_play_counts,ad_reqd_counts,ad_lengths,time,has_prio):
    playlist = []
    incr = 0.2
    if has_prio:
        incr = 1

    count_in_playlist = {}          
    for ad in ad_list:              
        count_in_playlist[ad] = 0
        
    playlist_duration = 0

    while playlist_duration < time:
        utility_gain = {}
        for ad in ad_list:
            utility_gain[ad] = 0
    
        for ad in ad_list:
            temp_1 = math.log(ubs_utility_func(ad_play_counts[ad] + count_in_playlist[ad] + incr,ad_reqd_counts[ad]))
            temp_2 = math.log(ubs_utility_func(ad_play_counts[ad] + count_in_playlist[ad], ad_reqd_counts[ad]))
            utility_gain[ad] = temp_1 - temp_2
        k = max(utility_gain, key=utility_gain.get)
        playlist.append(k)
        count_in_playlist[k] += incr
        playlist_duration += ad_lengths[ad]

    return playlist


def play_video(video, folderPath):
    if video.endswith(".mp4"):
        path = os.path.join(folderPath, video)

        text_file.write("now playing: {0}\n".format(video))
        text_file.flush()

        omx = subprocess.run(["omxplayer", "-o", "local", path])    # play video

def upc(video, video_points,play_counts,reqd_counts,x_pos, y_pos): # could maybe make priority regions an input too
    priority_multiplier = 1
    play_multiplier = 0.2 #arbitrary, 1 play outside zone is just equivalent to 0.2 plays
    for priority_zone in priority_zones[video]:
            # temporary fix, but better if the priority zones are in the grid format to begin with
            if convertToGrid((x_pos, y_pos)) == convertToGrid(priority_zone): 
                text_file.write("in priority fence\n")
                text_file.flush()
                priority_multiplier = 3    # We need to decide on how much of a premium this gives
                play_multiplier = 1
                break
    
    new_count_utility =  math.log(ubs_utility_func(play_counts[video] + play_multiplier,reqd_counts[video]))
    old_count_utility = math.log(ubs_utility_func(play_counts[video],reqd_counts[video]))
    count_utility_gained = (new_count_utility - old_count_utility) * 10000 #to put things in a workable range, but need to read the study more

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

for src, content in graph_dict.items():
    zone_min_avg_dict[src] = min(list(map(lambda x: x[1], content)))

##########################################################################



# begin by running gps supplier
proc = subprocess.Popen(["python3", "-u", "gpxplayer.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

folderPath = "/home/pi/Videos"
queue = []
nextQueue = []
video_points = {}
play_counts = {}
reqd_counts = {}
ad_lengths = {}
priority_zones = {}
default_queue = [] #this will get modified, but will always be accessible via default_queue

next_has_prio_ads = 0
zone_has_prio_ads = 0

# setup priority zones with point counter
priority_zones_json = open('priority_zones.json')
priority_zones_data = json.load(priority_zones_json)

for filename in os.listdir(folderPath):
    default_queue.append(filename)
    # start counter for each file
    video_points[filename] = 0
    play_counts[filename] = 0
    reqd_counts[filename] = 100 #temp value, should come from ad list later on
    # How do we handle required play counts??? total, or in zone? Damn there's so much to consider
    # we need a metric, like maybe how many equivalent play counts would it be in/out of the zone?

    ad_lengths[filename] = 6.0 # ^
    priority_zones[filename] = []

queue = default_queue.copy() #if rr we don't need to copy, since removed ad gets pushed back

reqd_counts['kfc.mp4'] = 100

for ad in priority_zones_data['ads']:
    for zone in ad['zones']:
        priority_zones[ad['name']].append((zone['lat'],zone['lon'])) #should really be lon lat but I got them flippined in priority file

print(priority_zones)
print(getAllAdsInZone("33$87"))
# setup and read visited coordinates
OUTPUT_PATH = 'output/visited.txt'
if not os.path.exists('output'):
    os.makedirs('output')

# Begin JPype and train TTDM
jpype.startJVM(classpath=['TTDM/target/classes'])
TTDM = jpype.JClass("com.mdm.sdu.mdm.model.taxi.TTDM_Taxi")
TTDM.train()

# Empty initial sequence
visited_list = []
last_pred = ""



while len(queue) > 0: # might want to revisit this condition later

    ################### current coordinates input #######################

    curr_loc = proc.stdout.readline().decode("utf-8")
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
   
            queue = nextQueue #hopefully no memory issues with this? garbage collected anyway

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

    # will need more modifications again, need to consider that UBS could create a queue that is not enough for the time.
    # This is why the outer while loop may be problematic, considering setting it to just while true
    
    # we can consider making this depend on arg i.e. if scheduler == "rr"

    #if no next queue, or prediction changed, generate a new next queue.
    if not nextQueue or predicted != last_pred:
        #nextQueue.clear() hopefully no memory issues, but yeah garbage collect
        tempQueue = generateNextQueue(predicted,default_queue) 
        if tempQueue != default_queue:
            next_has_prio_ads = 1

        # we assume that the already scheduled playlist will finish i.e. be optimistic.
        # optimistic allocator - this means we need accurate predictions for better performance.
        optimistic_counts = play_counts.copy()
        
        for ad in queue:
            if zone_has_prio_ads:
                optimistic_counts[ad] += 1
            else:
                optimistic_counts[ad] += 0.2
                
        zone_time = zone_min_avg_dict[int(loc_long_dict[predicted])]
        nextQueue = ubs(tempQueue,optimistic_counts,reqd_counts,ad_lengths,zone_time,next_has_prio_ads) # 60  is a temp value, connect it up
        # not sure if it is still close to optimal if we delay it per zone, will need to investigate

        text_file.write("populated next queue (" + str(predicted) + ")  with:\n")
        text_file.flush()

        text_file.write("{0}\n".format(nextQueue))
        text_file.flush()

    last_pred = predicted
        
    # play video via scheduler output
    
    text_file.write("current queue: {0}\n".format(queue))
    text_file.flush()

    # get the top from the queue
    video = queue.pop(0)
    
    # this is for round robin, we can make this depend on an arg later i.e. if scheduler == "rr"
    #queue.append(video)

    # this is for UBS
    if len(queue) == 0:
        tempQueue = generateNextQueue(coords,default_queue)
        queue = ubs(tempQueue,play_counts,reqd_counts,ad_lengths,zone_time,zone_has_prio_ads)

    play_video(video,folderPath)

    #################   Utility Point Counter   ####################
    upc(video,video_points,play_counts,reqd_counts,float(x_pos),float(y_pos)) #utility and play counts

    for video in default_queue:
        text_file.write("{0}: {1} pts, {2}/{3} plays\n".format(video, video_points[video],play_counts[video],reqd_counts[video]))
        text_file.flush()

    text_file.write("\n")
    text_file.flush() 

text_file.close()
jpype.shutdownJVM()
