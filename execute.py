# *  Credits:
# *
# *  v.1.1.0~beta11
# *  original RPi Weatherstation Lite code by pkscout

import data.config as config
import calendar, os, sys, time
from datetime import datetime
from threading import Thread
from collections import deque
from resources.common.xlogger import Logger
from resources.rpi.sensors import SenseHatSensors, SenseHatLED
from resources.rpi.screens import RPiTouchscreen
from resources.rpi.cameras import RPiCamera
if sys.version_info >= (2, 7):
    import json as _json
else:
    import simplejson as _json

p_folderpath, p_filename = os.path.split( os.path.realpath(__file__) )
lw = Logger( logfile = os.path.join( p_folderpath, 'data', 'logfile.log' ),
             numbackups = config.Get( 'logbackups' ), logdebug = str( config.Get( 'debug' ) ) )

try:
    import websocket
    trigger_kodi = True
except ImportError:
    lw.log( ['websocket-client not installed, so the script cannot trigger Kodi weather window updates'], 'info' )
    trigger_kodi = False



class Main:
    def __init__( self ):
        self.SENSOR = SenseHatSensors( testmode = config.Get( 'testmode' ) )
        self.SCREEN = RPiTouchscreen( testmode = config.Get( 'testmode' ) )
        self.CAMERA = RPiCamera( testmode = config.Get( 'testmode' ) )
        self.AUTODIM = config.Get( 'autodim' )
        self.STOREDBRIGHTNESS = self.SCREEN.GetBrightness()
        self.SCREENSTATE = 'On'
        self.PRESSUREHISTORY = deque()
        self.SUNRISE = ''
        self.SUNSET = ''
        self.DARKRUN = False
        self.LIGHTRUN = False


    def AutoDim( self ):
        while True:
            if self.AUTODIM and ws_conn:
                lw.log( ['checking autodim'] )
                lightlevel = self.CAMERA.LightLevel()
                lw.log( ['got back %s from camera' % str( lightlevel )] )
                css = self.SCREENSTATE
                do_dark = False
                do_light = False
                if lightlevel:
                    if lightlevel <= config.Get( 'dark' ):
                        do_dark = True
                    if lightlevel >= config.Get( 'light' ):
                        do_light = True
                if do_dark and not self.DARKRUN:
                    lw.log( ['dark trigger activated with ' + config.Get( 'specialtriggers' ).get( 'dark' )] )
                    self.HandleAction( config.Get( 'specialtriggers' ).get( 'dark' ) )
                    self.DARKRUN = True
                    self.LIGHTRUN = False
                elif do_light and not self.LIGHTRUN:
                    lw.log( ['light trigger activated with ' + config.Get( 'specialtriggers' ).get( 'light' )] )
                    self.HandleAction( config.Get( 'specialtriggers' ).get( 'light' ) )
                    self.DARKRUN = False
                    self.LIGHTRUN = True
                else:
                    triggers = config.Get( 'timedtriggers' )
                    triggers.append( [config.Get( 'fetchsuntime' ), 'GetSunriseSunset'] )
                    for onetrigger in triggers:
                        if onetrigger[0].lower() == 'sunrise':
                            onetrigger[0] = self.SUNRISE
                        if onetrigger[0].lower() == 'sunset':
                            onetrigger[0] = self.SUNSET
                        try:
                            checkdays = onetrigger[2]
                        except IndexError:
                            checkdays = ''
                        if self._is_time( onetrigger[0], checkdays = checkdays ):
                            lw.log( ['timed trigger %s activated with %s' % (onetrigger[0], onetrigger[1])] )
                            self.HandleAction( onetrigger[1] )
                if css <> self.SCREENSTATE:
                    self.SendJson( type = 'update', data = 'ScreenStatus:' + self.SCREENSTATE )
            time.sleep( config.Get( 'autodimdelta' ) * 60 )


    def GetSensorData( self, ledcolor=(255, 255, 255) ):
        config.Reload()
        led.PixelOn( 0, 0, ledcolor )
        temperature = self.SENSOR.Temperature()
        humidity = self.SENSOR.Humidity()
        pressure = self.SENSOR.Pressure()
        s_data = []
        if temperature is not None:
            s_data.append( 'IndoorTemp:' + self._reading_to_str( temperature ) )
        if humidity is not None:
            s_data.append( 'IndoorHumidity:' + self._reading_to_str( humidity ) )
        if pressure is not None:
            s_data.append( 'IndoorPressure:' + self._reading_to_str( pressure ) )
            s_data.append( 'PressureTrend:' + self._get_pressure_trend( pressure ) )
        d_str = ''
        for item in s_data:
            d_str = '%s;%s' % (d_str, item)
        d_str = d_str[1:]
        lw.log( ['sensor data: ' + d_str] )
        if d_str:
            led.Sweep( start = 1, color = ledcolor, vertical = True )
            self.SendJson( type = 'update', data = d_str )



    def HandleAction( self, action ):
        action = action.lower()
        if action == 'brightnessup' and self.SCREENSTATE == 'On':
            self.SCREEN.AdjustBrightness( direction='up' )
            lw.log( ['turned brightness up'] )
        elif action == 'brightnessdown' and self.SCREENSTATE == 'On':
            self.SCREEN.AdjustBrightness( direction='down' )
            lw.log( ['turned brightness down'] )
        elif action == 'autodimon':
            self.AUTODIM = True
            lw.log( ['turned autodim on'] )
        elif action == 'autodimoff':
            self.AUTODIM = False
            lw.log( ['turned autodim off'] )
        elif action.startswith( 'screenon' ) and self.SCREENSTATE == 'Off':
            sb = action.split( ':' )
            try:
                brightness = sb[1]
            except IndexError:
                brightness = self.STOREDBRIGHTNESS
            self.SCREEN.SetBrightness( brightness = brightness )
            self.SCREENSTATE = 'On'
            lw.log( ['turned screen on to brightness of ' + str( brightness )] )
        elif action == 'screenoff' and self.SCREENSTATE == 'On':
            self.STOREDBRIGHTNESS = self.SCREEN.GetBrightness()
            self.SCREEN.SetBrightness( brightness = 11 )
            self.SCREENSTATE = 'Off'
            lw.log( ['turned screen off and saved brightness as ' + str( self.STOREDBRIGHTNESS )] )
        elif action.startswith( 'brightness:' ):
            try:
                level = int( action.split(':')[1] )
            except ValueError:
                level = None
            if level:
                if  self.SCREENSTATE == 'On':
                    self.SCREEN.SetBrightness( brightness = level )
                    lw.log( ['set brightness to ' + str( level )] )
                else:
                    self.STOREDBRIGHTNESS = level
                    lw.log( ['screen is off, so set stored brightness to ' + str( level )] )
        elif action == 'getsunrisesunset':
            self.SetSunRiseSunset()


    def SendJson( self, type, data ):
        jdata = None
        if type.lower() == 'update':
            jsondict = { 'id':'1', 'jsonrpc':'2.0', 'method':'Addons.ExecuteAddon',
                         'params':{'addonid':'script.weatherstation.lite','params':{'action':'updatekodi',
                         'plugin':'rpi-weatherstation-lite','data':data}} }
        elif type.lower() == 'infolabelquery':
            jsondict = { 'id':'2', 'jsonrpc':'2.0',  'method':'XBMC.GetInfoLabels',
                         'params':{'labels':data} }
            kodiquery = _json.dumps( jsondict )
        if trigger_kodi and ws_conn and jsondict:
            jdata = _json.dumps( jsondict )
            lw.log( ['sending Kodi ' + jdata] )
            ws.send( jdata )


    def SetSunRiseSunset( self, jsonresult = {} ):
        if jsonresult:
            self.SUNRISE = self._convert_to_24_hour( jsonresult.get( 'Window(Weather).Property(Today.Sunrise)' ) )
            self.SUNSET = self._convert_to_24_hour( jsonresult.get( 'Window(Weather).Property(Today.Sunset)' ) )
            lw.log( ['set sunrise to %s and sunset to %s' % (self.SUNRISE, self.SUNSET)] )
        else:
            if not self.AUTODIM:
                return
            lw.log( ['getting sunrise and sunset times from Kodi'] )
            self.SendJson( type = 'infolabelquery',
                           data = ['Window(Weather).Property(Today.Sunrise)', 'Window(Weather).Property(Today.Sunset)'] )


    def _convert_to_24_hour( self, timestr ):
        time_split = timestr.split( ' ' )
        if time_split[1] == 'AM':
            return time_split[0]
        else:
            hm = time_split[0].split( ':' )
            hour = str( int( hm[0] ) + 12 )
            return '%s:%s' % (hour, hm[1])


    def _get_pressure_trend( self, current_pressure ):
        self.PRESSUREHISTORY.append( current_pressure )
        if len( self.PRESSUREHISTORY ) > config.Get( 'pressuredelta' ) / config.Get( 'readingdelta' ):
            self.PRESSUREHISTORY.popleft()
        previous_pressure = self.PRESSUREHISTORY[0]
        diff = current_pressure - previous_pressure
        if diff < 0:
            direction = 'falling'
        else:
            direction = 'rising'
        if abs( diff ) >= config.Get( 'pressurerapid' ):
            return 'rapidly ' + direction
        elif abs( diff ) >= config.Get( 'pressureregular' ):
            return direction
        return 'steady'

    
    def _is_time( self, thetime, checkdays='' ):
        action_time = self._set_datetime( thetime )
        if not action_time:
            return False
        elif checkdays.lower().startswith( 'weekday' ) and not calendar.day_name[action_time.weekday()] in config.Get( 'weekdays' ):
            return False
        elif checkdays.lower().startswith( 'weekend' ) and not calendar.day_name[action_time.weekday()] in config.Get( 'weekend' ):
            return False  
        rightnow = datetime.now()
        action_diff = rightnow - action_time
        if abs( action_diff.total_seconds() ) < config.Get( 'autodimdelta' ) * 30: # so +/- window is total' ) readingdelta
            return True
        else:
            return False


    def _reading_to_str( self, reading ):
        return str( int( round( reading ) ) )


    def _set_datetime( self, str_time ):
        tc = str_time.split( ':' )
        now = datetime.now()
        try:
            fulldate = datetime( year = now.year, month = now.month, day = now.day, hour = int( tc[0] ), minute = int( tc[1] ) )
        except ValueError:
            fulldate = None
        return fulldate



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
        elif jm.get( 'id' ) == '2':
            gs.SetSunRiseSunset( jsonresult = jm.get( 'result' ) )
                
    def on_error( ws, error ):
        lw.log( ['got an error reading data from Kodi: ' + str( error )] )

    def on_open( ws ):
        lw.log( ['opening websocket connection to Kodi'] )

    def on_close( ws ):
        lw.log( ['closing websocket connection to Kodi'] )
        global ws_conn
        ws_conn = False

    global should_quit
    global ws
    global ws_conn
    kodiurl = 'ws://%s:%s/jsponrpc' % (config.Get( 'kodiuri' ), config.Get( 'kodiwsport' ) )
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
        if ws.sock.connected:
            gs.SetSunRiseSunset()
        gs.SendJson( type = 'update', data = 'AutoDim:' + str( config.Get( 'autodim' ) ) )
        while (not should_quit) and ws.sock.connected:
            gs.GetSensorData( ledcolor = led.Color( config.Get( 'kodi_connection' ) ) )
            lw.log( ['in websockets and waiting %s minutes before reading from sensor again' % str( config.Get( 'readingdelta' ) )] )
            time.sleep( config.Get( 'readingdelta' ) * 60 )
    except KeyboardInterrupt:
        should_quit = True
    except AttributeError:
        pass


