rpi.weatherstation.lite
================
This python script is designed to run as a service on a Raspberry Pi that has a SenseHAT installed.  It provides a few functions:
1. read the temperature, humidity, and pressure from the SenseHat and write it to a file
2. Handle messages sent from Kodi for screen control (brightness and auto dim status)
3. Turn the offical RPi touchscreen on or off on a schedule

The auto dimming in in #2 and #3 have to be enabled in the settings.


Prerequisites:
1. Optimally you should be running Raspian Jessie or later, as it has all the SenseHAT and touchscreen modules and most of the python bindings already included.  If you're running something older, you'll have to run the script, see what imports don't work, and download python modules as needed.

2. You should use Python 2.7.x for this. (3.4.x might work, but I haven't tested it).

3. For rpi.weatherstation.lite to function properly, there are some modules you need to install:
From a terminal window:	pip install websocket-client		(to communicate with Kodi)
						pip install rpi-backlight			(to control the RPi Touchscreen)

4. If you are using the official RPi 7" touchscreen you need to also edit the backlight rules.
From a terminal window:	sudo nano /etc/udev/rules.d/backlight-permissions.rules
and add:				SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power"

Then reboot.


Installation:
It is recommended you install this in /home/pi.  If you install this anywhere else, you will need to modify the DIR line in the rpi.sensehat.mon file used later in the instructions.


Configuration:
In the data directory of the script there is a file called settings-example.py. Rename it to settings.py, review it, and make changes as needed.  The defaults assume you have the RPi Touchscreen and are going to use the SenseHAT Joystick to control Kodi.  If you're not sure what a setting does even after reading the comments in the settings.py file, you can probably leave it at the default.


Usage:
To run from the terminal (for testing): python /home/pi/rpi.sensehat.mon/execute.py
To exit: CNTL-C

If you are using the Joystick keyboard mapping, take a look at the settings.py file to see the default configuration.

Running from the terminal is useful during initial testing.  Once you know it's working the way you want, you should set it to autostart.  To do that:
From a terminal window: nano /home/pi/.config/lxsession/LXDE-pi/autostart
and add:				@python /home/pi/rpi.weatherstation.lite/execute.py &

Save and exit.  From now on the python script will start after the Raspian desktop loads.