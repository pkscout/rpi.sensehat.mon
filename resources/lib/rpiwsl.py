
import resources.config as config
import calendar, json, os, time
from datetime import datetime
from threading import Thread
from collections import deque
from resources.lib.sensors import BME280Sensors, SenseHatSensors
from resources.lib.screens import RPiTouchscreen, SenseHatLED
from resources.lib.cameras import AmbientSensor, RPiCamera
from resources.lib.xlogger import Logger
try:
    import websocket
    has_websockets = True
except ImportError:
    has_websockets = False

KODIACTIONMAP = ['Screen Off', 'ScreenOn:10', 'ScreenOn:20', 'ScreenOn:30', 'ScreenOn:40',
                 'ScreenOn:50', 'ScreenOn:60', 'ScreenOn:70', 'ScreenOn:80', 'ScreenOn:90',
                 'ScreenOn:100', 'None']
KODIDAYMAP    = ['', 'Weekdays', 'Weekend']


class Main:
    def __init__( self, thepath ):
        self.LW = Logger( logfile=os.path.join( os.path.dirname( thepath ), 'data', 'logs', 'logfile.log' ),
                          numbackups = config.Get( 'logbackups' ), logdebug = str( config.Get( 'debug' ) ) )
        self.LW.log( ['script started', 'websockets is %s' % str( has_websockets ) ], 'info' )
        self._init_vars()
        adt = Thread( target = self._auto_dim )
        adt.setDaemon( True )
        adt.start()
        while not self.SHOULDQUIT:
            if has_websockets:
                for x in range( 1,6 ):
                    self._run_in_websockets()
                    if self.WSCONN or not self.FIRSTRUN:
                        break
                    else:
                        self.LW.log( ['no connection to Kodi, waiting 10 seconds then trying again'] )
                        self._sleep( 10 )
            if not self.SHOULDQUIT:
                self.WSCONN = False
                self._get_sensor_data( ledcolor = self.LED.Color( config.Get( 'no_kodi_connection' ) ) )
                self.LW.log( ['waiting %s minutes before reading from sensor again' % str( self.READINGDELTA )] )
                self.FIRSTRUN = False
                self._sleep( self.READINGDELTA * 60 )
        self._send_json( thetype = 'update', data = 'IndoorTemp:None;IndoorHumidity:None;IndoorPressure:None;PressureTrend:None' )
        self.LED.ClearPanel()
        self.LW.log( ['script finished'], 'info' )
    

    def _init_vars( self ):
        self._update_shared_settings()
        self.SHOULDQUIT = False
        self.WSCONN = False
        self.FIRSTRUN = True
        self.SENSOR = self._pick_sensor()
        self.CAMERA = self._pick_camera()
        self.SCREEN = self._pick_screen()
        self.READINGDELTA = config.Get( 'readingdelta' )
        self.STOREDBRIGHTNESS = self.SCREEN.GetBrightness()
        self.SCREENSTATE = 'On'
        self.PRESSUREHISTORY = deque()
        self.SUNRISE = ''
        self.SUNSET = ''
        self.DARKRUN = False
        self.BRIGHTRUN = False
        self.DIMRUN = False
        self.LED = SenseHatLED()
        self.LED.PixelOn( 0, 7, self.LED.Color( config.Get( 'script_running' ) ) )
        self.LED.PixelOn( 1, 7, self.LED.Color( config.Get( 'no_kodi_connection' ) ) )
        self._set_brightness_bar()


    def _update_shared_settings( self, thedata=None ):
        if thedata:
            self._map_returned_settings( thedata )
        else:
            self._get_config_settings()
        self.LW.log( ['shared variables initialized'] )


    def _get_config_settings( self ):
        self.FIXEDBRIGHTNESS = 0
        self.AUTODIM = config.Get( 'autodim' )
        self.DARKACTION = config.Get( 'specialtriggers' ).get( 'dark' )
        self.DIMACTION = config.Get( 'specialtriggers' ).get( 'dim' )
        self.BRIGHTACTION = config.Get( 'specialtriggers' ).get( 'bright' )
        self.DARKTHRESHOLD = config.Get( 'dark' )
        self.BRIGHTTHRESHOLD = config.Get( 'bright' )
        self.TIMEDTRIGGERS = config.Get( 'timedtriggers' )


    def _map_returned_settings( self, thedata ):
        self.FIXEDBRIGHTNESS = thedata.get( 'fixed_brightness' )
        self.AUTODIM = thedata.get( 'auto_dim', True )
        self.DARKACTION = KODIACTIONMAP[thedata.get( 'dark_action', 0 )]
        self.DIMACTION = KODIACTIONMAP[thedata.get( 'dim_action', 4 )]
        self.BRIGHTACTION = KODIACTIONMAP[thedata.get( 'bright_action', 10 )]
        self.DARKTHRESHOLD = thedata.get( 'dark_threshold', 5 )
        self.BRIGHTTHRESHOLD = thedata.get( 'bright_threshold', 80 )
        self.TIMEDTRIGGERS = []
        self.TIMEDTRIGGERS.append( ['sunrise',
                                     KODIACTIONMAP[thedata.get( 'sunrise_action', 11 )],
                                     KODIDAYMAP[thedata.get( 'sunrise_days', 0 )]] )
        self.TIMEDTRIGGERS.append( ['sunset',
                                     KODIACTIONMAP[thedata.get( 'sunset_action', 11 )],
                                     KODIDAYMAP[thedata.get( 'sunset_days', 0 )]] )
        self.TIMEDTRIGGERS.append( [ thedata.get( 'timed_one', '00:00' ),
                                     KODIACTIONMAP[thedata.get( 'timed_one_action', 11 )],
                                     KODIDAYMAP[thedata.get( 'timed_one_days', 0 )]] )
        self.TIMEDTRIGGERS.append( [ thedata.get( 'timed_two', '00:00' ),
                                     KODIACTIONMAP[thedata.get( 'timed_two_action', 11 )],
                                     KODIDAYMAP[thedata.get( 'timed_two_days', 0 )]] )
        self.TIMEDTRIGGERS.extend( config.Get( 'timedtriggers' ) )

    def _auto_dim( self ):
        while True:
            if self.AUTODIM and self.WSCONN and not self.SHOULDQUIT:
                self.LW.log( ['checking autodim'] )
                lightlevel = self.CAMERA.LightLevel()
                self.LW.log( ['got back %s from light sensor' % str( lightlevel )] )
                css = self.SCREENSTATE
                do_dark = False
                do_bright = False
                do_dim = False
                if lightlevel:
                    if lightlevel <= self.DARKTHRESHOLD:
                        do_dark = True
                    elif lightlevel <= self.BRIGHTTHRESHOLD:
                        do_dim = True
                    else:
                        do_bright = True
                if do_dark and not self.DARKRUN:
                    self.LW.log( ['dark trigger activated with ' + self.DARKACTION] )
                    self._handle_action( self.DARKACTION )
                    self.DARKRUN = True
                    self.BRIGHTRUN = False
                    self.DIMRUN = False
                elif do_bright and not self.BRIGHTRUN:
                    self.LW.log( ['bright trigger activated with ' + self.BRIGHTACTION] )
                    self._handle_action( self.BRIGHTACTION )
                    self.DARKRUN = False
                    self.BRIGHTRUN = True
                    self.DIMRUN = False
                elif do_dim and not self.DIMRUN:
                    self.LW.log( ['dim trigger activated with ' + self.DIMACTION] )
                    self._handle_action( self.DIMACTION )
                    self.DARKRUN = False
                    self.BRIGHTRUN = False
                    self.DIMRUN = True
                if self._is_time( config.Get( 'fetchsuntime' ) ):
                    self.LW.log( ['getting updated sunrise and sunset times'] )
                    self._handle_action( 'GetSunriseSunset' )
                else:
                    triggers = self.TIMEDTRIGGERS
                    for onetrigger in triggers:
                        if onetrigger[0].lower() == 'sunrise':
                            onetrigger[0] = self.SUNRISE
                        if onetrigger[0].lower() == 'sunset':
                            onetrigger[0] = self.SUNSET
                        try:
                            checkdays = onetrigger[2]
                        except IndexError:
                            checkdays = ''
                        if self._is_time( onetrigger[0], checkdays=checkdays ):
                            self.LW.log( ['timed trigger %s activated with %s' % (onetrigger[0], onetrigger[1])] )
                            self._handle_action( onetrigger[1] )
