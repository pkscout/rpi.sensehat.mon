defaults = { 'readingdelta': 10,
             'script_running': 'green',
             'kodi_connection': 'blue',
             'no_kodi_connection': 'red',
             'brightness_bar': 'yellow',
             'autodim': True,
             'autodimdelta': 0.5,
             'dark': 10,
             'bright': 80,
             'fetchsuntime': '3:00',
             'specialtriggers': { 'dark': 'ScreenOff', 'bright': 'ScreenOn:200', 'dim': 'ScreenOn:100' },
             'timedtriggers': [], 
             'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
             'weekend': ['Saturday', 'Sunday'],
             'which_sensor': 'BME280',
             'i2c_port': 1,
             'bme_address': 0x76,
             'bme280_sampling': 4,
             'sensehat_adjust': True,
             'sensehat_factor': 8.199,
             'pressuredelta': 180,
             'pressurerapid': 10,
             'pressureregular': 3,
             'kodiuri': 'localhost',
             'kodiwsport': 9090,
             'logbackups': 1,
             'debug': False,
             'testmode': False }

try:
    import data.settings as overrides
    has_overrides = True
except ImportError:
    has_overrides = False


def Reload():
    if has_overrides:
        reload( overrides )


def Get( name ):
    setting = None
    if has_overrides:
        setting = getattr(overrides, name, None)
    if not setting:
        setting = defaults.get( name, None )
    return setting
    