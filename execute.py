# *  Credits:
# *
# *  v.0.4.1
# *  original RPi Weatherstation Lite code by pkscout

import os, sys, time
from datetime import datetime
from threading import Thread
from resources.common.xlogger import Logger
from resources.rpi.sensors import SenseHatSensors
from resources.rpi.screens import RPiTouchscreen
from resources.rpi.cameras import RPiCamera
if sys.version_info >= (2, 7):
    import json as _json
else:
    import simplejson as _json


p_folderpath, p_filename = os.path.split( os.path.realpath(__file__) )
lw = Logger( logfile = os.path.join( p_folderpath, 'data', 'logfile.log' ) )
sensordata = Logger( logname = 'sensordata',
                     logconfig = 'timed',
                     format = '%(asctime)-15s %(message)s',
                     logfile = os.path.join( p_folderpath, 'data', 'sensordata.log' ) )

try:
    import data.settings as settings
    settings.readingdelta
    settings.autodim
    settings.mindim
    settings.maxdim
    settings.minlevel
    settings.maxlevel
    settings.changescreen
    settings.screenofftime
    settings.screenontime
    settings.trigger_kodi
    settings.kodiuri
    settings.kodiwsport
    settings.testmode
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
                'params':{"addonid":"script.weatherstation.lite"}}
    jsondata = _json.dumps( jsondict )
    try:
        import websocket
    except ImportError:
        lw.log( ['websocket-client not installed, so the script cannot trigger Kodi weather window updates'] )
        settings.trigger_kodi = False
else:
    jsondata = ''



class Main:
    def __init__( self ):
        self.SENSOR = SenseHatSensors( testmode = settings.testmode )
        self.SCREEN = RPiTouchscreen( testmode = settings.testmode )
        self.CAMERA = RPiCamera( testmode = settings.testmode )
        self.STOREDBRIGHTNESS = 255
        self.SCREENSTATE = 'On'


    def Run( self ):
        temperature = self.SENSOR.Temperature()
        humidity = self.SENSOR.Humidity()
        pressure = self.SENSOR.Pressure()
        lightlevel = self.CAMERA.LightLevel()
        s_data = []
        if temperature is not None:
            s_data.append( 'IndoorTemp:' + self._reading_to_str( temperature ) )
        if humidity is not None:
            s_data.append( 'IndoorHumidity:' + self._reading_to_str( humidity ) )
        if pressure is not None:
            s_data.append( 'IndoorPressure:' + self._reading_to_str( pressure ) )
        s_data.append( 'AutoDim:' + str( settings.autodim ) )
        s_data.append( 'ScreenStatus:' + self._screen_change() )
        if lightlevel is not None:
            s_data.append( 'LightLevel:' + self._reading_to_str( lightlevel ) )
        d_str = ''
        for item in s_data:
            d_str = '%s\t%s' % (d_str, item)
        lw.log( ['rounded data from sensor: ' + d_str] )
        sensordata.log( [d_str] )
        self._triggerscan()
        self._autodim( lightlevel = lightlevel )
                

    def HandleAction( self, action ):
        if action == 'BrightnessUp':
            lw.log( ['turning brightness up'] )
            self.SCREEN.AdjustBrightness( direction='up' )
        elif action == 'BrightnessDown':
            lw.log( ['turning brightness down'] )
            self.SCREEN.AdjustBrightness( direction='down' )
        elif action == 'AutoDimOn':
            lw.log( ['turning autodim on'] )
            settings.autodim = True
        elif action == 'AutoDimOff':
            lw.log( ['turning autodim off'] )
            settings.autodim = False
        elif action == 'ScreenOn':
            lw.log( ['turning screen on'] )
            self.SCREEN.SetBrightness( brightness = self.STOREDBRIGHTNESS )
            self.SCREENSTATE = 'On'
        elif action == 'ScreenOff':
            lw.log( ['turning screen off'] )
            self.STOREDBRIGHTNESS = self.SCREEN.GetBrightness()
            self.SCREEN.SetBrightness( brightness = 11 )
            self.SCREENSTATE = 'Off'


    def _autodim( self, lightlevel ):
        if not settings.autodim or not lightlevel:
            return
        delta = int( (settings.maxdim - settings.mindim) / 3 )
        highdim = settings.maxdim - delta
        lowdim =  settings.mindim + delta
        delta = int( (settings.maxlevel - settings.minlevel) / 4 )
        highlevel = settings.maxlevel - delta
        midlevel =  settings.minlevel + (2 * delta)
        lowlevel = settings.minlevel + delta
        if lightlevel >= highlevel:
            lw.log( ['auto adjusting brightness to max of ' + str( settings.maxdim )] )
            self.SCREEN.SetBrightness( brightness = settings.maxdim )
        elif lightlevel >= midlevel:
            lw.log( ['auto adjusting brightness to high of ' + str( highdim )] )
            self.SCREEN.SetBrightness( brightness = highdim )
        elif lightlevel >= lowlevel:
            lw.log( ['auto adjusting brightness to low of ' + str( lowdim )] )
            self.SCREEN.SetBrightness( brightness = lowdim )
        else:
            lw.log( ['auto adjusting brightness to min of ' + str( settings.mindim )] )
            self.SCREEN.SetBrightness( brightness = settings.mindim )
            

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
                lw.log( ['setting backlight to 11'] )
                self.STOREDBRIGHTNESS = self.SCREEN.GetBrightness()
                self.SCREEN.SetBrightness( brightness = 0 )
                self.SCREENSTATE = 'Off'
            elif (abs( ondiff.total_seconds() ) < settings.readingdelta * 30):
                lw.log( ['setting backlight to original setting'] )
                self.SCREEN.SetBrightness( brightness = self.STOREDBRIGHTNESS )
                self.SCREENSTATE = 'On'
        return self.SCREENSTATE


    def _set_datetime( self, str_time ):
        tc = str_time.split( ':' )
        now = datetime.now()
        return datetime(year=now.year, month=now.month, day=now.day, hour=int( tc[0] ), minute=int( tc[1] ) )


    def _triggerscan( self ):
        if settings.trigger_kodi and ws_conn:
            lw.log( ['triggering Kodi update'] )
            ws.send( jsondata )



