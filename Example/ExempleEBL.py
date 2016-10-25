
# ------ Imports --------------- #
import numpy
from EBL.ReadFinke2010_EBL import *
from EBL.ReadDominguez2011 import *
from EBL.ReadFranceschini2008_EBL import *
from EBL.EBLCorrection import *
# ------------------------------ #

## load each reader and correct for EBL for a putatibe source a z=.117
readerFinke = FinkeReader(0.117)
enerFinke,tauFinke = readerFinke.GetTau()

oneFinke = numpy.ones(len(enerFinke))
correctedFinke,_ = EBLCorrection(readerFinke,enerFinke,oneFinke)

readerDominguez = DominguezReader(0.117)
enerDominguez,tauDominguez = readerDominguez.GetTau()

oneDominguez = numpy.ones(len(enerDominguez))
correctedDominguez,_ = EBLCorrection(readerDominguez,enerDominguez,oneDominguez)

readerFranceschini = FranceschiniReader(0.117)
enerFranceschini,tauFranceschini = readerFranceschini.GetTau()
    
oneFranceschini = numpy.ones(len(enerFranceschini))
correctedFranceschini,_ = EBLCorrection(readerFranceschini,enerFranceschini,oneFranceschini)

#Draw part
import matplotlib.pyplot as plt
plt.ylim(ymax = 1.1, ymin = 1e-4   )
plt.ylim(ymax = 10, ymin = 0.01  )
plt.loglog(enerFinke,correctedFinke,'r', label ="Finke 2010")
plt.legend(bbox_to_anchor=(.2, .98, .40, .102), loc=3,
           ncol=2, borderaxespad=0.)
plt.loglog(enerDominguez,correctedDominguez,'b',label ="Dominguez 2011")
plt.legend(bbox_to_anchor=(.2, .98, .40, .102), loc=3,
           ncol=2, borderaxespad=0.)
plt.loglog(enerFranceschini,correctedFranceschini,'g',label ="Franceschini 2008")
plt.legend(bbox_to_anchor=(.2, .98, .40, .102), loc=3,
           ncol=2, borderaxespad=0.)
plt.ylabel('A.U.')
plt.xlabel('energy (TeV)')
plt.show()
