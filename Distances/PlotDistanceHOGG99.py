""" Redo Plots of the paper by Hogg 1999"""

import numpy
import matplotlib.pyplot as plt


import cosmolopy.distance as cd
### Define here the Univers
Cosmology = {'omega_M_0':0.2, 'omega_lambda_0':1-0.2, 'omega_k_0':0.0, 'h':0.71}

PlotNumber = 8


N=200



z=numpy.arange(0.001,5,1./N)


val = numpy.zeros(len(z))

for i in xrange(len(z)):
    #Hubble Distance
    dh = cd.hubble_distance_z(z[i],**Cosmology)*cd.e_z(z[i],**Cosmology)
    #In David Hogg's (arXiv:astro-ph/9905116v4) formalism, this is equivalent to D_H / E(z) = c / (H_0 E(z)) [see his eq. 14], which
        #appears in the definitions of many other distance measures.
    
    dm = cd.comoving_distance_transverse(z[i],**Cosmology)
    #See equation 16 of David Hogg's arXiv:astro-ph/9905116v4
    
    da = cd.angular_diameter_distance(z[i],**Cosmology)
    #See equations 18-19 of David Hogg's arXiv:astro-ph/9905116v4
    
    dl = cd.luminosity_distance(z[i],**Cosmology)
    #Units are Mpc
    
    dVc = cd.diff_comoving_volume(z[i], **Cosmology)
    #The differential comoving volume element dV_c/dz/dSolidAngle.
    #Dimensions are volume per unit redshift per unit solid angle.
    #Units are Mpc**3 Steradians^-1.
    #See David Hogg's arXiv:astro-ph/9905116v4, equation 28

    tl = cd.lookback_time(z[i],**Cosmology)
    #See equation 30 of David Hogg's arXiv:astro-ph/9905116v4. Units are s.
    
    agetl = cd.age(z[i],**Cosmology)
    #Age at z is lookback time at z'->Infinity minus lookback time at z.
    
    tH = 3.09e17/Cosmology['h']
    
    ez = cd.e_z(z[i],**Cosmology)
    #The unitless Hubble expansion rate at redshift z.
    #In David Hogg's (arXiv:astro-ph/9905116v4) formalism, this is
    #equivalent to E(z), defined in his eq. 14.
    
    if PlotNumber == 1:
        val[i] = dm/dh
        xtitle = "redshift z"
        ytitle = "Proper motion distance Dm/Dh"

    elif PlotNumber == 2:
        val[i] = da/dh
        xtitle = "redshift z"
        ytitle = "Angular diameter distance Da/Dh"

    elif PlotNumber == 3:
        val[i] = dl/dh
        xtitle = "redshift z"
        ytitle = "Luminosity distance Dl/Dh"
        
    elif PlotNumber == 4:
        val[i] = 5*numpy.log10(dl*1e6/10)+5*numpy.log10(Cosmology['h'])
        xtitle = "redshift z"
        ytitle = "Distance Modulus - 5 log (h)"

    elif PlotNumber == 5:
        val[i] =  cd.diff_comoving_volume(z[i], **Cosmology)/(dh)**3
        xtitle = "redshift z"
        ytitle = "Comoving volume element"

    elif PlotNumber == 6:
        val[i] =  dVc/(dh)**3
        xtitle = "redshift z"
        ytitle = "Comoving volume element"

    elif PlotNumber == 7:
        val[i] =  tl/tH
        xtitle = "redshift z"
        ytitle = "Lookback time"
        
    elif PlotNumber == 8:
        val[i] =  (1+z[i])**2/ez
        xtitle = "redshift z"
        ytitle = "Dimensionless intersection probability"
        
    else :
        exit()
plt.plot(z,val,linewidth=2, color='r')
plt.xlabel(xtitle)
plt.ylabel(ytitle)
plt.show()
