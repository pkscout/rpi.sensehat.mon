# *  Credits:
# *
# *  v.0.0.1
# *  original RPi Screen Change code by pkscout

import argparse, os
from ConfigParser import *
from resources.rpi.screens import RPiTouchscreen



class Main:
    def __init__( self ):
        self._parse_argv()
        rpit = RPiTouchscreen()
        if self.ARGS.brightness:
            rpit.SetBrightness( brightness=self.ARGS.brightness )
        

    def _parse_argv( self ):
        parser = argparse.ArgumentParser()
        parser.add_argument( "-b", "--brightness", help="set the RPi touchscreen to given brightness" )
        self.ARGS = parser.parse_args()



if ( __name__ == "__main__" ):
    Main()
