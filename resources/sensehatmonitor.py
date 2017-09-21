# *  Credits:
# *
# *  v.0.0.1
# *  original SenseHAT Monitor classes by pkscout

from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
import signal



class MonitorSensors:
    def __init__( self ):
        self.SENSE = SenseHat()

    
    def get_humidity( self ):
        return self.SENSE.get_humidity()

        
    def get_temperature( self ):
        return self.SENSE.get_temperature()

        
    def get_pressure( self ):
        return self.SENSE.get_pressure()



class ConvertJoystickToKeypress:
    def __init__( self, localkeymap={} ):
        self.DOWNACTION = 'pushed'
        if localkeymap:
            self.KEYMAP = localkeymap
        else:
            self.KEYMAP = {}
            self.KEYMAP['up'] = ['UP', 'O']
            self.KEYMAP['down'] = ['DOWN', 'C']
            self.KEYMAP['left'] = ['LEFT', 'X']
            self.KEYMAP['right'] = ['RIGHT', 'I']
            self.KEYMAP['middle'] = ['RETURN', 'ESCAPE']            


    def Convert( self ):
        sense = SenseHat()
        sense.stick.direction_up = self._pushed_up
        sense.stick.direction_down = self._pushed_down
        sense.stick.direction_left = self._pushed_left
        sense.stick.direction_right = self._pushed_right
        sense.stick.direction_middle = self._pushed_middle
        signal.pause()
        
    
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
        global down_action
        if self.DOWNACTION == 'pushed':
            print 'press ' + key_pushed
        elif self.DOWNACTION == 'held':
            print 'press ' + key_held
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