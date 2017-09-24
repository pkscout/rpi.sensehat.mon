# *  Credits:
# *
# *  v.0.0.1
# *  original SenseHAT Monitor classes by pkscout

try:
    import pyautogui
    haspyautogui = True
except ImportError:
    haspyautogui = False
try:
    from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
    hassensehat = True
except ImportError:
#    from random import randint
    hassensehat = False
import signal
from screencontrol import RPiTouchscreen


class MonitorSensors:
    def __init__( self ):
        if hassensehat:
            self.SENSE = SenseHat()

    
    def get_humidity( self ):
        if hassensehat:
            return self.SENSE.get_humidity()
        else:
#            return randint( 43, 68 )
            return 0

        
    def get_temperature( self ):
        if hassensehat:
            return self.SENSE.get_temperature()
        else:
#            return randint( 21, 28 )
            return 0

        
    def get_pressure( self ):
        if hassensehat:
            return self.SENSE.get_pressure()
        else:
#            return randint( 990, 1020 )
            return 0



class ConvertJoystickToKeypress:
    def __init__( self, keymap, reverselr ):
        self.DOWNACTION = 'pushed'
        self.REVERSELR = reverselr
        self.KEYMAP = keymap
        self.rpit = RPiTouchscreen()


    def Convert( self ):
        if hassensehat:
            sense = SenseHat()
            sense.stick.direction_up = self._pushed_up
            sense.stick.direction_down = self._pushed_down
            sense.stick.direction_middle = self._pushed_middle
            if self.REVERSELR:
                sense.stick.direction_left = self._pushed_right
                sense.stick.direction_right = self._pushed_left
            else:
                sense.stick.direction_left = self._pushed_left
                sense.stick.direction_right = self._pushed_right        
            signal.pause()


    def _do_action_for( self, thekey ):
        if thekey == 'screenon':
            self.rpit.Power( switch='on' )
        elif thekey == 'screenoff':
            self.rpit.Power( switch='off' )
        elif thekey == 'brightness':
            self.rpit.AdjustBrightness()
        elif haspyautogui:
            pyautogui.press( thekey )


    def _is_released( self, event ):
        if event.action == ACTION_HELD:
          self.DOWNACTION = 'held'
          return False
        elif event.action == ACTION_PRESSED:
          self.DOWNACTION = 'pushed'
          return False
        elif event.action == ACTION_RELEASED:
          return True
  
    
    def _press_key( self, key_pushed, key_held ):
        if self.DOWNACTION == 'pushed':
            self._do_action_for( key_pushed )
        else:
            self._do_action_for( key_held )
        self.DOWNACTION = ''


    def _pushed_up( self, event ):
        if self._is_released( event ):
            self._press_key( self.KEYMAP['up'] )
  
    
    def _pushed_down( self, event ):
        if self._is_released( event ):
            self._press_key( self.KEYMAP['down'] )
  
    
    def _pushed_left( self, event ):
        if self._is_released( event ):
            self._press_key( self.KEYMAP['left'] )
  
            
    def _pushed_right( self, event ):
        if self._is_released( event ):
            self._press_key( self.KEYMAP['right'] )
  
    
    def _pushed_middle( self, event ):
        if self._is_released( event ):
            self._press_key( self.KEYMAP['middle'] )