#                if css != self.SCREENSTATE:
#                    self._send_json( thetype = 'update', data = 'ScreenStatus:' + self.SCREENSTATE )
            self._sleep( config.Get( 'autodimdelta' ) * 60 )


    def _get_sensor_data( self, ledcolor=(255, 255, 255) ):
        config.Reload()
        temperature = self.SENSOR.Temperature()
        humidity = self.SENSOR.Humidity()
        pressure = self.SENSOR.Pressure()
        pressuretrend = self.SENSOR.PressureTrend()
        s_data = []
        s_data.append( 'IndoorTemp:' + self._reading_to_str( temperature ) )
        s_data.append( 'IndoorHumidity:' + self._reading_to_str( humidity ) )
        s_data.append( 'IndoorPressure:' + self._reading_to_str( pressure ) )
        if pressuretrend:
            s_data.append( 'PressureTrend:' + pressuretrend )
        else:
            s_data.append( 'PressureTrend:' + self._get_pressure_trend( pressure ) )
        d_str = ''
        for item in s_data:
            d_str = '%s;%s' % (d_str, item)
        d_str = d_str[1:]
        self.LW.log( ['sensor data: ' + d_str] )
        self.LED.Sweep( anchor = 7, start = 1, color = ledcolor )
        self.LED.PixelOn( 1, 7, ledcolor )
        self._send_json( thetype = 'update', data = d_str )


    def _handle_action( self, action ):
        action = action.lower()
        if action == 'brightnessup' and self.SCREENSTATE == 'On':
            self.SCREEN.AdjustBrightness( direction='up' )
            self.LW.log( ['turned brightness up'] )
        elif action == 'brightnessdown' and self.SCREENSTATE == 'On':
            self.SCREEN.AdjustBrightness( direction='down' )
            self.LW.log( ['turned brightness down'] )
        elif action == 'autodimon':
            self.AUTODIM = True
            self.LW.log( ['turned autodim on'] )
        elif action == 'autodimoff':
            self.AUTODIM = False
            self.LW.log( ['turned autodim off'] )
        elif action.startswith( 'screenon' ):
            sb = action.split( ':' )
            try:
                brightness = sb[1]
            except IndexError:
                brightness = self.STOREDBRIGHTNESS
            self.SCREEN.SetBrightness( brightness=brightness )
            self.SCREENSTATE = 'On'
            self.LW.log( ['turned screen on to brightness of ' + str( brightness )] )
            if self.DIMRUN and self.BRIGHTRUN:
                self.DARKRUN = False
                self.DIMRUN = False
                self.BRIGHTRUN = False
        elif action == 'screenoff' and self.SCREENSTATE == 'On':
            self.STOREDBRIGHTNESS = self.SCREEN.GetBrightness()
            self.SCREEN.SetBrightness( brightness=0 )
            self.SCREENSTATE = 'Off'
            self.LW.log( ['turned screen off and saved brightness as ' + str( self.STOREDBRIGHTNESS )] )
            if not self.DARKRUN:
                self.DARKRUN = True
                self.DIMRUN = True
                self.BRIGHTRUN = True
        elif action.startswith( 'brightness:' ):
            try:
                level = int( action.split(':')[1] )
            except ValueError:
                level = None
            if level:
                if  self.SCREENSTATE == 'On':
                    self.SCREEN.SetBrightness( brightness=level )
                    self.LW.log( ['set brightness to ' + str( level )] )
                else:
                    self.STOREDBRIGHTNESS = level
                    self.LW.log( ['screen is off, so set stored brightness to ' + str( level )] )
        elif action == 'getsunrisesunset':
            self._set_sunrise_sunset()
        self._set_brightness_bar()


    def _send_json( self, thetype, data ):
        jdata = None
        ac = 1
        if thetype.lower() == 'update':
            jsondict = { "id": 1, "jsonrpc": "2.0", "method": "JSONRPC.NotifyAll",
                         "params": {"sender": "Weatherstation", "message": "RPIWSL_VariablePass", "data": data} }
        elif thetype.lower() == 'infolabelquery':
            jsondict = { 'id':'2', 'jsonrpc':'2.0',  'method':'XBMC.GetInfoLabels',
                         'params':{'labels':data} }
        elif thetype.lower() == 'requestsettings':
            jsondict = { "id": 1, "jsonrpc": "2.0", "method": "JSONRPC.NotifyAll",
                         "params": {"sender": "Weatherstation", "message": "RPIWSL_SettingsRequest", "data": data} }
        if has_websockets and self.WSCONN and jsondict:
            jdata = json.dumps( jsondict )
            if self.WSCONN:
                self.LW.log( ['sending Kodi ' + jdata] )
                self.WS.send( jdata )


    def _set_brightness_bar( self ):
        self.LED.SetBar( level=self.SCREEN.GetBrightness(), anchor=6, themin=25, themax=225,
                         color=self.LED.Color( config.Get( 'brightness_bar' ) ) )


    def _set_sunrise_sunset( self, jsonresult=None ):
        if jsonresult:
            self.SUNRISE = self._convert_to_24_hour( jsonresult.get( 'Window(Weather).Property(Today.Sunrise)' ) )
            self.SUNSET = self._convert_to_24_hour( jsonresult.get( 'Window(Weather).Property(Today.Sunset)' ) )
            self.LW.log( ['set sunrise to %s and sunset to %s' % (self.SUNRISE, self.SUNSET)] )
        else:
            if not self.AUTODIM:
                return
            self.LW.log( ['getting sunrise and sunset times from Kodi'] )
            self._send_json( thetype = 'infolabelquery',
                           data = ['Window(Weather).Property(Today.Sunrise)', 'Window(Weather).Property(Today.Sunset)'] )


    def _run_in_websockets( self ):
        def on_message( ws, message ):
            self.LW.log( ['got back %s from Kodi' % message] )
            jm = json.loads( message )
            if jm.get( 'id' ) == '2':
                self._set_sunrise_sunset( jsonresult=jm.get( 'result' ) )
            elif jm.get( 'method' ) == 'System.OnQuit':
                self.WS.close()
            elif jm.get( 'method' ) == 'Other.ReturningSettings':
                self._update_shared_settings( thedata=jm.get( 'params', {} ).get( 'data' ) )

        def on_error( ws, error ):
            self.LW.log( ['got an error reading data from Kodi: ' + str( error )] )

        def on_open( ws ):
            self.LW.log( ['opening websocket connection to Kodi'] )

        def on_close( ws ):
            self.LW.log( ['closing websocket connection to Kodi'] )
            self.WSCONN = False
        self.WS = websocket.WebSocketApp( 'ws://%s:%s/jsponrpc' % (config.Get( 'kodiuri' ), config.Get( 'kodiwsport' ) ),
                                          on_message=on_message, on_error=on_error,
                                          on_open=on_open, on_close=on_close )
        wst = Thread( target = self.WS.run_forever )
        wst.setDaemon( True )
        wst.start()
        self.SHOULDQUIT = False
        try:
            conn_timeout = 5
            while not self.WS.sock.connected and conn_timeout and not self.SHOULDQUIT:
                self._sleep( 1 )
                conn_timeout -= 1
            self.WSCONN = self.WS.sock.connected
        except AttributeError:
            self.WSCONN = False
        self.LW.log( ['websocket status: ' + str( self.WSCONN )] )
        if self.WSCONN:
            self.LED.PixelOn( 1, 7, self.LED.Color( config.Get( 'kodi_connection' ) ) )
            self._set_sunrise_sunset()
            self._send_json( thetype='requestsettings', data='all' )
            self._send_json( thetype='update', data='ScreenStatus:%s' % self.SCREENSTATE )
        while (not self.SHOULDQUIT) and self.WSCONN:
            self._get_sensor_data( ledcolor=self.LED.Color( config.Get( 'kodi_connection' ) ) )
            self.LW.log( ['in websockets and waiting %s minutes before reading from sensor again' % str( config.Get( 'readingdelta' ) )] )
            self._sleep( config.Get( 'readingdelta' ) * 60 )


    def _sleep( self, total_wait ):
        wait = 0
        sleeptime = 5
        if total_wait < sleeptime:
            sleeptime = total_wait
        while wait < total_wait:
            try:
                time.sleep( sleeptime )
            except KeyboardInterrupt:
                self.SHOULDQUIT = True
                return
            wait = wait + sleeptime


    def _convert_to_24_hour( self, timestr ):
        time_split = timestr.split( ' ' )
        if time_split[1] == 'AM':
            return time_split[0]
        else:
            hm = time_split[0].split( ':' )
            hour = str( int( hm[0] ) + 12 )
            return '%s:%s' % (hour, hm[1])


    def _get_pressure_trend( self, current_pressure ):
        if current_pressure is None:
            return 'steady'
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


    def _pick_camera( self ):
        if config.Get( 'which_camera' ).lower() == 'pi':
            return RPiCamera( testmode = config.Get( 'testmode' ) )
        else:
            return AmbientSensor( port = config.Get( 'i2c_port' ), address = config.Get( 'ambient_address' ),
                                  cmd = config.Get( 'ambient_cmd' ), oversample = config.Get( 'ambient_oversample'),
                                  testmode = config.Get( 'testmode' ) )


    def _pick_screen( self ):
        return RPiTouchscreen( testmode = config.Get( 'testmode' ) )


    def _pick_sensor( self ):
        if config.Get( 'which_sensor' ).lower() == 'sensehat':
            return SenseHatSensors( adjust = config.Get( 'sensehat_adjust' ), factor = config.Get( 'sensehat_factor' ),
                                           testmode = config.Get( 'testmode' ) )
        else:
            return BME280Sensors( port = config.Get( 'i2c_port' ), address = config.Get( 'bme280_address' ),
                                         sampling = config.Get( 'bme280_sampling' ), adjust = config.Get( 'bme280_adjust'),
                                         testmode = config.Get( 'testmode' ) )


    def _reading_to_str( self, reading ):
        return str( reading )


    def _set_datetime( self, str_time ):
        tc = str_time.split( ':' )
        now = datetime.now()
        try:
            fulldate = datetime( year = now.year, month = now.month, day = now.day, hour = int( tc[0] ), minute = int( tc[1] ) )
        except ValueError:
            fulldate = None
        return fulldate



