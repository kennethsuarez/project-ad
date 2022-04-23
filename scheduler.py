import subprocess
import os
import json
from datetime import datetime
import math
import numpy as np
import jpype
import jpype.imports
from jpype.types import *
import csv


UPPER_LEFT_X = 120.90541
UPPER_LEFT_Y = 14.785505
DIFF_X = 0.002747
DIFF_Y = 0.002657

if not os.path.exists('output'):
    os.makedirs('output')

if not os.path.exists('state'):
    os.makedirs('state')

dt = datetime.now()

text_file = open("output/Output_{0}.txt".format(dt), "w")

dt2 = datetime.date(dt)

sf = 0
while os.path.exists("state/state_{0}_{1}.json".format(dt2,sf)):
    sf += 1


def convertToGrid(coords):
    lon, lat = coords
    x_grid = (float(lon) - UPPER_LEFT_X) // DIFF_X
    y_grid = (UPPER_LEFT_Y - float(lat)) // DIFF_Y
    return str(int(x_grid)) + "$" + str(int(y_grid))

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
            temp_1 = math.log(ubs_utility_func(ad_play_counts[ad] + count_in_playlist[ad] + incr,reqd_counts[ad]))
            temp_2 = math.log(ubs_utility_func(ad_play_counts[ad] + count_in_playlist[ad],reqd_counts[ad]))
            utility_gain[ad] = temp_1 - temp_2
        
        k = max(utility_gain, key=utility_gain.get)
        playlist.append(k)
        count_in_playlist[k] += incr
        playlist_duration += ad_list[k]['len']
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

    #print(priority_zones) 
    if priority_zones.get(coords):
        
        #print(coords + " is in pz")
        if video in priority_zones[coords]:
            text_file.write("in priority fence\n")
            text_file.flush()
            priority_multiplier = 1    # may not be necessary
            play_multiplier = 1
    #else:
    #    print(coords + " not in pz")
        
    new_count_utility =  math.log(ubs_utility_func(play_counts[video] + play_multiplier,reqd_counts[video]))
    old_count_utility = math.log(ubs_utility_func(play_counts[video],reqd_counts[video]))
    count_utility_gained = (new_count_utility - old_count_utility) * 10000 #to put things in a workable range

    video_points[video] += (count_utility_gained * priority_multiplier)
    play_counts[video] += (1 * play_multiplier)

    # boost all provisional counts when possible

    # check first if all other ads met provisional targets before boosting to prevent monopoly
    targets_met = 1
    for ad in ad_list.keys():
        if play_counts[ad] < reqd_counts[ad]:
            targets_met = 0
            
        if play_counts[ad] >= ad_list[ad]['count']:
            reqd_counts[ad] = 0 # also disable completed ads. Marker to remove priority.
                                # issue with this is it could be slow if ad list big, though
                                # shouldn't be too bad since it will be bounded.. at worst 
                                # 5760 ads that only want 1 slot.
    if targets_met:
        text_file.write("Provisional targets met\n")
        text_file.flush()
        actual_target_met = 1
        for ad in ad_list.keys():
            # if there are still more counts needed, let us move to the next
            diff = ad_list[ad]['count'] - reqd_counts[ad] 
            
            if not reqd_counts[ad]: continue # if reqd is 0 i.e. disabled, skip this step

            if diff >= 100 and reqd_counts[ad]: # non empty reqd_counts
                reqd_counts[ad] += 100
                text_file.write("provisional count for {0} is {1}\n".format(ad,reqd_counts[ad]))
                actual_target_met = 0
            elif diff > 0 and reqd_counts[ad]:
                reqd_counts[ad] += diff 
                text_file.write("provisional count for {0} is {1}\n".format(ad,reqd_counts[ad]))
                actual_target_met = 0
            #elif diff == 0:
            #    # disable the ad if its contract is done
            #    reqd_counts[ad] = 0 # will disable it since utility gain will be extremely low
            #    # we can use this 0 as a flag for when doing the priority regions stuff.

        if actual_target_met: #if actual targets met then we can restore required plays so all ads can play
            text_file.write("Real targets met\n")
            text_file.flush()
            for ad in ad_list.keys():
               reqd_counts[ad] = ad_list[ad]['count']
               
#############################  main code #################################

################################ setup ###################################

# Load location_long_map and use it to find lowest average playtimes per region

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

# begin running gps supplier
log = open('output/gpx_loc.txt', 'a+') 
proc = subprocess.Popen(["python3", "-u", "gpxplayer.py"], stdout=log)

# declare dictionaries and listsi that need initialization
folderPath = "/home/pi/Videos"
video_points = {}
play_counts = {}
reqd_counts = {}
queue = []
default_queue = [] # this will get modified, but will always be accessible via default_queue

#flags for operating mode
is_ubs = 1
predictive = 0

