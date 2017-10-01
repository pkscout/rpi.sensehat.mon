# *  Credits:
# *
# *  v.1.0.0
# *  original RPi Sensor classes by pkscout

try:
    import random
    from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
except ImportError:
    pass



class SenseHatSensors:
    def __init__( self, testmode=False ):
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
                reading = self.SENSE.get_temperature()
                if reading:
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

