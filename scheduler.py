import subprocess
import os
import json
from datetime import datetime
import time

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
    

# round robin player
def playVideo(queue, folderPath, video_points, x_pos, y_pos):
    text_file.write("current queue: {0}\n".format(queue))
    text_file.flush()
    video = queue.pop(0)    # remove from queue

    if video.endswith(".mp4"):
        path = os.path.join(folderPath, video)

        video_points[video] += 1    # increment point before playing
        for priority_zone in priority_zones[video]:
            if (checkGeoFence(priority_zone, x_pos, y_pos)):
                video_points[video] += 2    # add extra point for geo-fenced locations
                break

        text_file.write("now playing: {0}\n".format(video))
        text_file.flush()

        omx = subprocess.run(["omxplayer", "-o", "local", path])    # play video

        queue.append(video)     # add played video to end of queue

    for video in queue:
        text_file.write("{0}: {1} points\n".format(video, video_points[video]))
        text_file.flush()

    text_file.write("\n")
    text_file.flush()

# main code
# begin by running gps supplier
proc = subprocess.Popen(["python3", "-u", "gpxplayer.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

folderPath = "/home/pi/Videos"
queue = []
video_points = {}
priority_zones = {}


# setup priority zones with point counter
priority_zones_json = open('priority_zones.json')
priority_zones_data = json.load(priority_zones_json)

for filename in os.listdir(folderPath):
    queue.append(filename)
    # start counter for each file
    video_points[filename] = 0
    priority_zones[filename] = []

for ad in priority_zones_data['ads']: 
    for zone in ad['zones']:
        priority_zones[ad['name']].append((zone['lat'],zone['lon']))

print(priority_zones)

# setup and read visited coordinates
OUTPUT_PATH = 'output/visited.txt'
if not os.path.exists('output'):
    os.makedirs('output')

while len(queue) > 0:
    curr_loc = proc.stdout.readline().decode("utf-8")
    parsed_loc = curr_loc.split(" ")
    lon_lan = parsed_loc[0].split(",")
    y_pos = float(lon_lan[0][1:])
    x_pos = float(lon_lan[1][0:-1])
    tim = datetime.fromisoformat(parsed_loc[1] + " " + parsed_loc[2].strip())
    tim = int(tim.timestamp()*1000)

    text_file.write("current location: {0}\n".format(curr_loc))
    text_file.flush() 
    # predict next location
    x_grid =  (x_pos - UPPER_LEFT_X) // DIFF_X
    y_grid =  (UPPER_LEFT_Y - y_pos) // DIFF_Y
    coords = str(int(x_grid)) + "$" + str(int(y_grid)) + "@" + str(tim)
    with open(OUTPUT_PATH, 'a+') as visited_list:
        visited_list.write(coords + '\n')
    pred = subprocess.Popen(["python3", "-u", "JPypeTest.py"], stdout=subprocess.PIPE)
    predicted = pred.stdout.readline().decode("utf-8")
    text_file.write(predicted+"\n")
    # play video
    playVideo(queue, folderPath, video_points, float(x_pos), float(y_pos))

text_file.close()
