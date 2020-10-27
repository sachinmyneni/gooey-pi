# sudo apt-get install libgeos-dev
# python3 -m pip install gps3 pytz tzwhere

from gps3 import agps3
from time import sleep
import datetime as dt
import pytz
from tzwhere import tzwhere
import logging

def get_loc_time():
    gps_socket = agps3.GPSDSocket()
    data_stream = agps3.DataStream()
    gps_socket.connect()
    gps_socket.watch()
    for new_data in gps_socket:
        if new_data:
            data_stream.unpack(new_data)
            if data_stream.alt != 'n/a':
                logging.debug('Altitude = ', data_stream.alt)
                logging.debug('Latitude = ', data_stream.lat)
                logging.debug('Longitude = ', data_stream.lon)
                logging.debug('Time (UTC) = ', data_stream.time)
                tzhere = tzwhere.tzwhere()
                timezone_str = tzhere.tzNameAt(data_stream.lat, data_stream.lon)
                print(timezone_str)
                return({'Alt':data_stream.alt,'Lat':data_stream.lat,'Lon':data_stream.lon,'Time':data_stream.time})
            else:
                sleep(1)

if __name__ == "__main__":

    DEFAULT_LOG_LEVEL=logging.WARNING 
    logging.basicConfig(level=DEFAULT_LOG_LEVEL,format='[{asctime}:{filename}:{lineno}] {msg}',style="{")
    get_loc_time()
