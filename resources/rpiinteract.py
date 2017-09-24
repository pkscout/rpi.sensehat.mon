# *  Credits:
# *
# *  v.0.0.1
# *  original RPi Interaction classes by pkscout

try:
    from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
    has_sense_hat = True
except ImportError:
#    from random import randint
    has_sense_hat = False


class ReadSenseHAT:
    def __init__( self ):
        if has_sense_hat:
            self.SENSE = SenseHat()

    
    def Humidity( self ):
        if has_sense_hat:
            return self.SENSE.get_humidity()
        else:
#            return randint( 43, 68 )
            return 0

        
    def Temperature( self ):
        if has_sense_hat:
            return self.SENSE.get_temperature()
        else:
#            return randint( 21, 28 )
            return 0

        
    def Pressure( self ):
        if has_sense_hat:
            return self.SENSE.get_pressure()
        else:
#            return randint( 990, 1020 )
            return 0



class ConvertJoystickToKeypress:
    import signal
    try:
        import pyautogui
        has_pyautogui = True
    except ImportError:
        has_pyautogui = False


    def __init__( self, keymap, reverselr ):
        self.DOWNACTION = 'pushed'
        self.REVERSELR = reverselr
        self.KEYMAP = keymap
        self.rpit = RPiTouchscreen()


    def Convert( self ):
        if has_sense_hat:
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
        elif has_py_autogui:
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



class RPiTouchscreen:
    try:    
        import rpi_backlight
        has_rpi_backlight = True
    except ImportError:
        has_rpi_backlight = False


    def __init__( self ):
        self.BDIRECTION = 1


    def AdjustBrightness( self, step=25, smooth=True, duration=1 ):
        # only have one button for brightness, so this logic runs the brightness up to max
        # then back down to a minimum of the given step before going back up
        max = 255 - ( 255 % step )
        min = step
        current = rpi_backlight.get_actual_brightness()
        current = current - (current % step)
        if current == max:
            self.BDIRECTION = -1
        elif current == step:
            self.BDIRECTION = 1
        rpi_backlight.set_brightness( current + (self.BDIRECTION * step), smooth=smooth, duration=duration )


    def BrightnessDown( self, step=25, smooth=True, duration=1 ):
        if has_rpi_backlight:
            current = rpi_backlight.get_actual_brightness()
            current = current - (current % step)
            if not current == step:
                self.BDIRECTION = -1
                self.AdjustBrightness( step=step, smooth=smooth, duration=duration )
            
            
    def BrightnessUp( self, step=25, smooth=True, duration=1 ):    
        if has_rpi_backlight:
            current = rpi_backlight.get_actual_brightness()
            current = current - (current % step)
            max = 255 - ( 255 % step )
            if not current == max:
                self.BDIRECTION = 1
                self.AdjustBrightness( step=step, smooth=smooth, duration=duration )


    def Power( self, switch='on', smooth=True, brightness=0, duration=3 ):
        if switch == 'on' and has_rpi_backlight:
            rpi_backlight.set_power( True )
        if brightness and has_rpi_backlight:
            rpi_backlight.set_brightness( brightness, smooth=True, duration=3 )
        if switch == 'off' and has_rpi_backlight:
            rpi_backlight.set_power( False )
    
    
    def SetBrightness( self, brightness=255, smooth=True, duration=3 ):
        if has_rpi_backlight:
            if brightness > 255:
                brightness = 255
            elif brightness < 10:
                brightness = 10
            rpi_backlight.set_brightness( brightness, smooth=smooth, duration=duration )



