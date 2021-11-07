import subprocess
import os

def playVideo(path):
	omx = subprocess.run(["omxplayer", "-o", "local", path])

folderPath = "/home/pi/Videos"
queue = []

for filename in os.listdir(folderPath):
	queue.append(filename)
	
for video in queue:
	if video.endswith(".mp4"):
        	path = os.path.join(folderPath, video)
        	playVideo(path)

