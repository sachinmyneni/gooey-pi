import time
import gps
from datetime import datetime
import random

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
location_file = '/home/pi/location'+datetime.now().strftime('%Y%m%d%H%M%S')+'.txt'
random.seed()

while True:
    try:
        report = session.next()
        # Wait for a 'TPV' report and display the current time
        # To see all report data, uncomment the line below
        #print(report)
        if report['class'] == 'TPV':
            if hasattr(report, 'time'):
                print(report.time)
            if hasattr(report, 'lon'):
                print(report.lon)
            if hasattr(report, 'lat'):
                print(report.lat)
            if hasattr(report, 'alt'):
                print(report.alt)
            with open(location_file,'a+') as lf:
                lf.write(str(report.alt)+","+str(report.lat)+","+str(report.lon)+","+str(report.time)+"\n") 
            time.sleep(random.randint(1,6))
    except KeyError:
        pass
    except KeyboardInterrupt:
        quit()
    except StopIteration:
        session = None
        print("GPSD has terminated")
