import os, sys
from submit import call
import environ
print sys.executable
from os.path import join
import pyfits
import math
from ctoolsAnalysis.LikeFit import CTA_ctools_analyser
import ctools
import Script.Common_Functions as CF
import numpy as np
# from environ import INST_DIR
from Plot.PlotLibrary import *
from Catalog.ReadFermiCatalog import *
from Plot.PlotLibrary import *
from ebltable.tau_from_model import OptDepth as OD
import ctoolsAnalysis.xml_generator as xml
import Script.SimulSelectedFrom3FHL as SimulScript



#PL func to fit
powerlaw = lambda x,norm,gamma, : norm * (x) ** (-gamma)
#LP func to fit
logparabola = lambda x,norm,gamma,beta, : norm * (x) ** (-gamma-beta*np.log(x))

def create_xml_from_fileFunctions(sourcename,ra,dec,outfile):
    '''
    Create xml file for given alpha and index
    Parameters
    ---------
    sourcename: studied source
    ra,dec: coordinates of the source
    alpha: EBL normalisation
    index: index of the power law
    '''
    lib,doc = xml.CreateLib()
    spec = xml.addFileFunction(lib, sourcename, type = "PointSource",filefun=outfile,flux_free=1, flux_value=1., flux_scale=1.,flux_max=100000000.0, flux_min=0.0)
    spatial = xml.AddPointLike(doc,ra,dec)
    spec.appendChild(spatial)
    lib.appendChild(spec)
    bkg = xml.addCTAIrfBackground(lib)
    lib.appendChild(bkg)
    open(outfile.replace('txt','xml'), 'w').write(doc.toprettyxml('  '))


i = int(sys.argv[1])

#Define data and parameters
TableInfo = pyfits.open(environ.DIRS["INST_DIR"]+'/data/table_20161213.fits')
Gmin = 1.5
Gmax = 3.
Gstep = 0.1
alphamin = 0.1
alphamax = 2.1
alphastep = 0.1
norm = 1e-18 #PKS2155-304 normalisation Norm = 2.2293 10^{-16} cm^{-2} s^{-1} MeV^{-1}

# out =  join(os.getcwd(), "out")
AnalysisType = "DominguezNoCutOff"
#AnalysisType = "Dominguez3TeVCutOff"
eblmodel = "dominguez"
work = join(os.getcwd(), "work/"+AnalysisType)
out = join(os.getcwd(), "out/"+AnalysisType)
datapath = join(os.getcwd(), "out/"+AnalysisType)
# datapath = join("/gpfs/LAPP-DATA/cta/ScienceTools", AnalysisType)
os.system("mkdir -p "+work)

sourcename,ra,dec,z,_,_ = SimulScript.GetInfoFromTable(TableInfo,i)
data = join(datapath,sourcename+"_0.05TeV_event00001.fits")
############### Correct for EBL using EBL model
energy = np.logspace(-2,2,100) #TeV

tau = OD.readmodel(model = eblmodel)
TauEBL = tau.opt_depth(z,energy)
###############

simutime=100.
irfTime=CF.IrfChoice(simutime)
irf = "South_z20_"+str(int(float(irfTime)))+"h"
caldb = "prod3b"

for index in np.arange(Gmin,Gmax,Gstep):
    phi = powerlaw(energy,norm,index)
    for alpha in np.arange(alphamin,alphamax,alphastep):
        # create_fileFunctions(TauEBL, sourcename,phi,alpha,index)
        EBL_corrected_phi = phi*np.exp(-alpha * TauEBL)
        Filefunction = join(work,sourcename.replace(" ","").replace("-","m").replace("+","p")+"_alpha_"+str(alpha)+"_index_"+str(index)+".txt")
        CF.MakeFileFunction(energy*1e6,EBL_corrected_phi,Filefunction)

        config = CF.MakeconfigFromDefault(work,work,sourcename,ra,dec)
        config["file"]["inobs"] = data
        config["file"]["selectedevent"] = data.replace(".fits","_alpha_"+str(alpha)+"_index_"+str(index)+"_selected.fits")
        config["file"]["inmodel"] = Filefunction.replace("txt","xml")

        config["time"]["tmax"] = 20*3600

        config["irfs"]["irf"] = irf
        config["irfs"]["caldb"] = caldb


        config["energy"]["emin"] = 0.05
        config["energy"]["emax"] = 10

        config.write(open(Filefunction.replace("txt","conf"), 'w'))

        create_xml_from_fileFunctions(sourcename,ra,dec,Filefunction)
        cmd = "python  "+join(os.getcwd(), "Fit_Ctools.py")+" "+Filefunction.replace("txt","conf")
        # print cmd
        # os.system(cmd)
        call(cmd,Filefunction.replace("txt","sh"),Filefunction.replace("txt","log"))