text_file.write("ubs: {0}, predictive: {1}\n".format(is_ubs,predictive))
text_file.flush()


# load priority zones
priority_zones_json = open('priority_zones2.json')
priority_zones = json.load(priority_zones_json)

# load ad list
ad_list_json = open('ad_list.json')
ad_list = json.load(ad_list_json)

for filename in os.listdir(folderPath):
    default_queue.append(filename) 

original_queue = default_queue.copy()

if is_ubs:
    queue = default_queue.copy()
else:
    queue = default_queue #if rr we don't need to copy, since removed ad gets pushed back

# check if there is previous state and load if necessary
if sf > 0:
    last_state_json = open("state/state_{0}_{1}.json".format(dt2,sf-1))
    last_state = json.load(last_state_json)
    video_points = last_state["video_points"]
    reqd_counts = last_state["reqd_counts"]
    play_counts = last_state["play_counts"]
    last_state_json.close()

    if not is_ubs: # check for completed ads to remove when doing rr.
        for ad in default_queue:
            if reqd_counts[ad] == 0:
                default_queue.remove(ad)
else:
    for filename in os.listdir(folderPath):
        video_points[filename] = 0
        
        if ad_list[filename]['count'] > 100:
            reqd_counts[filename] = 100 
        else:
            reqd_counts[filename] = ad_list[filename]['count']  
        
        play_counts[filename] = 0


print(priority_zones)
print(ad_list)

# Begin JPype and train TTDM
jpype.startJVM(classpath=['TTDM/target/classes'])
TTDM = jpype.JClass("com.mdm.sdu.mdm.model.taxi.TTDM_Taxi")
TTDM.train()

