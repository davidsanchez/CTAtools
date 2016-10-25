# author David Sanchez david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
from Plot import PlotLibrary
# ------------------------------ #

## Spectral information of PKS 2155-304 by HESS phase II mono reported here : 
Norm = 1480.18  *1e-12*1e-3
DNorm =    70.4701*1e-12*1e-3
Index = 2.9485
DIndex =  0.22477 
Beta = 1.04002
DBeta =  0.312364   
Ec = 0.1412*1e3
Eminh2 = 0.11*1e3
Emaxh2 =4.715*1e3
cov1 =-0.0001163*1e-4*1e-3
cov2 = 0.2765*1e-4*1e-3
cov3 =-0.00322

#gh.SetXTitle("E [GeV]")
#gh.SetYTitle("E^{2}dN/dE [ erg cm^{-2} s^{-1} ] ")
Spec = PlotLibrary.Spectrum([Norm,DNorm,Index,DIndex,Beta,DBeta,Ec,cov1,cov2,cov3],Model='LogParabola',Emin=Eminh2,Emax=Emaxh2,escale = "GeV")

enerphi,phi = Spec.GetModel()
enerbut,but = Spec.GetButterfly()


import matplotlib.pyplot as plt
plt.loglog()
plt.plot(enerbut, but, 'b-', enerphi,phi, 'b-')
plt.ylabel('E2dN/dE(erg.cm-2.s-1)')
plt.xlabel('energy (TeV)')
plt.show()
