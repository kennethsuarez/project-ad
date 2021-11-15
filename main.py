#!/usr/bin/python3
import gps
from datetime import datetime

file1 = open("gpslog.txt","a")

session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

file1.write(f'gpstest started at {datetime.now()} \n')
file1.close()

while True:
    try:
        report = session.next()
        if report['class'] == 'TPV':
            if hasattr(report, 'time') and hasattr(report, 'lat') and hasattr(report, 'lon'):
                file1 = open("gpslog.txt","a")
                file1.write(f'time: {report.time}, lat: {report.lat}, lon: {report.lon}\n')
                file1.close()
    except KeyError:
        pass
    except KeyboardInterrupt:
        quit()
    except StopIteration:
        session = None
        print("GPSD has terminated")
