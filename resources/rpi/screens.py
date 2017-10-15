# *  Credits:
# *
# *  v.1..0
# *  original RPi Screen classes by pkscout

import time
try:
    import rpi_backlight
except ImportError:
    pass
try:
    from sense_hat import SenseHat
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
            
    
    def SetBrightness( self, brightness, max=255, min=11, smooth=True, duration=10 ):
        brightness = int( brightness )
        if brightness == self.CURRENTBRIGHTNESS:
            return
        if brightness > max:
            brightness = max
        elif brightness < 11:
            # I have no idea why the fork the absolute minimum is 11, but it is
            brightness = 11
        elif brightness < min:
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
        self.SetBrightness( new_brightness, max = max, min = min, duration = duration )


    def GetBrightness( self ):
        return self.CURRENTBRIGHTNESS



class SenseHatLED:
    def __init__( self, low_light=True, rotate=False ):
        try:
            self.SENSE = SenseHat()
        except (OSError, NameError) as error:
            self.SENSE = None
        if self.SENSE:
            self.SENSE.low_light = low_light
            if rotate:
                self.SENSE.set_rotation( 180 )
        self.PALETTE = {'green':(0, 255, 0), 'yellow':(255, 255, 0), 'blue':(0, 0, 255),
                        'red':(255, 0, 0), 'white':(255,255,255), 'nothing':(0,0,0),
                        'pink':(255,105, 180)}
    
    
    def Blink( self, x, y, color=(255, 255, 255), pause=0.2, pivot=False ):
        if pivot:
            bx = y
            by = x
        else:
            bx = x
            by = y
        self.PixelOn( bx, by, color )
        time.sleep( pause )
        self.PixelOff( bx, by )


    def ClearPanel( self, color=None ):
        if self.SENSE:
            if color:
                self.SENSE.clear( color )
            else:
                self.SENSE.clear()


    def Color( self, color ):
        if isinstance( color, basestring ):
            return self.PALETTE[color.lower()]
        elif isinstance( color, tuple ):
            if len( color ) == 3:
               return color
        return (255, 255, 255)


    def PixelOff( self, x, y ):
        if self.SENSE:
            self.SENSE.set_pixel( x, y, 0, 0, 0 )
        
        
    def PixelOn( self, x, y, color=(255, 255, 255) ):
        if self.SENSE:
            self.SENSE.set_pixel( x, y, color )
        

    def SetBar( self, level, vertical=False, anchor=0, min=0, max=255, color=(255, 255, 255) ):
        step = (max - min)/8
        height = int( (level - min)/step )
        for loc in range( 0, 7 ):
            if vertical:
                x = anchor
                y = loc
            else:
                x = loc
                y = anchor
            if loc < height:
                self.PixelOn( x, y, color )
            else:
                self.PixelOff( x, y )


    def Sweep( self, vertical=False, anchor=0, start=0, stop=7, color=(255, 255, 255), pause=0.1 ):
        if start < 0:
            start = 0
        if stop > 7:
            stop = 7
        current = start
        while current <= stop:
            self.Blink( current, anchor, color, pause, vertical )
            current = current + 1
        current = current - 2
        while current >= start:
            self.Blink( current, anchor, color, pause, vertical )
            current = current - 1
    
