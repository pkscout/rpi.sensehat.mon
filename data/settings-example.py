# amount of time between sensor readings (in minutes)
readingdelta = 2

# color settings for status lights
# acceptable color names are green, yellow, blue, red, white, nothing, pink
# use nothing for all colors if you want the LED off
# you can also use any RGB value as a tuple (255, 255, 255) is white
script_running = 'green'
kodi_connection = 'blue'
no_kodi_connection = 'red'

# whether autodim is enabled at restart (requires restart to take affect)
# the dark and light auto dim functions require Raspberry Pi camera
autodim = True

# amount of time (in minutes) between auto dim checks
autodimdelta = 0.5

# for autodim there are specific actions you can assign: ScreenOn, ScreenOff, Brightness:xxx
# for Brightness (and optionally for ScreenOn) :xxx is a number indicating the brightness to set
# if you use the dark or light triggers, they will run once and then not run again until
# the opposite trigger has happened (i.e. dark runs then won't run again until light occurs)

# light level thesholds for dark and light
# anything less than or equal to dark will be considered dark
# anything greater than or equal to light will be considered light
# for ambient light sensor target values are dark: 50, bright: 700
# for pi camera target values are dark: 10, bright: 80
dark = 50
bright = 700

# time (24 hour format) the updated sunrise and sunset should be fetched
fetchsuntime = '3:00'

# special triggers for autodim
specialtriggers = { 'dark': 'ScreenOff',
                    'dim': 'ScreenOn:100',
                    'bright': 'ScreenOn:200' }

# timed triggers are a list of lists in the form of time, action, day type
# time is 24 hour and can also take Sunrise and Sunset as a value
# day type is optional and can be Weekdays or Weekend
# WARNING: light levels cannot override timed triggers that turn the display off
# by default there are NO timed triggers, these are examples so you can see the format
timedtriggers = [
                  ['Sunrise', 'ScreenOn'],
                  ['8:00', 'Brightness:200'],
                  ['9:00', 'None', 'Weekend'],
                  ['14:00', 'None', 'Weekdays'],
                  ['Sunset', 'Brightness:100']
                ] 

# Weekdays and Weekend defined, if your system isn't using English use your local language
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
weekend  = ['Saturday', 'Sunday']

# the port of the SMBus (requires restart to take affect)
i2c_port = 1

# choose which sensor you're using: BME280 or SenseHat (requires restart to take affect)
which_sensor = 'BME280'

# set a sampling mode for the BME280 (requires restart to take affect)
# Oversampling modes
# oversampling.x1 = 1
# oversampling.x2 = 2
# oversampling.x4 = 3
# oversampling.x8 = 4
# oversampling.x16 = 5
bme280_sampling = 4

# the i2c address of the BME280 (requires restart to take affect)
bme280_address = 0x76

# the adjustment (in Celcius) to the BME280 - most reports are it reads a degree or so high
# (requires restart to take affect)
bme280_adjust = -1

# disable if the SenseHAT is far enough away from the RPi processor to read temp properly
# (requires restart to take affect)
sensehat_adjust = True

# the factor used to change the temperature read from the SenseHat
# for an RPi mounted as outlined in the wiki, use the factor below
# 5.466 is the standard if the SenseHat is in a regular case with the RPi
# (requires restart to take affect)
sensehat_factor = 8.199

# choose which 'camera' you are using to detect light levels: pi or ambient (requires restart to take effect)
which_camera = 'ambient'

# the i2c address of the ambient light sensor
ambient_address = 0x23

# the command to send to the ambient sensor if needed. If not, use 0. (requires restart to take affect)
# the BH1750 accepts the following commands to set the light sensor method:
# CONTINUOUS_LOW_RES_MODE = 0x13, CONTINUOUS_HIGH_RES_MODE_1 = 0x10, CONTINUOUS_HIGH_RES_MODE_2 = 0x11
# ONE_TIME_HIGH_RES_MODE_1 = 0x20, ONE_TIME_HIGH_RES_MODE_2 = 0x21, ONE_TIME_LOW_RES_MODE = 0x23
ambient_cmd = 0x20

# amount of time in minutes to look back at pressure history to determine pressure trend
pressuredelta = 180

# pressure in millibars that should be considered a rapid or regular change
pressurerapid   = 10
pressureregular = 3

# the URL Kodi remote command services are using (requires restart to take affect)
kodiuri = 'localhost'

# the port for websockets (requires restart to take affect)
kodiwsport = 9090

#number of sensor and script logs to keep (requires restart to take affect) 
logbackups = 1

# for debugging you can get a more verbose log by setting this to True (requires restart to take affect)
debug = False

# if you're testing on a non-RPi platform, setting to True will generate random data for
# all sensors and PiCamera light level (requires restart to take affect)
testmode = False