if ( __name__ == "__main__" ):
    lw.log( ['script started', 'debugging set to ' + str( config.Get( 'debug') ) ], 'info' )
    global should_quit
    global ws_conn
    should_quit = False
    ws_conn = False
    firstrun = True
    led = SenseHatLED()
    led.PixelOn( 0, 7, led.Color( config.Get( 'script_running' ) ) )
    led.PixelOn( 0, 0, led.Color( config.Get( 'no_kodi_connection' ) ) )
    gs = Main()
    adt = Thread( target = gs.AutoDim )
    adt.setDaemon( True )
    adt.start()
    try:
        while not should_quit:
            if trigger_kodi:
                for x in range( 1,6 ):
                    RunInWebsockets()
                    if ws_conn or not firstrun:
                        break
                    else:
                        lw.log( ['no connection to Kodi, waiting 10 seconds then trying again'] )
                        time.sleep( 10 )
            if not should_quit:
                ws_conn = False
                gs.GetSensorData( ledcolor = led.Color( config.Get( 'no_kodi_connection' ) ) )
                lw.log( ['waiting %s minutes before reading from sensor again' % str( config.Get( 'readingdelta' ) )] )
                firstrun = False
                time.sleep( config.Get( 'readingdelta' ) * 60 )
    except KeyboardInterrupt:
        pass
    led.ClearPanel()
    lw.log( ['script finished'], 'info' )


