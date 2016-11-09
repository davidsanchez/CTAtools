# author David Sanchez david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
import numpy
from Plot.PlotLibrary import *
from Catalog.ReadFermiCatalog import *
from environ import FERMI_CATALOG_DIR
# ------------------------------ #
#look for this 2FGL source
source = "2FGL J1015.1+4925"
#source = "1FHL J2158.8-3013"
#source = "3FGL J2158.8-3013"
Cat = FermiCatalogReader(source,FERMI_CATALOG_DIR,"e2dnde","TeV")

#print some information
print "2FGL association ",Cat.Association('3FGL')
print "3FGL Name ",Cat.Association('2FHL','3FGL_name')
print "3FGL Var Index ",Cat.GetVarIndex("3FGL")


#create a spectrum for a given catalog and compute the model+butterfly
Cat.MakeSpectrum("3FGL",1e-4,0.3)
enerbut,but,enerphi,phi = Cat.Plot("3FGL")

Cat.MakeSpectrum("2FGL",1e-4,0.3)
enerbut2FGL,but2FGL,enerphi2FGL,phi2FGL = Cat.Plot("2FGL")

Cat.MakeSpectrum("2FHL",5e-2,2)
enerbut2FHL,but2FHL,enerphi2FHL,phi2FHL = Cat.Plot("2FHL")


# read DATA Point 
em,ep,flux,dflux =  Cat.GetDataPoints('3FGL') #energy in TeV since the user ask for that in the call of Cat
ener = numpy.sqrt(em*ep) 
dem = ener-em
dep = ep-ener
c=Cat.ReadPL('3FGL')[3]
dnde = (-c+1)*flux*numpy.power(ener*1e6,-c+2)/(numpy.power((ep*1e6),-c+1)-numpy.power((em*1e6),-c+1))*1.6e-6
ddnde = dnde*dflux/flux

#plot
import matplotlib.pyplot as plt
plt.loglog()
plt.plot(enerbut, but, 'b-',label = "3FGL")
plt.plot(enerphi,phi, 'b-')
plt.plot(enerbut2FGL,but2FGL,'g-',label = "2FGL")
plt.plot(enerphi2FGL,phi2FGL,'g-')
plt.plot(enerbut2FHL,but2FHL,'r-',label = "2FHL")
plt.plot(enerphi2FHL,phi2FHL,'r-')

plt.errorbar(ener, dnde, xerr= [dem,dep], yerr = ddnde,fmt='o')
plt.legend(loc = 3)
plt.ylabel('E2dN/dE(erg.cm-2.s-1)')
plt.xlabel('energy (TeV)')
plt.show()





