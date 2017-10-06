defaults = { 'readingdelta': 10,
             'script_running': 'green',
             'kodi_connection': 'blue',
             'no_kodi_connection': 'red',
             'autodim': True,
             'autodimdelta': 0.5,
             'dark': 10,
             'light': 50,
             'fetchsuntime': '3:00',
             'specialtriggers': { 'dark': 'ScreenOff', 'light': 'ScreenOn' },
             'timedtriggers': [['Sunrise', 'ScreenOn'], ['8:00', 'Brightness:200'], ['Sunset', 'Brightness:100']], 
             'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
             'weekend': ['Saturday', 'Sunday'],
             'pressuredelta': 180,
             'pressurerapid': 10,
             'pressureregular': 3,
             'kodiuri': 'localhost',
             'kodiwsport': 9090,
             'logbackups': 0,
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
    