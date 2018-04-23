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
import pyfits
# ------------------------------ #
try:
    get_ipython().magic(u'pylab')
except :
    pass

catalog = os.getcwd()+"/AGN_Monitoring_list.dat"
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

#----------------- make the first DC1 selection 
from ctoolsAnalysis.cscriptClass import CTA_ctools_script 
Script = CTA_ctools_script.fromConfig(config)
Script.csobsselect(obsXml = "$CTADATA/obs/obs_agn_baseline.xml", log = True,debug = False)

#------------------- Select the files
Analyse = CTA_ctools_analyser.fromConfig(config)
Analyse.ctselect(log = False)

#------------------- make an on off analysis
num_bin = int(round((numpy.log10(config["energy"]["emax"])-numpy.log10(config["energy"]["emin"]))/0.2,0))
if num_bin == 0:
    num_bin = 1
Script.csphagen(log = True)

#read the files and compute the new Emax
prefix = Script.config["target"]["name"]+"_onoff"
Onfile = config['out']+"/"+prefix+"_stacked_pha_on.fits"
Offfile = config['out']+"/"+prefix+"_stacked_pha_off.fits"
Ondata = pyfits.open(Onfile)[1].data
Oncount = Ondata['COUNTS']
Alpha = Ondata['BACKSCAL']
Ebound = pyfits.open(Onfile)[2].data
Offdata = pyfits.open(Offfile)[1].data
Offcount = Offdata['COUNTS']

Emax = Analyse.config["energy"]["emax"]

print "Excess   significance  Excess/bkg Emin Emax"
srcname = config["target"]["name"]
filename_excess = "BinExcess_"+srcname+".txt"
filefun = open(filename_excess,"w")
filefun.write("Excess    Sigma    Excess/Off    E_min[TeV]    E_max[TeV]    \n")

for i in xrange(len(Oncount)-2):
	excess = Oncount[i]-Offcount[i]*Alpha[i]
	sigma = LiMa(Oncount[i],Offcount[i],Alpha[i])
	print excess," ",sigma," ",(excess)/Offcount[i]," ",Ebound[i]['E_MIN']," ",Ebound[i]['E_MAX']
	filefun.write(str(excess)+" "+str(sigma)+" "+str((excess)/(Offcount[i]*Alpha[i])) +" "+str(Ebound[i]['E_MIN']*1e-9)+" "+str(Ebound[i]['E_MAX']*1e-9)+"\n")
	if excess/Offcount[i]<0.05 or sigma<2 or excess<10:
		Emax = Ebound[i+2]['E_MAX']*1e-9 #in MeV
		break

print "Found maximal energy for the analysis to be ",Emax
filefun.write("Found maximal energy for the analysis to be "+str(Emax))
Analyse.config["energy"]["emax"] = Emax
Script.config["energy"]["emax"] = Emax

#------------------ Value of the EBL  and redshift
ETeV = numpy.logspace(-2,2.5,200)
tau = OD.readmodel(model = 'franceschini')
Tau_values = tau.opt_depth(redshift,ETeV)


#------------------ Make the XML model
lib,doc = xml.CreateLib()
srcname = config["target"]["name"]
#SOURCE SPECTRUM
if Model == "PL":
	spec = xml.addPowerLaw1(lib,srcname,"PointSource",
			eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]),
			flux_value=1e-14,flux_max=1000.0, flux_min=1e-5)

elif Model == "PLEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	spec = xml.PowerLawEBL(lib,srcname,filename,eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]))
	#### EBL : end
elif Model == "LPEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	spec = xml.LogParabolaEBL(lib,srcname,filename,eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]))
	#### EBL : end
elif Model == "PLECEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	Ecut = 3./(1+redshift)*1e6
	spec = xml.PowerLawExpCutoffEBL(lib,srcname,filename,eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]),
			ecut_value=Ecut,ecut_free=0)
	#### EBL : end


ra = config["target"]["ra"]
dec = config["target"]["dec"]
spatial = xml.AddPointLike(doc,ra,dec)
spec.appendChild(spatial)
lib.appendChild(spec)

#------------------ look for close sources
data = numpy.genfromtxt(catalog,dtype=str,unpack=True)
for i in xrange(len(data[0])):
	srcname_cat = data[0][i]+data[1][i]
	ra_cat = float(data[2][i])
	dec_cat = float(data[3][i])
	z = float(data[4][i])
	Tau_values = tau.opt_depth(z,ETeV)
	r = numpy.sqrt((ra_cat-ra)**2+(dec_cat-dec)**2)
	if r>0.1 and r<3.:
		print "Add source in the FoV : ",srcname_cat," ",ra_cat," ",dec_cat
		if data[0][i] == "1FHL":
			print "Add simple PowerLaw + EBL"
			filename = config["out"]+"/tau_addedd_"+srcname_cat+".txt"
			filefun = open(filename,"w")
			for j in xrange(len(ETeV)):
				filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
				#------------------ Make the XML model
				spec = xml.PowerLawEBL(lib,srcname_cat,filename,eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]))
		else:
			print "Add simple PowerLaw"
			spec = xml.addPowerLaw1(lib,srcname_cat,"PointSource",
				eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]),
				flux_value=1e-14,flux_max=1000.0, flux_min=1e-5)
		spatial = xml.AddPointLike(doc,ra_cat,dec_cat)
		spec.appendChild(spatial)
		lib.appendChild(spec)

#CTA BACKGROUND
bkg = xml.addCTAIrfBackground(lib)
lib.appendChild(bkg)

# save the model into an xml file
open(config["file"]["inmodel"], 'w').write(doc.toprettyxml('  '))

#------------------- Select the files
Analyse.ctselect(log = True)

#------------------- Make the skymap
Analyse.ctskymap(log = True,debug = False) # --> It does not work (see comments).

#------------------- fit the data
Analyse.create_fit(log = True,debug = False)
Analyse.fit()
Analyse.PrintResults()
# print "LogLike value for ",sys.argv[-1]," ", Analyse.like.obs().logL()

#------------------- make butterfly plot
Analyse.ctbutterfly(log = True,debug = False)

import show_butterfly
show_butterfly.plot_butterfly(Analyse.ctbutterfly["outfile"].value(),Analyse.ctbutterfly["outfile"].value().replace("dat","png"))

#------------------- make residual maps
Script.csresmap(log = True,debug = False)

#------------------- make spectral point
#5 point per decade
#npoint = int((numpy.log10(config["energy"]["emax"])-numpy.log10(config["energy"]["emin"]))/5.)
#Script.csspec(npoint = npoint,log = True,debug = False)
npoint = int(round((numpy.log10(config["energy"]["emax"])-numpy.log10(config["energy"]["emin"]))/0.2,0))
if npoint == 0:
    npoint = 1
Script.csspec(npoint,log = True,debug = False)

#------------------- plot the points
import show_spectrum
show_spectrum.plot_spectrum(Script.csspec["outfile"].value(),Script.csspec["outfile"].value().replace("fits","png"))


