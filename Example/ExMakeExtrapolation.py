# author David Sanchez david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
from math import *
from array import *
import string
import numpy
from Plot.PlotLibrary import *
from ebltable.tau_from_model import OptDepth as OD
from Catalog.ReadFermiCatalog import *
# ------------------------------ #

Emax = 10 #let's extrapolate up to 10 TeV

#Make extrapolation from user numbers
# use spectral parameters of Ap Librae (see https://arxiv.org/abs/1410.5897)

Flux   = 2.717986274e-6 #ph/cm2/s/TeV
DFlux  = 0.09558767091e-6
Index  = 2.11
DIndex = 0.03
Ec     = 1454e-6 #TeV
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
tau = OD.readmodel(model = 'dominguez')
Tau_dominguez = tau.opt_depth(z,enerphi)
EBL_corrected_phi = phi*numpy.exp(-1. * Tau_dominguez)

Tau_dominguez = tau.opt_depth(z,enerbut)
EBL_corrected_but = but*numpy.exp(-1. * Tau_dominguez)


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
plt.plot(enerbut , EBL_corrected_but , 'r--')
plt.plot(enerphi ,EBL_corrected_phi , 'r--',label ="Corrected for EBL")
plt.legend(loc = 3)
plt.show()
