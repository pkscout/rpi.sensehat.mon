# *  Credits:
# *
# *  v.1..0
# *  original RPi Screen classes by pkscout

try:
    import random, rpi_backlight
except ImportError:
    pass



class RPiTouchscreen:
    def __init__( self, testmode=False ):
        self.BDIRECTION = 1
        self.TESTMODE = testmode
        try:
            self.CURRENTBRIGHTNESS = rpi_backlight.get_actual_brightness()
            self.TOUCHSCREEN = True
        except NameError:
            self.CURRENTBRIGHTNESS = 255
            self.TOUCHSCREEN = False
            
    
    def SetBrightness( self, brightness, max=255, min=11, smooth=True, duration=3 ):
        brightness = int( brightness )
        if brightness == self.CURRENTBRIGHTNESS:
            return
        if brightness > max:
            brightness = max
        elif brightness < min:
            # I have no idea why the fork the minimum is 11, but it is
            brightness = min
        if self.TOUCHSCREEN:
            rpi_backlight.set_brightness( brightness, smooth = smooth, duration = duration )
            self.CURRENTBRIGHTNESS = brightness


    def AdjustBrightness( self, direction, step=25, smooth=True, duration=1 ):
        max = int( 255 / step ) * step
        min = step
        if self.CURRENTBRIGHTNESS > max:
            self.CURRENTBRIGHTNESS = max
        elif self.CURRENTBRIGHTNESS < min:
            self.CURRENTBRIGHTNESS = min
        if direction == 'down':
            step = -1 * step
        new_brightness = self.CURRENTBRIGHTNESS + step
        self.SetBrightness( new_brightness, max = max, min = min )


    def GetBrightness( self ):
        return self.CURRENTBRIGHTNESS


