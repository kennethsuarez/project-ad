import subprocess
import os
import json

KFC_fence = [(120.99726, 14.55372), (120.99833, 14.55434)]

def checkGeoFence(point, x_pos, y_pos):
    x1, y1 = point
    if ((x1 < x_pos < x1+0.002747) and (y1-0.002657 < y_pos < y1)):
        print("now inside priority  fence")
        return True
    return False
    

# round robin player
def playVideo(queue, folderPath, video_points, x_pos, y_pos):
    print("current queue: {0}".format(queue))
    video = queue.pop(0)    # remove from queue

    if video.endswith(".mp4"):
        path = os.path.join(folderPath, video)

        video_points[video] += 1    # increment point before playing
        for priority_zone in priority_zones[video]:
            if (checkGeoFence(priority_zone, x_pos, y_pos)):
                video_points[video] += 2    # add extra point for geo-fenced locations
                break

        print("now playing: {0}".format(video))
        omx = subprocess.run(["omxplayer", "-o", "local", path])    # play video

        queue.append(video)     # add played video to end of queue

    for video in queue:
        print("{0}: {1} points".format(video, video_points[video]))

    print()


# begin by running gps supplier
proc = subprocess.Popen(["python3", "-u", "gpxplayer.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

folderPath = "/home/pi/Videos"
queue = []
video_points = {}
priority_zones = {}

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


while len(queue) > 0:
    curr_loc = proc.stdout.readline().decode("utf-8")
    parsed_loc = curr_loc.split(" ")
    lon_lan = parsed_loc[0].split(",")
    y_pos = lon_lan[0][1:]
    x_pos = lon_lan[1][0:-1]
    print(y_pos)
    print("current location: {0}".format(curr_loc))
    playVideo(queue, folderPath, video_points, float(x_pos), float(y_pos))

