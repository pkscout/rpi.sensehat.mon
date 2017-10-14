# *  Credits:
# *
# *  v.2.0.0~beta1
# *  original RPi Sensor classes by pkscout

import datetime, random, subprocess, time
try:
    from sense_hat import SenseHat
except ImportError:
    pass
try:
    import smbus2, bme280
except ImportError:
    pass
    
    
class BME280Sensors:
    def __init__( self, port=1, address=0x76, sampling=4, testmode=False ):
        self.TESTMODE = testmode
        self.ADDRESS = address
        self.SAMPLING = sampling
        self.DATA = None
        try:
            self.BUS = smbus2.SMBus( port )
            bme280.load_calibration_params( self.BUS, self.ADDRESS )
        except (OSError, NameError, TypeError) as error:
            self.BUS = None
    
    
    def Humidity( self ):
        if self.BUS:
            self._get_data()
            return self.DATA.humidity
        elif self.TESTMODE:        
            return random.randint( 43, 68 )
        return None

    
    def Temperature( self ):
        if self.BUS:
            self._get_data()
            return self.DATA.temperature
        elif self.TESTMODE:        
            return random.randint( 21, 28 )
        return None
    
    
    def Pressure( self ):
        if self.BUS:
            self._get_data()
            return self.DATA.pressure
        elif self.TESTMODE:        
            return random.randint( 990, 1020 )
        return None

    
    def _get_data( self ):
        if not self.DATA:
            self._sample()
        else:
            diff = datetime.datetime.now() - self.DATA.timestamp
            if diff.total_seconds > 60:
                self._sample()


    def _sample( self ):
        self.DATA = bme280.sample(bus = self.BUS, address = self.ADDRESS, sampling = self.SAMPLING )



class SenseHatSensors:
    def __init__( self, adjust=False, factor=5.466, testmode=False ):
        self.ADJUST = adjust
        self.FACTOR = factor
        self.TESTMODE = testmode
        try:
            self.SENSE = SenseHat()
        except (OSError, NameError) as error:
            self.SENSE = None

    
    def Humidity( self ):
        if self.SENSE:
            for i in range( 0, 5 ):
                reading = self.SENSE.get_humidity()
                if reading:
                    return reading
        elif self.TESTMODE:        
            return random.randint( 43, 68 )
        return None

        
    def Temperature( self ):
        if self.SENSE:
            for i in range( 0, 5 ):
                p_reading = self.SENSE.get_temperature_from_pressure()
                h_reading = self.SENSE.get_temperature()
                if p_reading < h_reading:
                    reading = p_reading
                else:
                    reading = h_reading
                if reading:
                    if self.ADJUST:
                        cpu_raw = subprocess.check_output("vcgencmd measure_temp", shell=True)
                        cpu_temp = float( cpu_raw.split( "=" )[1].split( "'" )[0] )
                        return int( round( reading - ((cpu_temp - reading)/self.FACTOR), 0 ) )
                    else:
                        return reading
        elif self.TESTMODE:        
            return random.randint( 21, 28 )
        return None

        
    def Pressure( self ):
        if self.SENSE:
            for i in range( 0, 5 ):
                reading = self.SENSE.get_pressure()
                if reading:
                    return reading
        elif self.TESTMODE:        
            return random.randint( 990, 1020 )
        return None



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
    
        
            
    
    
    