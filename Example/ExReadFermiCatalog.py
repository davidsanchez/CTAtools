# author David Sanchez david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
import numpy
from Plot.PlotLibrary import *
from Catalog.ReadFermiCatalog import *
from environ import FERMI_CATALOG_DIR
# ------------------------------ #
#look for this 2FGL source
#source = "2FGL J1015.1+4925"
#source = "1FHL J2158.8-3013"
source = "3FGL J2158.8-3013"
Cat = FermiCatalogReader(source,FERMI_CATALOG_DIR,"e2dnde","TeV")

#print some information
print "2FGL association ",Cat.Association('3FGL')
print "3FGL Name ",Cat.Association('2FHL','3FGL_name')
print "3FGL Var Index ",Cat.GetVarIndex("3FGL")


#create a spectrum for a given catalog and compute the model+butterfly
Cat.MakeSpectrum("3FGL",1e-4,0.3)
enerbut,but,enerphi,phi = Cat.Plot("3FGL")

Cat.MakeSpectrum("3FHL",1e-2,2)
enerbut3FHL,but3FHL,enerphi3FHL,phi3FHL = Cat.Plot("3FHL")

Cat.MakeSpectrum("2FHL",5e-2,0.5)
enerbut2FHL,but2FHL,enerphi2FHL,phi2FHL = Cat.Plot("2FHL")


# read DATA Point 3FGL
em,ep,flux,dflux =  Cat.GetDataPoints('3FGL') #energy in TeV since the user ask for that in the call of Cat
ener = numpy.sqrt(em*ep) 
dem = ener-em
dep = ep-ener
c=Cat.ReadPL('3FGL')[2]
dnde = (-c+1)*flux*numpy.power(ener*1e6,-c+2)/(numpy.power((ep*1e6),-c+1)-numpy.power((em*1e6),-c+1))*1.6e-6
ddnde = dnde*dflux/flux

# read DATA Point 3FHL
em3FHL,ep3FHL,flux3FHL,dflux3FHL =  Cat.GetDataPoints('3FHL') #energy in TeV since the user ask for that in the call of Cat
ener3FHL = numpy.sqrt(em3FHL*ep3FHL) 
dem3FHL = ener3FHL-em3FHL
dep3FHL = ep3FHL-ener3FHL
c3FHL=Cat.ReadPL('3FHL')[2]
dnde3FHL = (-c3FHL+1)*flux3FHL*numpy.power(ener3FHL*1e6,-c3FHL+2)/(numpy.power((ep3FHL*1e6),-c3FHL+1)-numpy.power((em3FHL*1e6),-c3FHL+1))*1.6e-6
ddnde3FHL = dnde3FHL*dflux3FHL/flux3FHL

#plot
import matplotlib.pyplot as plt
plt.loglog()
plt.plot(enerbut, but, 'b-',label = "3FGL")
plt.plot(enerphi,phi, 'b-')
plt.plot(enerbut3FHL,but3FHL,'g-',label = "3FHL")
plt.plot(enerphi3FHL,phi3FHL,'g-')
plt.plot(enerbut2FHL,but2FHL,'r-',label = "2FHL")
plt.plot(enerphi2FHL,phi2FHL,'r-')

plt.errorbar(ener, dnde, xerr= [dem,dep], yerr = ddnde,fmt='o')
plt.errorbar(ener3FHL, dnde3FHL, xerr= [dem3FHL,dep3FHL], yerr = ddnde3FHL,fmt='go')
plt.legend(loc = 3)
plt.ylabel('E2dN/dE(erg.cm-2.s-1)')
plt.xlabel('energy (TeV)')
plt.show()





