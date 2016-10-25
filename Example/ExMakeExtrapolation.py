# author David Sanchez david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
from math import *
from array import *
import string
import numpy
from Plot.PlotLibrary import *
from EBL.ReadDominguez2011 import *
from EBL.EBLCorrection import *
from Catalog.ReadFermiCatalog import *
# ------------------------------ #

Emax = 10 #let's extrapolate up to 10 TeV

#Make extrapolation from user numbers
# use spectral parameters of Ap Librae (see https://arxiv.org/abs/1410.5897)

Flux   = 2.717986274e-12
DFlux  = 0.09558767091e-12
Index  = 2.105534772
DIndex = 0.03118624899
Ec     = 1454e-6
z=0.049

data = [Flux,DFlux,Index,DIndex,Ec]
Spec = PlotLibrary.Spectrum(data,Model="PowerLaw",Emin=1e-4,Emax=Emax,escale = "TeV")

#compute the model and the butterfly
enerphi,phi = Spec.GetModel()
enerbut,but = Spec.GetButterfly()

#For comparison, show the butterfly in the Fermi energy range
SpecNotExtrapolated = PlotLibrary.Spectrum(data,Model="PowerLaw",Emin=1e-4,Emax=0.064,escale = "TeV")
#compute the model and the butterfly
enerphi_NotExtrapolated,phi_NotExtrapolated = SpecNotExtrapolated.GetModel()
enerbut_NotExtrapolated,but_NotExtrapolated = SpecNotExtrapolated.GetButterfly()

#Correct for EBL using Dominguez model
readerDominguez = DominguezReader(z)
enerDominguez,tauDominguez = readerDominguez.GetTau()
EBL_corrected_phi,_ = EBLCorrection(readerDominguez,enerphi,phi)
EBL_corrected_but,_ = EBLCorrection(readerDominguez,enerbut,but)


#draw
import matplotlib.pyplot as plt
plt.plot(enerbut, but, 'b--')
plt.plot(enerphi,phi, 'b--',label = "Fermi measurement extrapolated")
plt.legend(bbox_to_anchor=(.2, .98, .40, .102), loc=1,
           ncol=1, borderaxespad=0.)
plt.yscale('log')
plt.xscale('log')

plt.ylabel('E2dN/dE(erg.cm-2.s-1)')
plt.xlabel('energy (TeV)')

plt.plot(enerbut_NotExtrapolated , but_NotExtrapolated , 'b-')
plt.plot(enerphi_NotExtrapolated ,phi_NotExtrapolated , 'b-',label ="Fermi energy range")
plt.legend(bbox_to_anchor=(.2, .98, .40, .102), loc=1,
           ncol=1, borderaxespad=0.)
       
plt.plot(enerbut , EBL_corrected_but , 'r--')
plt.plot(enerphi ,EBL_corrected_phi , 'r--',label ="Corrected for EBL")
plt.legend(bbox_to_anchor=(.2, .98, .40, .102), loc=1,
           ncol=1, borderaxespad=0.)
           

plt.show()
