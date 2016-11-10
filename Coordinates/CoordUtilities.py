"""
list of functions for computing various values with coordinates
astropy module is mandatory
author David Sanchez  david.sanchez@lapp.in2p3.fr
"""

# ------ Imports --------------- #
try :
    from astropy import units as u
    from astropy.coordinates import SkyCoord, AltAz, EarthLocation
    from astropy.coordinates import ICRS, Galactic, FK4, FK5 
    from astropy.time import Time
except :
    raise(RuntimeError( "no astropy module found"))
# ------------------------------ #


def GetCoordInDegrees(coords):
    '''
    return the Coordinate in degree stored into an array
    Parameters
    ----------
    coords   : CoordinatesHandler object
    '''
    return [coords.X.degree,coords.Y.degree]

def GetCoordInHMSDMS(coords):
    '''
    return the Coordinate in Hours-minutes-seconds and Degrees-minutes-seconds in a string
    Parameters
    ----------
    coords   : CoordinatesHandler object
    '''
    return coords.to_string('hmsdms')

def AngleSepHMSDMS(c1,c2):
    '''
    return the angulare separation in  Hours-minutes-seconds and Degrees-minutes-seconds between c1 and c2 not matter the frame used
    Parameters
    ----------
    c1   : CoordinatesHandler object
    c2   : CoordinatesHandler object
    '''
    return c1.skycoord.separation(c2.skycoord)

def AngleSepDegree(c1,c2):
    '''
    return the angulare separation in  degrees between c1 and c2 not matter the frame used
    Parameters
    ----------
    c1   : CoordinatesHandler object
    c2   : CoordinatesHandler object
    '''
    res = AngleSepHMSDMS(c1,c2)
    return res.deg

def GetAltAzHESS(coords, date='2016-06-06 00:00:00'):
    '''
    Get AltAz of a source at a given date for the HESS site
    Parameters
    ----------
    coords   : CoordinatesHandler object
    date     : date for which the results is valid. Format is YYYY-MM-DD HH:MM:SS 
    '''
    #Site Location
    print "At HESS Location at ",date
    location = EarthLocation(lat = '-23d16m18s' , lon = '16d30m00s', height = 1800*u.m)
    time = Time(date, format='iso', scale='utc')
    return _GetAltAz(coords,location,time)
    
def GetAltAzLAPALMA(coords, date='2016-06-06 00:00:00'):
    '''
    Get AltAz of a source at a given date for the HELAPALMASS site
    Parameters
    ----------
    coords   : CoordinatesHandler object
    date     : date for which the results is valid. Format is YYYY-MM-DD HH:MM:SS 
    '''
    #Site Location
    print "At CTA North Location at ",date
    location = EarthLocation(lat = '28d45m43s' , lon = '-17d53m24s', height = 1800*u.m)
    time = Time(date, format='iso', scale='utc')
    return _GetAltAz(coords,location,time)
    
def _GetAltAz(coords,location,time):
    '''helper function for the AltAz calculation
    Parameters
    ----------
    coords   : CoordinatesHandler object
    location : location of the observatory (this is an EarthLocation object from astropy). 
    date     : date for which the results is valid. Format is YYYY-MM-DD HH:MM:SS 
    '''
    cAltAz = coords.skycoord.transform_to(AltAz(obstime = time, location = location))
    return cAltAz
    
    