# declare variables to keep state in while loop
unknown_loc = 0
last_pred = ""
update_next_queue = 0
wrong_prediction = 0
next_has_prio_ads = 0
nextQueue = []
visited_list = []

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
    
    # check if in known location
    unknown_loc = 0
    if coords not in loc_long_dict:
        unknown_loc = 1
    
    # check if moved into a new zone or there are no visited areas yet
    if (len(visited_list) == 0 or visited_list[-1].split('@')[0] != coords) and predictive:
        # move the queue if the sequence moved already
        if len(visited_list) != 0:
            text_file.write("clearing queue. New queue is:\n")
            text_file.flush()

            text_file.write("{0}\n".format(nextQueue))
            text_file.flush()
            if is_ubs: 
                queue = nextQueue.copy()
            else:
                queue = nextQueue
            

            nextQueue = []
        
        # append to the visited list if it falls within the threshold
        if len(visited_list) != 0 and tim - int(visited_list[-1].split('@')[1]) > (120 * 1000):
            visited_list.clear()
        visited_list.append(coords + "@" + str(tim)) 
    
        # check if the prediction was wrong
        if last_pred != coords:
            wrong_prediction = 1

    predicted = ""
   
    # predict via trajectory sequence output if known location.
    if not unknown_loc and predictive:
        idx = "20000005,"
        visited_str = ",".join(visited_list)
        trajectory = jpype.java.lang.String(idx + visited_str)
    
        predicted = TTDM.TTDM_Instance.predictHelper(trajectory)
        text_file.write(idx + visited_str + " predicted: " + str(predicted)+"\n")
    elif predictive:
        visited_list.clear() # cannot have unknown loc in visited list or TTDM will break.
        text_file.write("New location with no history: " + str(coords) + "\n")


    ###################  Video scheduling module ###################

    # if no next queue, or prediction changed, set to update next queue
    if (not nextQueue or predicted != last_pred) and predictive:
        update_next_queue = 1

    if update_next_queue and predictive:
        #nextQueue.clear() hopefully no memory issues, but yeah garbage collect
        
        # get what ads can be scheduled for the zone
        tempQueue = []
        if priority_zones.get(predicted):
            tempQueue = priority_zones[predicted].copy()
            for ad in tempQueue:
                if reqd_counts[ad] == 0: # this removes already completed ads
                    tempQueue.remove(ad)
        
        if len(tempQueue) == 0:
            next_has_prio_ads = 0
            tempQueue = default_queue
        else:
            next_has_prio_ads = 1


        print("temp queue is")
        print(tempQueue)

        # we assume that the already scheduled playlist will finish i.e. be optimistic.
        
        optimistic_counts = {}
        if is_ubs:
            optimistic_counts = play_counts.copy()
            
            for ad in queue:
                if coords in priority_zones:
                    if ad in priority_zones[coords]:
                        optimistic_counts[ad] += 1
                else:
                    optimistic_counts[ad] += 0.2
            
            # if there is no known zone time, set to 60s
            if not unknown_loc:
                zone_time = zone_min_avg_dict[int(loc_long_dict[predicted])]
            else:
                zone_time = 60
            #zone_time = graph_dict[loc_long_dict[coords] + ">" + loc_long_dict[predicted]]   #actually less fair
        
            # generate next playlist
            nextQueue = ubs(tempQueue,optimistic_counts,ad_list,zone_time,next_has_prio_ads)
            next_has_prio_ads = 0
        else:
            if next_has_prio_ads:
                nextQueue = tempQueue.copy()
            else:
                nextQueue = default_queue

        text_file.write("populated next queue (" + str(predicted) + ")  with:\n") #technically wrong for LSRR when nextQueue is defaultQueue
        text_file.write("{0}\n".format(nextQueue))
        if is_ubs:
            text_file.write("based on")
            text_file.write(str(optimistic_counts) + "\n")
            text_file.flush()

        update_next_queue = 0

    if predictive: 
        last_pred = predicted
        
    text_file.write("current queue: {0}\n".format(queue))
    text_file.flush()

    video = queue.pop(0)
    
    play_video(video,folderPath)
    print("upc gets " + coords)

    old_reqd_count = reqd_counts[video]
    upc(video,video_points,play_counts,ad_list,coords) # Utility Point Counter

    new_ad_done =  old_reqd_count != 0 and reqd_counts[video] == 0
    
    # Special rules for updating current queue
    if is_ubs:
        # for UBS, generate new queue when needed
        
        if len(queue) == 0 or wrong_prediction or new_ad_done: 
            
            # Get the list of ads that can be scheduled
            tempQueue = []
            if priority_zones.get(coords) and predictive: #only do the zone thing if predictive
                tempQueue = priority_zones[coords]
                for ad in tempQueue:
                    if reqd_counts[ad] == 0:
                        tempQueue.remove(ad) 

            if len(tempQueue) == 0:
                tempQueue = default_queue

            # Check the zone time of the current zone
            zone_time  = 0
            if not unknown_loc and predictive:
                zone_time = zone_min_avg_dict[int(loc_long_dict[coords])]
            else: # unknown location or we don't care about locations cause not predictive
                zone_time = 60

            #tempQueue = generateNextQueue(coords,default_queue)

            # has_prio only relevant in predictive
            queue = ubs(tempQueue,play_counts,ad_list,zone_time,coords in priority_zones and predictive)
            if wrong_prediction:
                text_file.write("current queue update due to wrong prediction\n")

            if len(queue) == 0:
                text_file.write("current queue update due to running out\n")

            if new_ad_done:
                text_file.write("current queue update due to new ad completion\n")
                # sort of dangerous, given that it optimistic counts could be hurt?

            text_file.flush() 
            
            # over prediction case - when it runs out, update next queue optimistically
            # comment out to do under prediction case
            wrong_prediction = 0 # clear cause queue already refreshed
            
            #if not new_ad_done: # if a new ad finishes, don't update next. Actually wrong.
            #    update_next_queue = 1                                      An ad could be 
            #next_has_prio_ads = 0                                          eliminated
    else: # rr
        if not new_ad_done:
            queue.append(video) # return to queue only if it isn't done.
        else: 
            if len(queue) == 0: # if the last ad played is done and the queue has become empty
                queue = default_queue # if already default_queue doesn't change anything 

            # Ensure video is also removed from default queue, for when the ad finishes in zone
            if video in default_queue:
                default_queue.remove(video)

            if len(default_queue) == 0: # this means all ads are satisfied
                default_queue = original_queue.copy()

        if predictive and wrong_prediction:
            tempQueue = [] 
            if priority_zones.get(coords): # has priority ads
                tempQueue = priority_zones[coords].copy()
                for ad in tempQueue:
                    if reqd_counts[ad] == 0:
                        tempQueue.remove(ad) 
            if len(tempQueue) == 0: 
                queue = default_queue
            else:
                queue = tempQueue

    #Utility and points output.

    for video in original_queue:
        text_file.write("{0}: {1} pts, {2}/{3} plays\n".format(video, video_points[video],play_counts[video],ad_list[video]['count']))
       
    vals = list(video_points.values())
    text_file.write("Util: total:{0}, mean:{1}, sd:{2}\n".format(sum(vals),np.mean(vals),np.std(vals)))
    
    vals = list(play_counts.values())
    text_file.write("Plays: total:{0}, mean:{1}, sd:{2}\n".format(sum(vals),np.mean(vals),np.std(vals)))

    text_file.write("\n")
    text_file.flush()

    state_file = open("state/state_{0}_{1}.json".format(dt2,sf), "w")
    video_points_str = json.dumps(video_points)
    play_counts_str = json.dumps(play_counts)
    reqd_counts_str = json.dumps(reqd_counts)
    state_file.write("{{\"video_points\":{0}, \"play_counts\":{1}, \"reqd_counts\": {2}}}".format(video_points_str,play_counts_str,reqd_counts_str))
    state_file.close()

text_file.close()
jpype.shutdownJVM()
