from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
from signal import pause

x = 3
y = 3
sense = SenseHat()

def clamp(value, min_value=0, max_value=7):
    return min(max_value, max(min_value, value))

def pushed_up(event):
    global y
    if event.action != ACTION_RELEASED:
        y = clamp(y - 1)

def pushed_down(event):
    global y
    if event.action != ACTION_RELEASED:
        y = clamp(y + 1)

def pushed_left(event):
    global x
    if event.action != ACTION_RELEASED:
        x = clamp(x - 1)

def pushed_right(event):
    global x
    if event.action != ACTION_RELEASED:
        x = clamp(x + 1)

def pushed_middle(event):
    global down_action
    if event.action == ACTION_HELD:
      down_action = 'held'
      print "middle held"
    elif event.action == ACTION_PRESSED:
      down_action = 'pushed'
      print "middle pushed"
    elif event.action == ACTION_RELEASED:
      print "middle released"
      print "look at down action"
      if down_action == 'pushed':
        print 'do something for single press'
      elif down_action == 'held':
        print 'do something for held press'
      down_action = ''

def refresh():
    sense.clear()
    sense.set_pixel(x, y, 255, 255, 255)

sense.stick.direction_up = pushed_up
sense.stick.direction_down = pushed_down
sense.stick.direction_left = pushed_left
sense.stick.direction_right = pushed_right
sense.stick.direction_middle = pushed_middle
sense.stick.direction_any = refresh
refresh()
pause()