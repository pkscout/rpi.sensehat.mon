# boolean determining if you want to have the script adjust the temp returned
# to account for the temp of the RPi CPU.  You should really set this to False if the
# SenseHAT is in a separate case and connected with a ribbon cable
adjusttemp = True

# amount of time between sensor readings (in minutes)
readingdelta = 2

# whether autodim is enabled at restart
autodim = True

# if you want the script to trigger the Kodi weatherstation addon and update the weather window automatically, set to True
# if set to False the Kodi weatherstation addon should be set to poll periodically for new data
trigger_kodi = True

# the URL Kodi remote command services are using
kodiuri = 'localhost'

# the port for websockets
kodiwsport = 9090

# time to turn the screen off and on (hh:mm, 24 hour format)
changescreen = False
screenofftime = '22:00'
screenontime = '5:00'

# if True activates a thread to monitor the SenseHAT Joystick and convert those inputs
# into key presses (useful to control Kodi using the Joystick)
convertjoystick = True

# if the SenseHAT is mounted in a case where the joystick is facing the back, you want
# to reverse left and right actions so that it behaves the way you probably expect
reverselr = True

# the amount of time (in seconds) a joystick press has to be held to be considered extra long
lh_threshold = 4

# the keymap for regular and long holds of the SenseHAT Joystick
# the first item in the array is for single action, the second is for held action
keymap = {'up': ['up', 'brightness'],
          'down': ['down', 'c'],
          'left': ['left', 'screenoff'],
          'right': ['right', 'screenon'],
          'middle': ['return', 'esc']}

# keys you can set in localkeymap
# 'brightness', 'screenon', 'screenoff' <-- these control the RPi touchscreen if installed
# '\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
# ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
# '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
# 'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
# 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
# 'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
# 'browserback', 'browserfavorites', 'browserforward', 'browserhome',
# 'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
# 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
# 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
# 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
# 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
# 'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
# 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
# 'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
# 'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
# 'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
# 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
# 'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
# 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
# 'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
# 'command', 'option', 'optionleft', 'optionright'

# if you're testing on a non-RPi platform, setting to True will generate random data for
# SenseHAT sensors, extra long joystick actions, and PiCamera light level
testmode = False