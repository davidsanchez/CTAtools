.. _Coordinate:

Coordinate Handler
=============

This part of the module makes used of the astropy library. The  CoordinatesHandler is use to make 
coordinate transformation from different reference systems. The class contains a SkyCoord object 
from the astropy library.

.. code-block:: python

    from astropy.coordinates import ICRS, Galactic, FK4, FK5 
    import Coordinates.CoordHandler as CH
    import Coordinates.CoordUtilities as CU

    #Create a object from RA DEC of the HBL PKS 2155-304 in the FK5 frame
    coords = CH.CoordinatesHandler(329.716938,-30.225588,FK5)
    
This code creates a CoordinatesHandler object with the coordinates of the HBL PKS 2155-304 in the 
FK5 reference system. Functions ToGalactic, ToFK4, ToFK5 and ToICRS return another SkyCoord object.
The functions ChangeFrame will change the reference system of the object.

Another possibilty to create a CoordHandler object is to pass a source name. This use again the 
astropy module to resolve the name.

.. code-block:: python

    m87 = CH.CoordinatesHandler.fromName("M87",FK5)
    

Helper functions are defined in the module Coordinates.CoordUtilities to give the coordinates in 
degrees or Hours-minutes-seconds and Degrees-minutes-seconds and compute the angular separation 
between 2 CoordHandler objects.

Functions GetAltAz* gives the Altitude and Azimute of source at a given date. Currently HESS and 
Lapalma sites are supported. The returned object is an astropy SkyCoord.


.. code-block:: python

    altaz = CU.GetAltAzLAPALMA(m87,date='2016-06-06 00:00:00')
    print "Object's Altitude = {0.alt:.4}".format(altaz)
