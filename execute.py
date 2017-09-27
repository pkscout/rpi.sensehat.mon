# *  Credits:
# *
# *  v.0.1.2
# *  original RPi Weatherstation Lite code by pkscout

import os, sys, time
from subprocess import Popen, PIPE
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
    settings.changescreen
    settings.screenofftime
    settings.screenontime
    settings.convertjoystick
    settings.reverselr
    settings.lh_threshold
    settings.keymap
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
    def __init__( self ):
        self.SENSOR = ReadSenseHAT( testmode = settings.testmode )
        self.SCREEN = RPiTouchscreen( testmode = settings.testmode )
        self.CAMERA = RPiCamera( testmode = settings.testmode )


    def Run( self ):
        sensordata.log( [self._read_sensor()] )
        TriggerScan()
        

    def _read_sensor( self ):
        raw_temp = self.SENSOR.Temperature()
        # if the SenseHAT is too close to the RPi CPU, it reads hot. This corrects that
        t = os.popen('/opt/vc/bin/vcgencmd measure_temp')
        cpu_temp = t.read()
        cpu_temp = cpu_temp.replace('temp=','')
        cpu_temp = cpu_temp.replace('\'C\n','')
        cpu_temp = float(cpu_temp)
        if settings.adjusttemp and raw_temp:
            adjusted_temp = raw_temp - ((cpu_temp - raw_temp)/2)
        else:
            adjusted_temp = raw_temp
        raw_humidity = self.SENSOR.Humidity()
        lw.log( ['raw_h: %s raw_t: %s' % (str( raw_humidity ), str( raw_temp ))] )
        if settings.adjusttemp and raw_humidity:
            dewpoint = raw_temp - ((100 - raw_humidity) / 5)
            temp_h = 100 - 5 * (raw_temp - dewpoint)
            lw.log( ['recalcuated humidity: ' + str( temp__h )] )
            humidity = self.reading_to_str( 100 - 5 * (adjusted_temp - dewpoint) )
        else:
            humidity = self._reading_to_str( self.SENSOR.Humidity() )
        temperature = self._reading_to_str( adjusted_temp )
        pressure = self._reading_to_str( self.SENSOR.Pressure() )
        if temperature == '0' and humidity == '0' and pressure == '0':
            datastr = ''
        else:
            autodim = str( settings.autodim )
            datastr = '\tIndoorTemp:%s\tIndoorHumidity:%s\tIndoorPressure:%s\tAutoDim:%s' % (temperature, humidity, pressure, autodim)
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



def CheckPassback():
    def _set_autodim():
        settings.autodim = not settings.autodim
        autodim_str = str( settings.autodim )
        lw.log( ['AutoDim has been set to ' + autodim_str] )
        sensordata.log( ['\tAutoDim:' +  autodim_str] )
        TriggerScan()

    past = passback.xljoystick
    while True:
        current = passback.xljoystick
        if past != current:
            lw.log( ['xljoystick has changed to ' + current] )
            if current == 'up':
                _set_autodim()
            past = current
        time.sleep(1)
 

def TriggerScan():
    if settings.trigger_kodi and ws_conn:
        lw.log( ['triggering Kodi update'] )
        ws.send( jsondata )


def RunInWebsockets():
    def on_message( ws, message ):
        lw.log( ['got back %s from Kodi' % message] )
        if 'System.OnQuit' in message:
            ws.close()

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


def SpawnThreads():
    if settings.convertjoystick:
        # create and start a separate thread to monitor the joystick and convert to keyboard presses
        cj = ConvertJoystickToKeypress( keymap = settings.keymap,
                                        reverselr = settings.reverselr,
                                        lh_threshold = settings.lh_threshold,
                                        testmode = settings.testmode )
        t1 = Thread( target = CheckPassback )
        t1.setDaemon( True )
        t1.start()
        t1 = Thread( target = cj.Convert )
        t1.setDaemon( True )
        t1.start()
                     

if ( __name__ == "__main__" ):
    lw.log( ['script started'], 'info' )
    global should_quit
    global ws_conn
    should_quit = False
    ws_conn = False
    gs = Main()
    SpawnThreads()
    try:
        while not should_quit:
            if settings.trigger_kodi:
                RunInWebsockets()
            if not should_quit:
                ws_conn = False
                gs.Run()
                lw.log( ['waiting %s minutes before reading from sensor again' % str( settings.readingdelta )] )
                time.sleep( settings.readingdelta * 60 )
    except KeyboardInterrupt:
        pass
    lw.log( ['script finished'], 'info' )


