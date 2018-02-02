# ------ Imports --------------- #
import os,sys,numpy
import matplotlib.pyplot as plt
import pyfits
from Script.Utils import LiMa
from ctoolsAnalysis.config import get_config,get_default_config
# ------------------------------ #
try:
    get_ipython().magic(u'pylab')
except :
    pass

try:  #conf file provided
    config = get_config(sys.argv[-1])
except :
    print "usage : python "+sys.argv[0]+" config_file"
    exit()
prefix = config["target"]["name"]+"_onoff"
Onfile = config['out']+"/"+prefix+"_stacked_pha_on.fits"
Offfile = config['out']+"/"+prefix+"_stacked_pha_off.fits"

Ondata = pyfits.open(Onfile)[1].data
Oncount = Ondata['COUNTS']
dOncount = Ondata['STAT_ERR']
Alpha = Ondata['BACKSCAL']

Offdata = pyfits.open(Offfile)[1].data
Offcount = Offdata['COUNTS']
dOffcount = Offdata['STAT_ERR']

Ebound = pyfits.open(Onfile)[2].data

plt.figure()
plt.errorbar((Ebound['E_MAX']+Ebound['E_MIN'])/2.,Oncount,xerr=(Ebound['E_MAX']-Ebound['E_MIN'])/2.,yerr=dOncount,ls='--',lw=2,color='b')
plt.errorbar((Ebound['E_MAX']+Ebound['E_MIN'])/2.,Offcount*Alpha,xerr=(Ebound['E_MAX']-Ebound['E_MIN'])/2.,yerr=numpy.sqrt(dOncount**2+dOffcount**2*Alpha),ls='--',lw=2,color='r')
plt.xlabel('E (ev)')
plt.ylabel('# Counts')
plt.semilogx()


plt.figure()
plt.errorbar((Ebound['E_MAX']+Ebound['E_MIN'])/2.,Oncount-Offcount*Alpha,xerr=(Ebound['E_MAX']-Ebound['E_MIN'])/2.,ls='--',lw=2,color='r')
plt.xlabel('E (ev)')
plt.ylabel('Excess')
plt.semilogx()

print "Excess   significance  Excess/bkg"
for i in xrange(len(Oncount)):
	print Oncount[i]-Offcount[i]*Alpha[i]," ",LiMa(Oncount[i],Offcount[i],Alpha[i])," ",(Oncount[i]-Offcount[i]*Alpha[i])/Offcount[i]


