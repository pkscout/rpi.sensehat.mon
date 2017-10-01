# amount of time between sensor readings (in minutes)
readingdelta = 2

# whether autodim is enabled at restart (if you change this it won't matter until you restart)
# the dark and light auto dim functions require Raspberry Pi camera
autodim = True

# for autodim there are specific actions you can assign:
# GetSunriseSunset, ScreenOn, ScreenOff, Brightness:xxx
# for Brightness (and optionally for ScreenOn) :xxx is a number indicating the brightness to set
# if you use the dark or light triggers, they will run once and then not run again until
# the opposite trigger has happened (i.e. dark runs then won't run again until light occurs)

# light level thesholds for dark and light
# anything less than or equal to dark will be considered dark
# anything greater than or equal to light will be considered light
dark = 10
light = 80

# special triggers for autodim
specialtriggers = { 'dark': 'ScreenOff',
                    'light': 'ScreenOn',
                    'sunrise': 'ScreenOn:200',
                    'sunset': 'Brightness:175' }

# timed triggers are a list of lists in the form of time:action (time is 24 hour format)
timedtriggers = [
                  ['3:00', 'GetSunriseSunset'],
                  ['7:30', 'Brightness:255']
                ] 

# if you want the script to trigger the Kodi weatherstation addon and update the weather window automatically, set to True
# if set to False the Kodi weatherstation addon should be set to poll periodically for new data
trigger_kodi = True

# the URL Kodi remote command services are using
kodiuri = 'localhost'

# the port for websockets
kodiwsport = 9090

# if you're testing on a non-RPi platform, setting to True will generate random data for
# SenseHAT sensors and PiCamera light level. Requires reboot if changed.
testmode = False