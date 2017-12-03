# *  Credits:
# *
# *  v.1.0.0
# *  original RPi Camera classes by pkscout

import time
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
    def __init__ ( self, port=1, address=0x23, cmd=0x20, oversample=10, testmode=False ):
        self.ADDRESS = address
        self.CMD = cmd
        self.OVERSAMPLE = int( oversample )
        self.TESTMODE = testmode
        try:
            self.BUS = smbus2.SMBus( port )
        except (OSError, NameError) as error:
            self.BUS = None

    
    def LightLevel( self ):
        if self.BUS:
            level = 0
            for x in range( 0, self.OVERSAMPLE ):
                data = self.BUS.read_i2c_block_data( self.ADDRESS, self.CMD, 2 )
                level = level + self._converttonumber( data )
                time.sleep( 0.1 )
            return  level/self.OVERSAMPLE + 1
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

