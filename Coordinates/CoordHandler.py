# author David Sanchez
# david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
try :
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    from astropy.coordinates import ICRS, Galactic, FK4, FK5 
except :
    raise(RuntimeError( "no astropy module found"))
import numpy
# ------------------------------ #

class CoordinatesHandler():
    def __init__(self,x,y, frame = FK5):
        '''init function'''
        self.frame = frame
        try :
            self.skycoord = SkyCoord(x, y, frame=frame)
        except:
            self.skycoord = SkyCoord(x*u.degree, y*u.degree, frame=frame)
            
        try :
            self.X = self.skycoord.ra
            self.Y = self.skycoord.dec
        except:
            self.X = self.skycoord.l
            self.Y = self.skycoord.b
            
        self.to_string = self.skycoord.to_string

        self.to_string = self.skycoord.to_string
        self.frame = self.skycoord.frame.name
    
    @classmethod
    def fromName(cls, name, frame = FK5):
        c = SkyCoord.from_name(name,frame)
        return cls(c.ra,c.dec,frame)

    def ToGalactic(self):
        return self.skycoord.galactic

    def ToFK4(self):
        return self.skycoord.fk4

    def ToFK5(self):
        return self.skycoord.fk5
        
    def ToICRS(self):
        return self.skycoord.icrs
    
    def ChangeFrame(self,frame):
        '''frame is a astropy.coordinates: ICRS, Galactic, FK4 or FK5 '''
        self.skycoord = self.skycoord.transform_to(frame)
        self.frame = frame