def RunInWebsockets():
    def on_message( ws, message ):
        lw.log( ['got back %s from Kodi' % message] )
        jm = _json.loads( message )
        if jm.get( 'method' ) == 'System.OnQuit':
            ws.close()
        elif jm.get( 'method' ) == 'Other.RPIWSL_VariablePass':
            action = jm.get( 'params', {} ).get( 'data', {} ).get( 'action' )
            if action:
                gs.HandleAction( action )
                
    def on_error( ws, error ):
        lw.log( ['got an error reading data from Kodi: ' + str( error )] )

    def on_open( ws ):
        lw.log( ['opening websocket connection to Kodi'] )

    def on_close( ws ):
        lw.log( ['closing websocket connection to Kodi'] )

    global should_quit
    global ws
    global ws_conn
    kodiurl = 'ws://%s:%s/jsponrpc' % (settings.kodiuri, settings.kodiwsport )
    ws = websocket.WebSocketApp( kodiurl, on_message = on_message, on_error = on_error, on_open = on_open, on_close = on_close )
    wst = Thread( target = ws.run_forever )
    wst.setDaemon( True )
    wst.start()
    should_quit = False
    try:
        conn_timeout = 5
        while not ws.sock.connected and conn_timeout:
            time.sleep( 1 )
            conn_timeout -= 1
        ws_conn = ws.sock.connected
    except AttributeError:
        ws_conn = False
    lw.log( ['websocket status: ' + str( ws_conn )] )
    try:
        while (not should_quit) and ws.sock.connected:
            gs.Run()
            lw.log( ['in websockets and waiting %s minutes before reading from sensor again' % str( settings.readingdelta )] )
            time.sleep( settings.readingdelta * 60 )
    except KeyboardInterrupt:
        should_quit = True
    except AttributeError:
        pass


if ( __name__ == "__main__" ):
    lw.log( ['script started'], 'info' )
    global should_quit
    global ws_conn
    should_quit = False
    ws_conn = False
    gs = Main()
    try:
        while not should_quit:
            if settings.trigger_kodi:
                for x in range( 1,6 ):
                    RunInWebsockets()
                    if ws_conn:
                        break
                    else:
                        lw.log( ['waiting 10 seconds then trying again'] )
                        time.sleep( 10 )
            if not should_quit:
                ws_conn = False
                gs.Run()
                lw.log( ['waiting %s minutes before reading from sensor again' % str( settings.readingdelta )] )
                time.sleep( settings.readingdelta * 60 )
    except KeyboardInterrupt:
        pass
    lw.log( ['script finished'], 'info' )


