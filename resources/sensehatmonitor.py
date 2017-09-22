# *  Credits:
# *
# *  v.0.0.1
# *  original SenseHAT Monitor classes by pkscout

import pyautogui, signal, rpi_backlight
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED


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
    def __init__( self, keymap, reverselr ):
        self.DOWNACTION = 'pushed'
        self.BRIGHTNESSATOFF = rpi_backlight.get_actual_brightness()
        self.BDIRECTION = 1
        self.REVERSELR = reverselr
        self.KEYMAP = keymap


    def Convert( self ):
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


    def _adjust_brightness( self ):
        # only have one button for brightness, so this logic runs the brightness up to max
        # then back down to a minimum of 25 before going back up
        current = rpi_backlight.get_actual_brightness()
        current = current - (current % 25)
        if current == 250:
            self.BDIRECTION = -1
        elif current == 25:
            self.BDIRECTION = 1
        rpi_backlight.set_brightness( current + self.BDIRECTION*25, smooth=True, duration=1 )


    def _do_action_for( self, thekey ):
        if thekey == 'screenon':
            rpi_backlight.set_power( True )
            rpi_backlight.set_brightness( self.BRIGHTNESSATOFF, smooth=True, duration=3 )
        elif thekey == 'screenoff':
            self.BRIGHTNESSATOFF = rpi_backlight.get_actual_brightness()
            rpi_backlight.set_power( False )
        elif thekey == 'brightness':
            self._adjust_brightness()
        else:
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
