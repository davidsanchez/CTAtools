# author David Sanchez david.sanchez@lapp.in2p3.fr
#read Fermi catalog for ApLib and the TeV data.
#Data point are then fitted with a logparabola function
from math import *
from array import *
import string
import numpy,scipy.optimize
from Plot.PlotLibrary import *
from Catalog.ReadFermiCatalog import *
from environ import FERMI_CATALOG_DIR
try :
    from astropy.coordinates import ICRS, Galactic, FK4, FK5 
except :
    print "\033[33m WARNING : you don't have astropy installed. Creation of a catalog with name will not work\033[0m"
    pass

#logparabola func to fit
logparabola = lambda x,norm,alpha,beta, : norm * (x / .1) ** (-alpha - beta * numpy.log(x / .1))

# table for the data
xdata = []
ydata = []
dydata = []

#Read Data : either you use the FGL name or another name (should be recognize by the astropy module
#source = "3FGL J1517.6-2422"
#Cat = FermiCatalogReader(source,FERMI_CATALOG_DIR,"e2dnde","TeV")
source = "AP Librae"
Cat = FermiCatalogReader.fromName(source,FK5,FERMI_CATALOG_DIR,"e2dnde","TeV")

#print some information
print "2FGL association ",Cat.Association('3FGL')
print "3FGL Name ",Cat.Association('2FHL','3FGL_name')
print "3FGL Var Index ",Cat.GetVarIndex("3FGL")

#create a spectrum for a given catalog and compute the model+butterfly
# 3FGL CATALOG
Cat.MakeSpectrum("3FGL",1e-4,0.3)
enerbut,but,enerphi,phi = Cat.Plot("3FGL")

# 2FHL CATALOG
Cat.MakeSpectrum("2FHL",5e-2,2)
enerbut2FHL,but2FHL,enerphi2FHL,phi2FHL = Cat.Plot("2FHL")

# read DATA Point from 3FGL CATALOG
em3FGL,ep3FGL,flux3FGL,dflux3FGL =  Cat.GetDataPoints('3FGL') #energy in TeV since the user ask for that in the call of Cat
ener3FGL = numpy.sqrt(em3FGL*ep3FGL) 
dem3FGL = ener3FGL-em3FGL
dep3FGL = ep3FGL-ener3FGL
c=Cat.ReadPL('3FGL')[3]
e2dnde3FGL = (-c+1)*flux3FGL*numpy.power(ener3FGL*1e6,-c+2)/(numpy.power((ep3FGL*1e6),-c+1)-numpy.power((em3FGL*1e6),-c+1))*1.6e-6
de2dnde3FGL = e2dnde3FGL*dflux3FGL/flux3FGL

for i in xrange(len(ener3FGL)):
    xdata.append(ener3FGL[i])
    ydata.append(e2dnde3FGL[i])
    dydata.append(de2dnde3FGL[i])


# read DATA Point from 2FHL CATALOG
em2FHL,ep2FHL,flux2FHL,dflux2FHL =  Cat.GetDataPoints('2FHL') #energy in TeV since the user ask for that in the call of Cat
for i in xrange(len(em2FHL)):
    if isnan(dflux2FHL[i]):
        em2FHL = numpy.delete(em2FHL,i)
        ep2FHL = numpy.delete(ep2FHL,i)
        flux2FHL = numpy.delete(flux2FHL,i)
        dflux2FHL = numpy.delete(dflux2FHL,i)
        
ener2FHL = numpy.sqrt(em2FHL*ep2FHL) 
dem2FHL = ener2FHL-em2FHL
dep2FHL = ep2FHL-ener2FHL
c2FHL=Cat.ReadPL2('2FHL')[3]
e2dnde2FHL = (-c2FHL+1)*flux2FHL*numpy.power(ener2FHL*1e6,-c2FHL+2)/(numpy.power((ep2FHL*1e6),-c2FHL+1)-numpy.power((em2FHL*1e6),-c2FHL+1))*1.6e-6
de2dnde2FHL = e2dnde2FHL*dflux2FHL/flux2FHL


for i in xrange(len(ener2FHL)):
    xdata.append(ener2FHL[i])
    ydata.append(e2dnde2FHL[i])
    dydata.append(de2dnde2FHL[i])


#Read TEV DATA
TeVData = numpy.genfromtxt("HESS_ApLIB_2015_loose.dat",unpack=True)
#read data from  https://arxiv.org/abs/1410.5897

ener_TeV = TeVData[1]
flux_TeV =   TeVData[2]*ener_TeV**2.16
Dflux_TeV_m = (TeVData[2]-TeVData[3])*ener_TeV**2.16
Dflux_TeV_p = (TeVData[4]-TeVData[2])*ener_TeV**2.16

for i in xrange(len(ener_TeV)):
    xdata.append(ener_TeV[i])
    ydata.append(flux_TeV[i])
    dydata.append((Dflux_TeV_m[i]+Dflux_TeV_p[i])/2.)

################################## FIT
xdata = numpy.array(xdata)
ydata = numpy.array(ydata)
dydata = numpy.array(dydata)
popt, pcov = scipy.optimize.curve_fit(logparabola, xdata, ydata, p0=[1e-12,1.5,0.3], sigma=dydata)

x= numpy.logspace(-6,2,1000)

print "Norm at 0.1 TeV : ",popt[0]," +/- ",numpy.sqrt(pcov[0][0])
print "Alpha : ",popt[1]," +/- ",numpy.sqrt(pcov[1][1])
print "Beta : ",popt[2]," +/- ",numpy.sqrt(pcov[2][2])


########################################"plot
import matplotlib.pyplot as plt
plt.loglog()
plt.plot(enerbut, but, 'b-',label = "3FGL")
plt.plot(enerphi,phi, 'b-')
plt.plot(enerbut2FHL,but2FHL,'r-',label = "2FHL")
plt.plot(enerphi2FHL,phi2FHL,'r-')

plt.errorbar(ener3FGL, e2dnde3FGL, xerr= [dem3FGL,dep3FGL], yerr = de2dnde3FGL,fmt='o')
plt.errorbar(ener2FHL, e2dnde2FHL, xerr= [dem2FHL,dep2FHL], yerr = de2dnde2FHL,fmt='o')
    
plt.errorbar(ener_TeV, flux_TeV, yerr = [Dflux_TeV_m,Dflux_TeV_p],fmt='o',label = "H.E.S.S.")
        
plt.legend(loc=3)

#plot fit function    
plt.plot(x,logparabola(x, popt[0],popt[1],popt[2]), "b-")       

plt.ylabel('E2dN/dE(erg.cm-2.s-1)')
plt.xlabel('energy (TeV)')
plt.show()
