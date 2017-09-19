# *  Credits:
# *
# *  v.0.0.2
# *  original Read SenseHAT code by pkscout

import atexit, os, random, time
from resources.common.xlogger import Logger
from resources.common.fileops import readFile, writeFile, deleteFile

p_folderpath, p_filename = os.path.split( os.path.realpath(__file__) )
lw = Logger( logfile = os.path.join( p_folderpath, 'data', 'logfile.log' ) )


def _deletePID():
    success, loglines = deleteFile( pidfile )
    lw.log (loglines )

pid = str(os.getpid())
pidfile = os.path.join( p_folderpath, 'data', 'read.pid' )
atexit.register( _deletePID )


class Main:
    def __init__( self ):
        self._setPID()
        self._init_vars()
        self.SENSORDATA.log( [self._read_sensor()] )
        

    def _init_vars( self ):
        self.SENSORDATA = Logger( logname = 'sensordata',
                                  logconfig = 'timed',
                                  format = '%(asctime)-15s %(message)s',
                                  logfile = os.path.join( p_folderpath, 'data', 'sensordata.log' ) )
        

    def _read_sensor( self ):
        temperature = str( random.randint( 19, 28 ) )
        humidity = str( random.randint( 52, 75 ) )
        pressure = str( random.randint( 950, 1050 ) )
        datastr = '\tIndoorTemp:%s\tIndoorHumidity:%s\tIndoorPressure:%s' % (temperature, humidity, pressure)
        lw.log( ['data from sensor: ' + datastr] )
        return datastr


    def _setPID( self ):
        basetime = time.time()
        while os.path.isfile( pidfile ):
            time.sleep( random.randint( 1, 3 ) )
            if time.time() - basetime > 3:
                err_str = 'taking too long for previous process to close - aborting attempt to read sensor'
                lw.log( [err_str] )
                sys.exit( err_str )
        lw.log( ['setting PID file'] )
        success, loglines = writeFile( pid, pidfile )
        lw.log( loglines )        



if ( __name__ == "__main__" ):
    lw.log( ['script started'], 'info' )
    Main()
lw.log( ['script finished'], 'info' )