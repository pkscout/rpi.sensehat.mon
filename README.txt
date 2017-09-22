rpi.sensehat.mon
================
This python script is designed to run as a service on a Raspberry Pi that has a SenseHAT installed.  If provides three functions:
1. read the temperature, humidity, and pressure from the SenseHat and write it to a file
2. monitor the SenseHAT joystick and translate the 10 state options to keyboard presses (useful if you're using this in conjunction with Kodi)
3. Turn the offical RPi touchscreen on or off on a schedule

The last two functions can be disabled via settings.


Prerequisites:
1. Optimally you should be running Raspian Jessie or later, as it has all the SenseHAT and touchscreen modules and python bindings already included.  If you're running something older, you'll have to run the script, see what imports don't work, and download python modules as needed.

2. You should use Python 2.7.x for this. (3.4.x might work, but I haven't tested it).

3. You need to add the PyAutoGUI module and its associated dependencies to your python install.  This is the module that does the key presses. (these instructions are for Python 2.7.x. If you're using Python 3.4.x, then use pip3, python3-tk, and python3-dev)
From a terminal window:	pip install python-xlib
						sudo apt-get install scrot
						sudo apt-get install python-tk
						sudo apt-get install python-dev
						pip install pyautogui

4. PLACEHOLDER IN CASE THERE ARE OTHER MODULES TO INSTALL

Installation:
It is recommended you install this in /home/pi.  If you install this anywhere else, you will need to modify the DIR line in the rpi.sensehat.mon file.


Configuration:
In the data directory of the script there is a file called settings.py.  Review the settings file and make changes as needed.  If you're not sure what a setting does even after reading the comments in the settings.py file, you can probably leave it at the default.


Usage:
To run from the terminal: python /home/pi/rpi.sensehat.mon/execute.py
To exit: CNTL-C

Running from the terminal is useful during initial testing.  Once you know it's working the way you want, you should set it to autostart.  To do that:

1. copy the rpi.sensehat.mon file (NOT the folder) to /etc/init.d
		sudo cp /home/pi/rpi.sensehat.mon/rpi.sensehat.mon /etc/init.d
		
2. update rc.d
		sudo update-rc.d rpi.sensehat.mon
		
When you restart rpi.sensehat.mon will automatically start.  If you need to start or stop the script manually, you can do that with:

		sudo service rpi.sensehat.mon start
or		sudo service rpi.sensehat.mon stop
or		sudo service rpi.sensehat.mon reload