# *  Credits:
# *
# *  v.0.0.1
# *  original Screen Control classes by pkscout

try:    
    import rpi_backlight
    has_rpi_backlight = True
except ImportError:
    has_rpi_backlight = False



class RPiTouchscreen:
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


    def BrightnessDown( self, step=25, smooth=True, duration=1 )
        if has_rpi_backlight:
            current = rpi_backlight.get_actual_brightness()
            current = current - (current % step)
            if not current == step:
                self.BDIRECTION = -1
                self.AdjustBrightness( step=step, smooth=smooth, duration=duration )
            
            
    def BrightnessUp( self, self, step=25, smooth=True, duration=1 )    
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
