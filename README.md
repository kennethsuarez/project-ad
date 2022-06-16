# A Location Sensitive and Utility Based Advertising System for Public Transport

# Abstract from the research paper
The increasing use of computers in vehicles presents an opportunity
to harness data in ways that create value for public transport systems.
In this paper we propose an advertising system that makes use of current
location information and historical data to present ads relevant to a location,
subject to the feasibility of the proposed ad allocation. The scheduling of
ads is done in a way that prioritizes fairness, by assuming that less often
played ads provide more utility when played than ads that have already been
played often, and that ads played in their priority zones count towards more
plays than ads played outside their priority regions. On the other hand,
determining whether to accept requests for advertising allocations is done
by estimating the ad play time available in a day, and then estimating based
on statistics if the ad request is likely to be satisfied given the ad priority
zones and the amount of time remaining. Experiment results show that
the proposed algorithm for scheduling ads is a good compromise between
utility gained and fairness. On the other hand, the ad allocation algorithm’s
performance is dependent on determining the correct parameters for the
algorithm, but still works better than simply allocating based on the worst
case, since the amount of time used by the ad allocations is closer to the
actual available time.

# Requirements
python3
JPype
Java SDK 15
omxplayer

# How to get started

Run ad allocation by running the following command
```
python3 ad_allocation.py
```

Refer to `index.html` to view a grid in the coordinates system.

Run the scheduler file by using the following command

```
python3 scheduler.py
```

Currently, the GPS coordinates supplied are from a previously generated set, but can easily be adapted to handle real time data by changing where input is read from, moving it from a file to the output of the gps device consistent with gpx files.

After specifying a path folder containing the videos, the scheduler feeds the videos to a queue depending on the scheduling options selected, by the flags `is_ubs` and `predictive`, with the first being to select between round robin and utility based scheduling, and the latter for location sensitivity.

Coordinates based on a time function are run in parallel with the video scheduler though the following command
```
proc = subprocess.Popen(["python3", "-u", "gpxplayer.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
```

Before playing a video, the running process checks first if the user is currently located inside a priority zone. If located inside a point of interest, the played video is given 1 point; otherwise it is given 0.2, as stated in the research paper.

Output is logged to a file and can be viewed while the scheduler is running. Additionally, a state file is saved to resume running in case it gets interrupted in a day.
