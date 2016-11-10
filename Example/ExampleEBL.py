#exemple script to use the ebltable from M. Meyer
# have a loot at the repo https://github.com/me-manu/ebltable
# ------ Imports --------------- #
from ebltable.tau_from_model import OptDepth as OD
import numpy 
import matplotlib.pyplot as plt
# ------------------------------ #

# ------------------------------ #

# Source redshift
z = 0.117
# array with energies in TeV
ETeV = numpy.logspace(-1,1,50)

#compute the optical depth 
#Supported EBL models:
#	Name:		Publication:
#	franceschini	Franceschini et al. (2008)	http://www.astro.unipd.it/background/
#	kneiske		Kneiske & Dole (2010)
#	dominguez	Dominguez et al. (2011)
#	inoue		Inuoe et al. (2013)		http://www.slac.stanford.edu/~yinoue/Download.html
#	gilmore		Gilmore et al. (2012)		(fiducial model)
tau = OD(model = 'franceschini')
Tau_franceschini = tau.opt_depth_array(z,ETeV)

tau = OD(model = 'kneiske')
Tau_kneiske = tau.opt_depth_array(z,ETeV)

tau = OD(model = 'dominguez')
Tau_dominguez = tau.opt_depth_array(z,ETeV)

#tau = OD(model = 'inoue')
#Tau_inuoe = tau.opt_depth_array(z,ETeV)

tau = OD(model = 'gilmore')
Tau_gilmore = tau.opt_depth_array(z,ETeV)

#Draw part
import matplotlib.pyplot as plt
plt.ylim(ymax = 1.1, ymin = 1e-4   )
plt.ylim(ymax = 10, ymin = 0.01  )
plt.loglog(ETeV,numpy.exp(-1. * Tau_franceschini[0]), lw = 2., ls = '-', label ="Franceschini et al. (2008)")
plt.loglog(ETeV,numpy.exp(-1. * Tau_kneiske[0]), lw = 2., ls = '-', label ="Kneiske & Dole (2010)")
plt.loglog(ETeV,numpy.exp(-1. * Tau_dominguez[0]), lw = 2., ls = '-', label ="Dominguez et al. (2011)")
#plt.loglog(ETeV,numpy.exp(-1. * Tau_inuoe[0]), lw = 2., ls = '-', label ="Inuoe et al. (2013")
plt.loglog(ETeV,numpy.exp(-1. * Tau_gilmore[0]), lw = 2., ls = '-', label ="Gilmore et al. (2012)")
plt.legend(loc = 3)
plt.ylabel('A.U.')
plt.xlabel('energy (TeV)')
plt.show()
