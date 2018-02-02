# ------ Imports --------------- #
from ebltable.tau_from_model import OptDepth as OD
import os,sys,numpy
from os.path import join
import ctools
from ctoolsAnalysis.config import get_config,get_default_config
from ctoolsAnalysis.LikeFit import CTA_ctools_analyser
from Script.Common_Functions import *
from Script.Utils import LiMa
import  ctoolsAnalysis.xml_generator as xml
# ------------------------------ #
try:
    get_ipython().magic(u'pylab')
except :
    pass

#Model = "PL"
#Model = "LPEBL"
Model = "PLEBL"
#Model = "PLECEBL"

try:  #conf file provided
    config = get_config(sys.argv[-2])
    redshift = float(sys.argv[-1])
except :
    print "usage : python "+sys.argv[0]+" config_file redshift"
    exit()

#------------------ Value of the EBL  and redshift
ETeV = numpy.logspace(-2,2.5,200)
tau = OD.readmodel(model = 'franceschini')
Tau_values = tau.opt_depth(redshift,ETeV)

#------------------ Make the XML model
lib,doc = xml.CreateLib()
srcname = config["target"]["name"]
#SOURCE SPECTRUM
if Model == "PL":
	spec = xml.addPowerLaw1(lib,srcname,"PointSource",flux_value=1e-14,flux_max=1000.0, flux_min=1e-5)

elif Model == "PLEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	spec = xml.PowerLawEBL(lib,srcname,filename)
	#### EBL : end
elif Model == "LPEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	spec = xml.LogParabolaEBL(lib,srcname,filename)
	#### EBL : end
elif Model == "PLECEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	Ecut = 3./(1+redshift)*1e6
	spec = xml.PowerLawExpCutoffEBL(lib,srcname,filename,ecut_value=Ecut,ecut_free=0)
	#### EBL : end


ra = config["target"]["ra"]
dec = config["target"]["dec"]
spatial = xml.AddPointLike(doc,ra,dec)
spec.appendChild(spatial)
lib.appendChild(spec)

#CTA BACKGROUND
bkg = xml.addCTAIrfBackground(lib)
lib.appendChild(bkg)

# save the model into an xml file
open(config["file"]["inmodel"], 'w').write(doc.toprettyxml('  '))

#----------------- make the first DC1 selection 
from ctoolsAnalysis.cscriptClass import CTA_ctools_script 
Script = CTA_ctools_script.fromConfig(config)
Script.csobsselect(obsXml = "$CTADATA/obs/obs_agn_baseline.xml", log = True,debug = False)

#------------------- Select the files
Analyse = CTA_ctools_analyser.fromConfig(config)
Analyse.ctselect(log = False)

#------------------- make an on off analysis
Script.csphagen(log = True)
prefix = Script.config["target"]["name"]+"_onoff"
Onfile = config['out']+"/"+prefix+"_stacked_pha_on.fits"
Offfile = config['out']+"/"+prefix+"_stacked_pha_off.fits"
Ondata = pyfits.open(Onfile)[1].data
Oncount = Ondata['COUNTS']
Alpha = Ondata['BACKSCAL']
Ebound = pyfits.open(Onfile)[2].data
Offdata = pyfits.open(Offfile)[1].data
Offcount = Offdata['COUNTS']

print "Excess   significance  Excess/bkg"
for i in xrange(len(Oncount)):
	excess = Oncount[i]-Offcount[i]*Alpha[i]
	sigma = LiMa(Oncount[i],Offcount[i],Alpha[i])
	print excess," ",sigma," ",(excess)/Offcount[i]
	if excess/Offcount[i]<0.05 or sigma<2:
		Emax = Ebound[i+2]['E_MAX']
print "Found maximal energy for the analysis to be ",Emax
Analyse.config["energy"]["emax"] = Emax
Script.config["energy"]["emax"] = Emax
Analyse.ctselect(log = True)

#------------------- Make the skymap
Analyse.ctskymap(log = True,debug = False) # --> It does not work (see comments).

#------------------- fit the data
Analyse.create_fit(log = True,debug = False)
Analyse.fit()
Analyse.PrintResults()
# print "LogLike value for ",sys.argv[-1]," ", Analyse.like.obs().logL()

#------------------- make spectral point
#5 point per decade
npoint = int((numpy.log10(config["energy"]["emax"])-numpy.log10(config["energy"]["emin"]))/5.)
Script.csspec(npoint = npoint,log = True,debug = False)

#------------------- plot the points
import show_spectrum
show_spectrum.plot_spectrum(Script.csspec["outfile"].value(),Script.csspec["outfile"].value().replace("fits","png"))

#------------------- make butterfly plot
Analyse.ctbutterfly(log = True,debug = False)

import show_butterfly
show_butterfly.plot_butterfly(Analyse.ctbutterfly["outfile"].value(),Analyse.ctbutterfly["outfile"].value().replace("dat","png"))

#------------------- make residual maps
Script.csresmap(log = True,debug = False)


