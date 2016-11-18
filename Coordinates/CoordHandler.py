"""
class to handle the coordinates. 
astropy module is mandatory
author David Sanchez  david.sanchez@lapp.in2p3.fr
"""

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
    ''' Class to handler coordinate'''
    def __init__(self,x,y, frame = FK5):
        ''' init function
        Parameters
        ---------
        x  : float, first coordinate of the source
        f  : float, second coordinate of the source
        frame   : Astropy coordinate frame ICRS, Galactic, FK4, FK5 , see astropy for more information
        '''
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
        ''' return a CoordinatesHandler object based on a name of a source
        Parameters
        ----------
        name    : catalog name (see astropy manual for the valid names)
        frame   : Astropy coordinate frame ICRS, Galactic, FK4, FK5 , see astropy for more information
        '''
        c = SkyCoord.from_name(name,frame)
        return cls(c.ra,c.dec,frame)

    def ToGalactic(self):
        '''
        return the coordinate in the Galactic frame
        '''
        return self.skycoord.galactic

    def ToFK4(self):
        '''
        return the coordinate in the FK4 frame
        '''
        return self.skycoord.fk4

    def ToFK5(self):
        '''
        return the coordinate in the FK5 frame
        '''
        return self.skycoord.fk5
        
    def ToICRS(self):
        '''
        return the coordinate in the ICRS frame
        '''
        return self.skycoord.icrs
    
    def ChangeFrame(self,frame):
        '''
        Change the frame of the object
        Parameters
        ----------
        frame   : Astropy coordinate frame ICRS, Galactic, FK4, FK5 , see astropy for more information
        '''
        self.skycoord = self.skycoord.transform_to(frame)
        self.frame = frame

