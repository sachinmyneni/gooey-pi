import threading
import time
import gps
from datetime import datetime

class GpsPoller(threading.Thread):

   def __init__(self):
       threading.Thread.__init__(self,daemon=True)
       self.session = gps.gps("localhost", "2947")
       self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
       self.current_value = None

   def get_current_value(self):
       return self.current_value

   def run(self):
       while True:
           try:
               report = self.session.next()
               if report['class'] == 'TPV':
                   if hasattr(report, 'time'):
                       print(report.time)
                   if hasattr(report, 'lon'):
                       print(report.lon)
                   if hasattr(report, 'lat'):
                       print(report.lat)
                   if hasattr(report, 'alt'):
                       print(report.alt)
                   self.current_value = report
           except KeyError:
               pass
           except KeyboardInterrupt:
               session = None
               quit()
           except StopIteration:
               session = None
               print("GPSD has terminated")
       time.sleep(1) # GPS Dongle max update frequency is 1 sec

if __name__ == '__main__':

   location_file = '/home/pi/location'+datetime.now().strftime('%Y%m%d%H%M%S')+'.txt'
   gpsp = GpsPoller()
   gpsp.start()
   gps_attribs = ['time','alt','lon','lat']
   while True:
       try:
           with open(location_file,'a+') as lf:
               result = gpsp.get_current_value()
               if all(getattr(result,attr) for attr in gps_attribs):
                   lf.write(str(result.alt)+","+str(result.lat)+","+str(result.lon)+","+str(result.time)+"\n") 
                   # In the main thread, every 5 seconds print the current value
                   print(gpsp.get_current_value())
           time.sleep(5)
       except AttributeError:
           time.sleep(2)
       except KeyboardInterrupt:
           quit()
