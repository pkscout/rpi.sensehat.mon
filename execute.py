# *  Credits:
# *
# *  v.0.0.9
# *  original RPi SenseHAT Control code by pkscout

import os, subprocess, sys, time
from datetime import datetime
from threading import Thread
from resources.common.xlogger import Logger
from resources.rpiinteract import ConvertJoystickToKeypress, ReadSenseHAT, RPiTouchscreen, RPiCamera
    

p_folderpath, p_filename = os.path.split( os.path.realpath(__file__) )
lw = Logger( logfile = os.path.join( p_folderpath, 'data', 'logfile.log' ) )

try:
    import data.settings as settings
    settings.adjusttemp
    settings.readingdelta
    settings.convertjoystick
    settings.reverselr
    settings.keymap
    settings.changescreen
    settings.screenofftime
    settings.screenontime
except (ImportError, AttributeError, NameError) as error:
    err_str = 'incomplete or no settings file found at %s' % os.path.join ( p_folderpath, 'data', 'settings.py' )
    lw.log( [err_str, 'script stopped'] )
    sys.exit( err_str )



class Main:
    def __init__( self ):
        self._init_vars()
        try:
            while True:
                self.SENSORDATA.log( [self._read_sensor()] )
                self._screen_change()
                lw.log( ['waiting %s minutes before reading from sensor again' % str( settings.readingdelta )] )
                time.sleep( settings.readingdelta * 60 )
        except KeyboardInterrupt:
          pass
        

    def _init_vars( self ):
        self.SENSOR = ReadSenseHAT()
        self.SCREEN = RPiTouchscreen()
        self.CAMERA = RPiCamera()
        self.SENSORDATA = Logger( logname = 'sensordata',
                                  logconfig = 'timed',
                                  format = '%(asctime)-15s %(message)s',
                                  logfile = os.path.join( p_folderpath, 'data', 'sensordata.log' ) )
        

    def _read_sensor( self ):
        raw_temp = self.SENSOR.Temperature()
        if settings.adjusttemp and raw_temp:
            # if the SenseHAT is too close to the RPi CPU, it reads hot. This corrects that
            # see https://github.com/initialstate/wunderground-sensehat/wiki/Part-3.-Sense-HAT-Temperature-Correction
            try:
                cpu_temp_raw = subprocess.check_output( "vcgencmd measure_temp", shell=True )
                cpu_temp = float( cpu_temp_raw.split( '=' )[1].split( "'" ) )
            except subprocess.CalledProcessError:
                cpu_temp = 0
            temperature = self._reading_to_str( raw_temp - ((cpu_temp - raw_temp)/5.466) )
        else:
            temperature = self._reading_to_str( raw_temp )
        humidity = self._reading_to_str( self.SENSOR.Humidity() )
        pressure = self._reading_to_str( self.SENSOR.Pressure() )
        if temperature == '0' and humidity == '0' and pressure == '0':
            datastr = ''
        else:
            datastr = '\tIndoorTemp:%s\tIndoorHumidity:%s\tIndoorPressure:%s' % (temperature, humidity, pressure)
        lw.log( ['rounded data from sensor: ' + datastr] )
        return datastr


    def _reading_to_str( self, reading ):
        return str( int( round( reading ) ) )


    def _screen_change( self ):
       if settings.changescreen:
            offtime = self._set_datetime( settings.screenofftime )
            ontime = self._set_datetime( settings.screenontime )
            rightnow = datetime.now()
            offdiff = rightnow - offtime
            ondiff = rightnow - ontime
            if abs( offdiff.total_seconds() ) < settings.readingdelta * 30: # so +/- window is total readingdelta
                lw.log( ['turning off screen'] )
                self.SCREEN.Power( switch='off' )
            elif abs( ondiff.total_seconds() ) < settings.readingdelta * 30:
                lw.log( ['turning on screen'] )
                self.SCREEN.Power( switch='on' )
            

    def _set_datetime( self, str_time ):
        tc = str_time.split( ':' )
        now = datetime.now()
        return datetime(year=now.year, month=now.month, day=now.day, hour=int( tc[0] ), minute=int( tc[1] ) )


if ( __name__ == "__main__" ):
    lw.log( ['script started'], 'info' )
    if settings.convertjoystick:
        #create and start a separate thread to monitor the joystick and convert to keyboard presses
        cj = ConvertJoystickToKeypress( keymap=settings.keymap, reverselr=settings.reverselr )
        t1 = Thread( target=cj.Convert() )
        t1.setDaemon( True )
        t1.start()
    Main()
lw.log( ['script finished'], 'info' )