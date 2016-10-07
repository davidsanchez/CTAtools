import numpy
from EBL.ReadFinke2010_EBL import *


def EBLCorrection(reader,ener,flux,dflux=None,alpha=1.,unit = "TeV"):
    '''small function called with a EBL reader a flux value and possibly and error on the flux
    z : redshift of the source
    flux and ener are the tabulated flux (SED) of the source and the correspondind enegrgy 
    alpha = 1 means absorption
    alpha = -1 means deabsorption
    unit can be MeV, GeV or TeV'''

    if unit == "MeV":
        ener*=1e-6
    elif unit == "GeV":
        ener*=1e-3

    E,tau = reader.GetTau()
    N=len(flux)
    AbsFlux = numpy.zeros(N)
    AbsdFlux = numpy.zeros(N)
    depth = numpy.interp(ener,E,tau,0,0)
    AbsFlux = flux*numpy.exp(-alpha*depth)
    if not(dflux==None):
      AbsdFlux=dflux*numpy.exp(-alpha*depth)
    return AbsFlux,AbsdFlux


if __name__ == '__main__':
    reader = FinkeReader(0.117)
    ener,tau = reader.GetTau()
    
    one = numpy.ones(len(ener))
    corrected,_ = EBLCorrection(reader,ener,one)
    
    import matplotlib.pyplot as plt
    plt.loglog(ener,corrected)
    plt.show()
