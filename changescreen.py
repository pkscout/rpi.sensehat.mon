# *  Credits:
# *
# *  v.0.0.1
# *  original RPi Screen Change code by pkscout

import argparse, os
from ConfigParser import *
from resources.common.xlogger import Logger
from resources.screencontrol import RPiTouchscreen

p_folderpath, p_filename = os.path.split( os.path.realpath(__file__) )
lw = Logger( logfile = os.path.join( p_folderpath, 'data', 'cs-logfile.log' ) )



class Main:
    def __init__( self ):
        self._parse_argv()
        rpit = RPiTouchscreen()
        if self.ARGS.on:
            try:
                brightness = int( self.ARGS.brightness )
            except ValueError:
                brightness = 0
            lw.log( ['turning display on with brightness of %s' % str( brightness )] )
            rpit.Power( switch='on', brightness=brightness )                
        elif self.ARGS.off:
            lw.log( ['turning display off'] )
            rpit.Power( switch='off' )
        elif self.ARGS.brightness:
            lw.log( ['setting brightness to ' + self.ARGS.brightness] )
            rpit.SetBrightness( brightness=self.ARGS.brightness )
        

    def _parse_argv( self ):
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group()
        group.add_argument( "-n", "--on", help="turn the RPi touchscreen display on", action="store_true" )
        group.add_argument( "-f", "--off", help="turn the RPi touchscreen display off", action="store_true" )
        parser.add_argument( "-b", "--brightness", help="set the RPi touchscreen to given brightness" )
        self.ARGS = parser.parse_args()



if ( __name__ == "__main__" ):
    lw.log( ['script started'], 'info' )
    Main()
lw.log( ['script finished'], 'info' )