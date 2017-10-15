# *  Credits:
# *
# *  v.1.0.0
# *  original RPi Camera classes by pkscout

try:
    import random, picamera, picamera.array
    import numpy as np
except ImportError:
    pass
try:
    import smbus2
except ImportError:
    pass



class AmbientSensor:
    def __init__ ( self, port=1, address=0x23, testmode=False ):
        self.ADDRESS = address
        self.TESTMODE = testmode
        self.POWER_DOWN = 0x00 # No active state
        self.POWER_ON   = 0x01 # Power on
        self.RESET      = 0x07 # Reset data register value
        self.CONTINUOUS_LOW_RES_MODE = 0x13
        self.CONTINUOUS_HIGH_RES_MODE_1 = 0x10
        self.CONTINUOUS_HIGH_RES_MODE_2 = 0x11
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20
        self.ONE_TIME_HIGH_RES_MODE_2 = 0x21
        self.ONE_TIME_LOW_RES_MODE = 0x23
        try:
            self.BUS = smbus2.SMBus( port )
        except (OSError, NameError) as error:
            self.BUS = None

    
    def LightLevel( self ):
        if self.BUS:
            data = bus.read_i2c_block_data( self.ADDRESS, self.ONE_TIME_HIGH_RES_MODE_1 )
            return self._converttonumber( data )
        elif self.TESTMODE:
            return random.randint( 0, 65000 )
        return None


    def _converttonumber( self, data ):
        return ((data[1] + (256 * data[0])) / 1.2)


   
class RPiCamera:
    def __init__( self, useled=False, testmode=False ):
        self.TESTMODE = testmode
        self.USELED = useled
        try:
            picamera
            self.CAMERA = True
        except NameError:
            self.CAMERA = False
    
    def LightLevel( self ):
        if self.CAMERA:
            for i in range( 0, 5 ):
                with picamera.PiCamera() as camera:
                    camera.resolution = (128, 80)
                    camera.led = self.USELED
                    with picamera.array.PiRGBArray(camera) as stream:
                        camera.exposure_mode = 'auto'
                        camera.awb_mode = 'auto'
                        camera.capture(stream, format='rgb')
                        reading = int(np.average(stream.array[...,1])) + 1
                if reading:
                    return reading
        elif self.TESTMODE:
            return random.randint( 0, 255 )
        return None

