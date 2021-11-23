import subprocess
import os

# round robin player
def playVideo(queue, folderPath, video_points, x_pos, y_pos):
    print("current queue: {0}".format(queue))
    video = queue.pop(0)    # remove from queue

    if video.endswith(".mp4"):
        path = os.path.join(folderPath, video)

        video_points[video] += 1    # increment point before playing
        if(x_pos > 14.553762 and x_pos < 14.554302):
            print("located inside x pos")
            video_points[video] += 2    # add extra point for geo-fenced locations

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

for filename in os.listdir(folderPath):
    queue.append(filename)
    # start counter for each file
    video_points[filename] = 0
	
while len(queue) > 0:
    curr_loc = proc.stdout.readline().decode("utf-8")
    parsed_loc = curr_loc.split(" ")
    lon_lan = parsed_loc[0].split(",")
    x_pos = lon_lan[0][1:]
    print(x_pos)
    print("current location: {0}".format(curr_loc))
    playVideo(queue, folderPath, video_points, float(x_pos), 0)

