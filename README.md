# ARANGKADATA Project ADJudicate

# About Project
ADjucate is an advertisement platform for advertisers and modernized PUVs operators that provides ads based on location and other available information, improving cost efficiency of ads and making transport more friendly with informative announcements

# Requirements
omxplayer

# How to get started
[Refer to scheduler branch for most updated version]

Run the scheduler file by using the following command
```
python3 scheduler.py
```
Currently, the GPS coordinates supplied are from a previously generated set. 
As the project moves on to real time data, the main.py file will be run which contains instructions on how to run the gps module

# How the code works

Specified a path folder containing the videos, the scheduler feeds the videos to a queue in a Round-Robin fashion.

Coordinates based on a time function are run in parallel with the video scheduler though the following command
```
proc = subprocess.Popen(["python3", "-u", "gpxplayer.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
```

Before playing a video, the running process checks first if the user is currently located inside a geo-fence. If located inside a point of interest, the first video in the queue is given an additional point.
