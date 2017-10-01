# *  Credits:
# *
# *  v.1.0.0
# *  original RPi Camera classes by pkscout

try:
    import random, picamera, picamera.array
    import numpy as np
except ImportError:
    pass



class RPiCamera:
    def __init__( self, testmode=False ):
        self.TESTMODE = testmode
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

