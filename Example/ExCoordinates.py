#Exemple script for the coordinates module
# author David Sanchez
# david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
try :
    from astropy.coordinates import ICRS, Galactic, FK4, FK5 
except :
    raise(RuntimeError( "no astropy module found"))

import Coordinates.CoordHandler as CH
import Coordinates.CoordUtilities as CU
# ------------------------------ #


if __name__ == '__main__':

    #Create a object from RA DEC of the HBL PKS 2155-304 in the FK5 frame
    coords = CH.CoordinatesHandler(329.716938,-30.225588,FK5)
    #change to different frame
    print coords.ToGalactic()
    print coords.ToFK4()
    print coords.ToFK5()
    print coords.ToICRS()

    print
    #Current frame
    print "frame: ",coords.frame
    print "Coordinate in different format"

    #coordinate in degree    
    print "In degrees:"
    print CU.GetCoordInDegrees(coords)

    #coordinate in Hours Minute Second and Degree Minute Second
    print "In HMS DMS:"
    print CU.GetCoordInHMSDMS(coords)

    coords2 = CH.CoordinatesHandler(328.716938,-30.225588,FK4)
    print "separation between \n",coords.skycoord,"\n and \n",coords2.skycoord
    print "val = ",CU.AngleSepDegree(coords,coords2)

    #look at the altaz at a the  date='2016-06-06 00:00:00' for 2 location
    #HESS and LAPALMA
    print "Observability"
    altaz = CU.GetAltAzHESS(coords,date='2016-06-06 00:00:00')
    print "Object's Altitude = {0.alt:.4}".format(altaz)

    altaz = CU.GetAltAzLAPALMA(coords,date='2016-06-06 00:00:00')
    print "Object's Altitude = {0.alt:.4}".format(altaz)
    
    #Construct an coordinate handler using a galaxie name
    print "looking at M87"
    m87coord = CH.CoordinatesHandler.fromName("M87",FK5)
    print CU.GetCoordInHMSDMS(m87coord)
    altaz = CU.GetAltAzHESS(m87coord,date='2016-06-06 00:00:00')
    print "Object's Altitude = {0.alt:.4}".format(altaz)

