# *  Credits:
# *
# *  v.0.1.0
# *  original RPi Weatherstation Lite code by pkscout

import os, subprocess, sys, time
import resources.passback as passback
from datetime import datetime
from threading import Thread
from resources.common.xlogger import Logger
from resources.rpiinteract import ConvertJoystickToKeypress, ReadSenseHAT, RPiTouchscreen, RPiCamera

p_folderpath, p_filename = os.path.split( os.path.realpath(__file__) )
lw = Logger( logfile = os.path.join( p_folderpath, 'data', 'logfile.log' ) )
sensordata = Logger( logname = 'sensordata',
                     logconfig = 'timed',
                     format = '%(asctime)-15s %(message)s',
                     logfile = os.path.join( p_folderpath, 'data', 'sensordata.log' ) )

try:
    import data.settings as settings
    settings.adjusttemp
    settings.readingdelta
    settings.autodim
    settings.trigger_kodi
    settings.kodiuri
    settings.kodiwsport
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

if settings.trigger_kodi:
    if sys.version_info >= (2, 7):
        import json as _json
    else:
        import simplejson as _json
    jsondict = {'id':'1', 
                'jsonrpc':'2.0',
                'method':'Addons.ExecuteAddon',
                'params':{"addonid":"script.weatherstation"}}
    jsondata = _json.dumps( jsondict )
    try:
        import websocket
    except ImportError:
        lw.log( ['websocket-client not installed, so the script cannot trigger Kodi weather window updates'] )
        settings.trigger_kodi = False
else:
    jsondata = ''



class Main:
    def __init__( self, ws=None ):
        self.WS = ws
        self._init_vars()
        try:
            while True:
                sensordata.log( [self._read_sensor()] )
                if settings.trigger_kodi:
                    self.WS.send( jsondata )
                self._screen_change()
                lw.log( ['waiting %s minutes before reading from sensor again' % str( settings.readingdelta )] )
                time.sleep( settings.readingdelta * 60 )
        except KeyboardInterrupt:
          pass
        

    def _init_vars( self ):
        self.SENSOR = ReadSenseHAT()
        self.SCREEN = RPiTouchscreen()
        self.CAMERA = RPiCamera()
        

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



class CheckPassback:
    def __init__( self, ws=None ):
        self.WS = ws
        
    def Run( self ):    
        past = passback.xljoystick
        while True:
            current = passback.xljoystick
            if past != current:
                lw.log( ['xljoystick has changed to ' + current] )
                if current == 'up':
                    settings.autodim = not settings.autodim
                    lw.log( ['autodim has been set to ' + str( settings.autodim )] )
                    sensordata.log( ['\tautodim:' +  str( settings.autodim )] )
                    if settings.trigger_kodi:
                        self.WS.send( jsondata )
                past = current



def RunScript( ws=None ):
    if settings.convertjoystick:
        # create and start a separate thread to monitor the joystick and convert to keyboard presses
        cj = ConvertJoystickToKeypress( keymap = settings.keymap,
                                        reverselr = settings.reverselr )
        cp = CheckPassback( ws = ws )
        t1 = Thread( target = cp.Run )
        t1.setDaemon( True )
        t1.start()
        t2 = Thread( target = cj.Convert )
        t2.setDaemon( True )
        t2.start()
    Main( ws=ws )
    

def RunInWebsockets():
    def on_message(ws, message):
        lw.log( ['got back: ' + message] )
    def on_error(ws, error):
        lw.log( [error] )
    def on_close(ws):
        lw.log( ['websocket connection closed'] )
    def on_open(ws):
        lw.log( ['websocket connection opening'] )
        RunScript( ws )
        ws.close()
    kodiurl = 'ws://%s:%s/jsponrpc' % (settings.kodiuri, settings.kodiwsport )
    ws = websocket.WebSocketApp( kodiurl, on_message = on_message, on_error = on_error, on_open = on_open, on_close = on_close )
    ws.run_forever()        


if ( __name__ == "__main__" ):
    lw.log( ['script started'], 'info' )
    if settings.trigger_kodi:
        RunInWebsockets()
    else:
        RunScript()
lw.log( ['script finished'], 'info' )