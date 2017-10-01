# amount of time between sensor readings (in minutes)
readingdelta = 2

# whether autodim is enabled at restart (if you change this it won't matter until you restart)
# requires Raspberry Pi camera
autodim = False

# max and min brightness for auto dim (the Pi Touchscreen can take values from 11 to 255)
mindim = 25
maxdim = 255

# max and min light levels for auto dim (0 is pitch dark, 255 is staring into the sun)
minlevel = 0
maxlevel = 80

# time set backlight to 11 then back up (hh:mm, 24 hour format)
changescreen = False
screenofftime = '5:00'
screenontime = '23:00'

# if you want the script to trigger the Kodi weatherstation addon and update the weather window automatically, set to True
# if set to False the Kodi weatherstation addon should be set to poll periodically for new data
trigger_kodi = True

# the URL Kodi remote command services are using
kodiuri = 'localhost'

# the port for websockets
kodiwsport = 9090

# if you're testing on a non-RPi platform, setting to True will generate random data for
# SenseHAT sensors and PiCamera light level
testmode = False