#!/usr/bin/env python3

from __future__ import print_function

import os
import sys
import string
from papirus import Papirus
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep
import RPi.GPIO as GPIO
from datetime import datetime
import threaded_get_gps_from_port as tggp
import threading

def collect_gps(papirus,SIZE):
    # thread to open a new file, start writing and spawn the
    # other thread to collect gps data from the port.
    # Start tracking.
    write_text(papirus, "Beginning tracking...", SIZE)
    location_file = '/home/pi/location'+datetime.now().strftime('%Y%m%d%H%M%S')+'.txt'
    gpsp = tggp.GpsPoller()
    gpsp.start()
    gps_attribs = ['time','alt','lon','lat']
    while True:
        try:
            with open(location_file,'a+') as lf:
                result = gpsp.get_current_value()
                if all(getattr(result,attr) for attr in gps_attribs):
                    lf.write(str(result.alt)+","+str(result.lat)+","+str(result.lon)+","+str(result.time)+"\n") 
                    # In the main thread, every 5 seconds print the current value
                    sleep(5)
        except AttributeError:
             sleep(2)
        except KeyboardInterrupt:
             quit()


# Check EPD_SIZE is defined
EPD_SIZE=0.0
if os.path.exists('/etc/default/epd-fuse'):
    exec(open('/etc/default/epd-fuse').read())
if EPD_SIZE == 0.0:
    print("Please select your screen size by running 'papirus-config'.")
    sys.exit()

# Running as root only needed for older Raspbians without /dev/gpiomem
if not (os.path.exists('/dev/gpiomem') and os.access('/dev/gpiomem', os.R_OK | os.W_OK)):
    user = os.getuid()
    if user != 0:
        print('Please run script as root')
        sys.exit()

# Command line usage
# papirus-buttons

hatdir = '/proc/device-tree/hat'

WHITE = 1
BLACK = 0

SIZE = 27

# Assume Papirus Zero
SW1 = 21
SW2 = 16
SW3 = 20 
SW4 = 19
SW5 = 26

# Check for HAT, and if detected redefine SW1 .. SW5
if (os.path.exists(hatdir + '/product')) and (os.path.exists(hatdir + '/vendor')) :
   with open(hatdir + '/product') as f :
      prod = f.read()
   with open(hatdir + '/vendor') as f :
      vend = f.read()
   if (prod.find('PaPiRus ePaper HAT') == 0) and (vend.find('Pi Supply') == 0) :
       # Papirus HAT detected
       SW1 = 16
       SW2 = 26
       SW3 = 20
       SW4 = 21
       SW5 = -1

def main(argv):
    global SIZE

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(SW1, GPIO.IN)
    GPIO.setup(SW2, GPIO.IN)
    GPIO.setup(SW3, GPIO.IN)
    GPIO.setup(SW4, GPIO.IN)
    if SW5 != -1:
        GPIO.setup(SW5, GPIO.IN)

    papirus = Papirus(rotation = int(argv[0]) if len(sys.argv) > 1 else 0)


    # Use smaller font for smaller displays
    if papirus.height <= 96:
        SIZE = 12

    papirus.clear()

    write_text(papirus, "Ready... 1 + 2 to exit.\n1 to start GPS\n2 to stop GPS\n4 to restart\n5 to shutdown", SIZE)
    TRACKING = False
    while True:
        # Exit when SW1 and SW2 are pressed simultaneously
        if (GPIO.input(SW1) == False) and (GPIO.input(SW2) == False) :
            write_text(papirus, "Exiting ...", SIZE)
            sleep(0.2)
            papirus.clear()
            sys.exit()

        if GPIO.input(SW1) == False:
            if TRACKING:
                 write_text(papirus, "GPS already logging.\nPress 2 to stop", SIZE)
            else:
                 # Start tracking
                 g = threading.Thread(target=collect_gps,args=(papirus,SIZE,),daemon=True)
                 g.start() 
                 TRACKING = True
        if GPIO.input(SW2) == False:
            if TRACKING:
                 # Stop tracking
                 g.join() 
                 write_text(papirus, "Tracking ended.", SIZE)
            else:
                 write_text(papirus, "No current GPS logging.\nPress 1 to start", SIZE)
        if GPIO.input(SW3) == False:
            write_text(papirus, "Three", SIZE)

        if GPIO.input(SW4) == False:
            write_text(papirus, "Rebooting...", SIZE)
            os.system("sudo reboot") 

        if (SW5 != -1) and (GPIO.input(SW5) == False):
            write_text(papirus, "Shutting Down at\n" + str(datetime.now()), SIZE)
            os.system("sudo shutdown now -h") 
 
        sleep(0.1)

def write_text(papirus, text, size):

    # initially set all white background
    image = Image.new('1', papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', size)

    # Calculate the max number of char to fit on line
    line_size = (papirus.width / (size*0.65))

    current_line = 0
    text_lines = [""]

    # Compute each line
    for word in str(text).split():
        # If there is space on line add the word to it
        if (len(text_lines[current_line]) + len(word)) < line_size:
            text_lines[current_line] += " " + word
        else:
            # No space left on line so move to next one
            text_lines.append("")
            current_line += 1
            text_lines[current_line] += " " + word

    current_line = 0
    for l in text_lines:
        current_line += 1
        draw.text( (0, ((size*current_line)-size)) , l, font=font, fill=BLACK)

    papirus.display(image)
    papirus.partial_update()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit('interrupted')

