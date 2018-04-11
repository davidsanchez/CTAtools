# ------ Imports --------------- #
from ebltable.tau_from_model import OptDepth as OD
import os,sys
from os.path import join
import ctools
from ctoolsAnalysis.config import get_config,get_default_config
from ctoolsAnalysis.LikeFit import CTA_ctools_analyser
from Script.Common_Functions import *
import  ctoolsAnalysis.xml_generator as xml
import matplotlib.pyplot as plt
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
    config = get_config(sys.argv[-1])
except :
    print "usage : python "+sys.argv[0]+" config_file"
    exit()

#------ Source Id
data = numpy.genfromtxt("AGN_Monitoring_list.dat",dtype=str,unpack=True)
for i in xrange(len(data[0])):
    srcname = data[0][i]+data[1][i]
    if srcname == config["target"]["name"]:
        redshift = data[-1][i]


srcname = config["target"]["name"]
ra = config["target"]["ra"]
dec = config["target"]["dec"]
        
#------------------ Value of the EBL normalisation and redshift
Alpha = numpy.arange(.1,1.5001,.2)
ETeV = numpy.logspace(-2,2.5,200)
tau = OD.readmodel(model = 'franceschini')
Tau_values = tau.opt_depth(redshift,ETeV)

#----------------- make the first DC1 selection 
from ctoolsAnalysis.cscriptClass import CTA_ctools_script 
Script = CTA_ctools_script.fromConfig(config)
Script.csobsselect(obsXml = "$CTADATA/obs/obs_agn_baseline.xml", log = True,debug = False)

#------------------- Select the files
Analyse = CTA_ctools_analyser.fromConfig(config)
Analyse.ctselect(log = True)

loglike_res = open(srcname+"_AlphaScan_DC1.txt","w")

for ii in xrange(len(Alpha)):
    filename = config["out"]+"/tau_"+str(redshift)+"_"+str(Alpha[ii])+".txt"
    filefun = open(filename,"w")
    for j in xrange(len(ETeV)):
        filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Alpha[ii] * Tau_values)[j]))+"\n")
    #------------------ Make the XML model
    #SOURCE SPECTRUM
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
	    if r>0.1 and r<5.:
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

    open(srcname+'.xml', 'w').write(doc.toprettyxml('  '))

    #------------------- fit the data
    Analyse.create_fit(log = True,debug = False)
    Analyse.fit()
#    Analyse.PrintResults()
    print "LogLike value for Alpha = ",Alpha[ii]," ",Analyse.like.opt().value()
    loglike_res.write(str(Alpha[ii])+" "+str(Analyse.like.opt().value())+"\n")
    
loglike_res.close()
d = numpy.loadtxt(srcname+"_AlphaScan_DC1.txt",unpack=True)
plt.plot(d[0],d[1])
plt.ylabel('Log_like' )
plt.xlabel('Alpha')
plt.show()

