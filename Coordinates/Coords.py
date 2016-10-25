

# ------ Imports --------------- #
from kapteyn import wcs
import numpy
# ------------------------------ #

class Coordinates():
    def __init__(self,x,y,sky_system = 'Equatorial',ref_system = 'J2000'):
        '''init function'''
        self.x = x
        self.y = y
        self.sys = sky_system+' '+ref_system
    
    def ToGalactic(self):
        trans = wcs.Transformation(self.sys,wcs.galactic)
        print  trans.transform((self.x,self.y))
        
    def ToEcliptic(self):
        trans = wcs.Transformation(self.sys,wcs.ecliptic)
        print  trans.transform((self.x,self.y))


if __name__ == '__main__':

    coords = Coordinates(329.716938,-30.225588)
    coords.ToGalactic()
    coords.ToEcliptic()

