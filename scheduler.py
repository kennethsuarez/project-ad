import subprocess
import os

# round robin player
def playVideo(queue, folderPath, video_points):
    print("current queue: {0}".format(queue))
    video = queue.pop(0)    # remove from queue

    if video.endswith(".mp4"):
        path = os.path.join(folderPath, video)

        print("now playing: {0}".format(video))
        omx = subprocess.run(["omxplayer", "-o", "local", path])    # play video

        queue.append(video)     # add played video to end of queue
        video_points[video] += 1    # increment point of video

    for video in queue:
        print("{0}: {1} points".format(video, video_points[video]))

    print()


folderPath = "/home/pi/Videos"
queue = []
video_points = {}

for filename in os.listdir(folderPath):
    queue.append(filename)
    # start counter for each file
    video_points[filename] = 0
	
while len(queue) > 0:
    playVideo(queue, folderPath, video_points)

