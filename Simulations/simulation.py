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
import random
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

# #------------------- 
Analyse = CTA_ctools_analyser.fromConfig(config)


#------------------ Value of the EBL
ETeV = numpy.logspace(-2,2.5,200)
EBL_mod = config["simulation"]["EBL_model"]
tau = OD.readmodel(model = EBL_mod)
Tau_values = tau.opt_depth(redshift,ETeV)

#------------------ Make the XML model for simulations
lib,doc = xml.CreateLib()
srcname = config["target"]["name"]
Model = config["simulation"]["spectrum_model"]
#SOURCE SPECTRUM
if Model == "PL":
	#spec = xml.addPowerLaw1(lib,srcname,"PointSource", eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]),flux_value=1e-10,flux_max=1000.0, flux_min=1e-5)
        spec = xml.addPowerLaw1(lib,srcname,filename,eflux=2000,flux_value=1.465e-10,flux_max=1.665e-10, flux_min=1.275e-10,index_value=-2.184, index_min=-2.3334, index_max=-2.0346)

elif Model == "PLEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	#spec = xml.PowerLawEBL(lib,srcname,filename,eflux=1e6*numpy.sqrt(Analyse.config["energy"]["emax"]*Analyse.config["energy"]["emin"]))

	#spec = xml.PowerLawEBL(lib,srcname,filename,eflux=Analyse.config["simulation"]["pivot_sim"],flux_value=Analyse.config["simulation"]["prefactor_sim"],flux_max=Analyse.config["simulation"]["prefactor_max_sim"], flux_min=Analyse.config["simulation"]["prefactor_min_sim"],flux_scale=Analyse.config["simulation"]["prefactor_scale_sim"],index_value=Analyse.config["simulation"]["index_value_sim"], index_min=Analyse.config["simulation"]["index_min_sim"], index_max=Analyse.config["simulation"]["index_max_sim"])

        spec = xml.PowerLawEBL(lib,srcname,filename,eflux=2000,flux_value=1.465e-10,flux_max=1.665e-10, flux_min=1.275e-10,flux_scale=1, index_value=-2.184, index_min=-2.3334, index_max=-2.0346, )

	#### EBL : end
elif Model == "LPEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
        spec = xml.LogParabolaEBL(lib,srcname,filename,eflux=2000,flux_value=1.465e-10,flux_max=1.665e-10, flux_min=1.275e-10,index_value=-2.184, index_min=-2.3334, index_max=-2.0346)
 
	#### EBL : end
elif Model == "PLECEBL":
	#### EBL
	filename = config["out"]+"/tau_"+srcname+".txt"
	filefun = open(filename,"w")
	for j in xrange(len(ETeV)):
	    filefun.write(str(ETeV[j]*1e6)+" "+str(max(1e-10,numpy.exp(-Tau_values)[j]))+"\n")
	#------------------ Make the XML model
	Ecut = 3./(1+redshift)*1e6
        spec = xml.PowerLawExpCutoffEBL(lib,srcname,filename,eflux=2000,flux_value=1.465e-10,flux_max=1.665e-10, flux_min=1.275e-10,index_value=-2.184, index_min=-2.3334, index_max=-2.0346)
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


#---------------------------- Simulations

n_hours = 2 #hours for simulations
n_simulations = 3

# produce different seeds for simulations
seed_index = 0
while seed_index != 1:
    seeds = random.sample(range(1, 1000000), n_simulations)
    sor_seed = numpy.sort(seeds)
    equal_el = 0
    for j in xrange(len(sor_seed)-1):
        if sor_seed[j] != sor_seed[j+1]:
            equal_el = equal_el+1
	if equal_el == len(sor_seed)-1:  
            seed_index = 1

start_time_MET = 662774400
end_time_MET = 662774400 + 3600*n_hours

for i in range(1, n_simulations+1):
    from ctools import ctobssim
    sm = ctools.ctobssim()
    sm["inmodel"]=config["file"]["inmodel"]
    sm["outevents"]= "/home/biasuzzi/Desktop/DC1_Analysis/test_ctobssim/PKS0507+17/"+srcname+"_sim"+"_"+str(i)+".fits"
    sm["caldb"]= config["irfs"]["caldb"]
    sm["irf"]= config["irfs"]["irf"]
    #sm["edisp"]=yes
    sm["seed"]=seeds[i-1]
    sm["ra"]= config["target"]["ra"]+0.4   # +0.4 deg to create an offset with respect to the source position.
    sm["dec"]= config["target"]["dec"]+0.4 # +0.4 deg to create an offset with respect to the source position.
    sm["rad"]= 3
    sm["tmin"]= start_time_MET
    sm["tmax"]= end_time_MET
    #sm["emin"]= config["simulation"]["emin_sim"]
    #sm["emax"]= config["simulation"]["emax_sim"]
    sm["emin"]= 0.03
    sm["emax"]= 8
    sm["logfile"]="/home/biasuzzi/Desktop/DC1_Analysis/test_ctobssim/PKS0507+17/ctobssim_"+str(i)+"log.txt"
    sm.execute()

# create a list 
bashCommand = "rm /home/biasuzzi/Desktop/DC1_Analysis/test_ctobssim/PKS0507+17/test.dat"
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)




