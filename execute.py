# *  Credits:
# *
# *  v.0.0.5
# *  original Read SenseHAT code by pkscout

import os, random, subprocess, time
from threading import Thread
from resources.common.xlogger import Logger
from resources.common.fileops import writeFile, deleteFile
# from resources.sensehatmonitor import ConvertJoystickToKeypress, MonitorSensors

p_folderpath, p_filename = os.path.split( os.path.realpath(__file__) )
lw = Logger( logfile = os.path.join( p_folderpath, 'data', 'logfile.log' ) )

try:
    import data.settings as settings
    ADJUSTTEMP = settings.adjusttemp
    READINGDELTA = settngs.readingdelta
    CONVERTJOYSTICK = settings.convertjoystick
    LOCALKEYMAP = settings.localkeymap
    REVERSELR = settings.reverselr
except (ImportError, AttributeError, NameError) as error:
    lw.log( ['no settings or incomplete settings found, using defaults'] )
    ADJUSTTEMP = True
    READINGDELTA = 2
    CONVERTJOYSTICK = False
    LOCALKEYMAP = {}
    REVERSELR = True



class Main:
    def __init__( self ):
        self._init_vars()
        try:
            while True:
                self.SENSORDATA.log( [self._read_sensor()] )
                lw.log( ['waiting %s minutes before reading from sensor again' % str( READINGDELTA )] )
                time.sleep( READINGDELTA*60 )
        except KeyboardInterrupt:
          pass
        

    def _init_vars( self ):
        self.SENSORDATA = Logger( logname = 'sensordata',
                                  logconfig = 'timed',
                                  format = '%(asctime)-15s %(message)s',
                                  logfile = os.path.join( p_folderpath, 'data', 'sensordata.log' ) )
        

    def _read_sensor( self ):
        raw_temp = random.uniform( 19, 28 )
        if ADJUSTTEMP:
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
        humidity = self._reading_to_str( random.uniform( 52, 75 ) )
        pressure = self._reading_to_str( random.uniform( 950, 1050 ) )
        datastr = '\tIndoorTemp:%s\tIndoorHumidity:%s\tIndoorPressure:%s' % (temperature, humidity, pressure)
        lw.log( ['rounded data from sensor: ' + datastr] )
        return datastr


    def _reading_to_str( self, reading ):
        return str( int( round( reading ) ) )



if ( __name__ == "__main__" ):
    lw.log( ['script started'], 'info' )
    if CONVERTJOYSTICK:
        #create and start a separate thread to monitor the joystick and convert to keyboard presses for Kodi
        cj = ConvertJoystickToKeypress( localkeymap=LOCALKEYMAP, reverselr=REVERSELR )
        t1 = Thread( target=cj.Convert() )
        t1.setDaemon( True )
        t1.start()
    Main()
lw.log( ['script finished'], 'info' )