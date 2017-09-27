rpi.weatherstation.lite
================
This python script is designed to run as a service on a Raspberry Pi that has a SenseHAT installed.  It provides three functions:
1. read the temperature, humidity, and pressure from the SenseHat and write it to a file
2. monitor the SenseHAT joystick and translate the 10 state options (press and long press for each action) to keyboard presses. Also returns extra long held keys to main script for processing.
3. Turn the offical RPi touchscreen on or off on a schedule

The last two functions can be disabled via settings.


Prerequisites:
1. Optimally you should be running Raspian Jessie or later, as it has all the SenseHAT and touchscreen modules and most of the python bindings already included.  If you're running something older, you'll have to run the script, see what imports don't work, and download python modules as needed.

2. You should use Python 2.7.x for this. (3.4.x might work, but I haven't tested it).

3. If you want to use the SenseHAT joystick to control Kodi, you need to add the PyAutoGUI module and its associated dependencies to your python install. (these instructions are for Python 2.7.x. If you're using Python 3.4.x, then use pip3 and python3-dev)
From a terminal window:	sudo apt-get install  python-xlib
                        sudo apt-get install libjpeg-dev
                        pip install pillow
						pip install pyautogui

4. If you are using the official RPi 7" touchscreen and want to be able to control the on/off and brightness of the display, you need to add the rpi backlight module.  As per the github repo for this module, you also need to edit the backlight rules.
From a terminal window:	pip install rpi-backlight
						sudo nano /etc/udev/rules.d/backlight-permissions.rules
and add: SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/%k/brightness /sys/class/backlight/%k/bl_power"

Then reboot.

Installation:
It is recommended you install this in /home/pi.  If you install this anywhere else, you will need to modify the DIR line in the rpi.sensehat.mon file used later in the instructions.


Configuration:
In the data directory of the script there is a file called settings-example.py. Rename it to settings.py, review it, and make changes as needed.  If you want to use the SenseHAT joystick to control Kodi and/or have the official Raspberry Pi 7" touchscreen, you definitely need to make some changes to enable those options.  If you're not sure what a setting does even after reading the comments in the settings.py file, you can probably leave it at the default.


Usage:
To run from the terminal (for testing): python /home/pi/rpi.sensehat.mon/execute.py
To exit: CNTL-C

If you are using the Joystick keyboard mapping, take a look at the settings.py file to see the default configuration.

Running from the terminal is useful during initial testing.  Once you know it's working the way you want, you should set it to autostart.  To do that:

1. copy the rpi.sensehat.mon file (NOT the folder) to /etc/init.d
		sudo cp /home/pi/rpi.sensehat.mon/rpi.sensehat.mon /etc/init.d
		
2. update rc.d
		sudo update-rc.d rpi.sensehat.mon
		
When you restart the Pi, rpi.sensehat.mon will automatically start.  If you need to start or stop the script manually, you can do that with:

		sudo service rpi.sensehat.mon start
or		sudo service rpi.sensehat.mon stop
or		sudo service rpi.sensehat.mon reload
