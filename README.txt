rpi.weatherstation.lite
================
This python script is designed to run as a service on a Raspberry Pi that has a SenseHAT installed.  It is designed to run in conjunction with Kodi running a modified version of the Estuary skin with a companion addon called script.weatherstation.lite.  Together they provide a clock/weather station system based on the Raspberry Pi platform.  Information about the complete setup will be available later on the wiki for this repo.

This script provides a few functions:
1. read the temperature, humidity, and pressure from the SenseHat and write it to a file
2. Handle messages sent from Kodi for screen control (brightness and auto dim status)
3. Set the brightness, and screen on/off based on triggers (dark, light) or times (including sunrise, sunset)


PREREQUISITES:
1. Optimally you should be running Raspian Jessie or later, as it has all the SenseHAT and touchscreen modules and most of the python bindings already included.  If you're running something older, you'll have to run the script, see what imports don't work, and download python modules as needed.

2. You need to use Python 2.7.x for this.  3.x will not work, as I know I'm using at least one 2.7.x function (to reload the settings) that isn't available any longer in Python 3.x.

3. For rpi.weatherstation.lite to function properly, there are some modules you need to install:
From a terminal window:
pip install websocket-client		(to communicate with Kodi)
pip install rpi-backlight			(to control the RPi Touchscreen)

4. If you have the RPi camera, it can be used to detect light levels.  The Camera must be plugged in and turned on in raspi-config.

5. If you are using the official RPi 7" touchscreen you need to also edit the backlight rules.
From a terminal window:
sudo nano /etc/udev/rules.d/backlight-permissions.rules

and add:
SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power"

Then reboot.


INSTALLATION:
It is recommended you install this in /home/pi.  The Kodi companion addon assumes this is where the script is by default, so if you install it somewhere else, you'll need to point Kodi to the correct location.


CONFIGURATION:
You can run this without further configuration.  If you want to see all how all the settings are set by default, you can look at settings-example.py.  If you want to change any of the defaults, you can either create a new file called settings.py and copy and paste the specific setting(s) you want to change from settings-example.py OR you can copy settings-example.py to settings.py and edit that file.

ABOUT AUTO DIMMING:
Auto dimming allows you to do certain actions based on given triggers or times.  Auto dim understands special triggers and time based triggers.  There are two special triggers: dark, light (these require a functioning RPi camera to do anything).  You can change the light level thresholds if needed.  Time triggers can accept any 24 hour formatted time as well as the keywords Sunrise and Sunset (those times are provided by Kodi via one of its weather plugins).  Time triggers can also be set to run only on weekdays or the weekend.  See settings-example.py for the exact format for timed triggers.


USAGE:
To run from the terminal (for testing): python /home/pi/rpi.sensehat.mon/execute.py
To exit: CNTL-C

Running from the terminal is useful during initial testing.  Once you know it's working the way you want, you should set it to autostart.  To do that:
From a terminal window:
nano /home/pi/.config/lxsession/LXDE-pi/autostart

and add:
@python /home/pi/rpi.weatherstation.lite/execute.py &

Save and exit.  From now on the python script will start after the Raspian desktop loads.  You can change settings by editing the settings.py file any time you'd like.  The script will reload the settings automatically.  No need to stop/start the script (unless otherwise noted in the settings file).