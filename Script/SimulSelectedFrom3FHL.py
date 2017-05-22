#Created to read salvatore table, read 3FHL data and etrapolated (Using Biteau prescription) and simulate with CTOOLS
# Made for Rio 2017.

# author David Sanchez david.sanchez@lapp.in2p3.fr
# Gate Florian
# Piel Quentin

# ------ Imports --------------- #
import numpy,math,pyfits,os
from Plot.PlotLibrary import *
from Catalog.ReadFermiCatalog import *
from environ import FERMI_CATALOG_DIR,INST_DIR
from Plot.PlotLibrary import *
from ebltable.tau_from_model import OptDepth as OD
import Common_Functions as CF
import ctoolsAnalysis.xml_generator as xml
from ctoolsAnalysis.config import get_config,get_default_config
from ctoolsAnalysis.SimulateSource import CTA_ctools_sim
# ------------------------------ #

out='/Users/gateflorian/Documents/devCTAtools/CTAtools/Script/out'
work='/Users/gateflorian/Documents/devCTAtools/CTAtools/Script/work'

def GetInfoFromTable(fitstable,indice):
    '''read salvatore table and return info corresponding to the source at the place indice
    Parameters
    ---------
    fitstable : pyfits object : table to be browsed
    indice : place of the source in the table 
    '''
    data = fitstable[1].data[indice]
    sourcename = data[0]
    ra = data[1]
    dec = data[2]
    z = data[4]
    
    if math.isnan(z):
        z=0
    hemisphere = data[6]
    observation_type = data[8]
    if hemisphere =='S':
        hemisphere ='South'
    if hemisphere =='N':
        hemisphere ='North'

    return sourcename,ra,dec,z,hemisphere,observation_type
    
    
def cutoff(energy):
    '''correct with JB cut off prescription
    Parameters
    ---------
    energy : in TeV.
    '''
    return numpy.exp(-energy*3/(1+z))
    
def ComputeExtrapolateSpectrum(sourcename,z,eblmodel = "dominguez",alpha = -1):
    try :
        Cat = FermiCatalogReader.fromName(sourcename,FK5,FERMI_CATALOG_DIR,"dnde","MeV") #read 3FHL
    except :
        print 'can read 3FHL for some reason, returning'
        return
    emin = 1e5 #Mev
    emax = 1e8
    Cat.MakeSpectrum("3FHL",emin,emax)
    _,_,energy,phi = Cat.Plot("3FHL")
    SpectreWithCutoff = cutoff(energy/1e6)
    
    #Correct for EBL using Dominguez model
    tau = OD(model = eblmodel)
    TauEBL = tau.opt_depth_array(z,energy/1e6)

    Etau2 = numpy.interp([2.],TauEBL[0],energy/1e6)*1e6 # Input in TeV -> Get MeV at the end
    
    EBL_corrected_phi = phi*numpy.exp(alpha * TauEBL[0])

    phi_extrapolated = EBL_corrected_phi*SpectreWithCutoff

    os.system("mkdir -p out")
    outfile = INST_DIR+"/Script/out/"+sourcename.replace(" ","")+"_File.txt"
    CF.MakeFileFunction(energy,phi_extrapolated,outfile)
    
    return outfile, Etau2

TableInfo = pyfits.open(INST_DIR+'/data/table_20161213.fits')
outfolder = "out"
os.system("mkdir -p "+outfolder)
simutime = 20 #Hours

sourcename,ra,dec,z,hemisphere,_ = GetInfoFromTable(TableInfo,11)
print 'work on source ',sourcename,' at a redsift of z=',z
filefunction, Etau2 = ComputeExtrapolateSpectrum(sourcename,z)

########### Create XML
lib,doc = xml.CreateLib()
spec = xml.addFileFunction(lib, sourcename, type = "PointSource",filefun=filefunction,flux_free=1, flux_value=1., flux_scale=1.,flux_max=100000000.0, flux_min=0.0)
spatial = xml.AddPointLike(doc,ra,dec)

spec.appendChild(spatial)
lib.appendChild(spec)

bkg = xml.addCTAIrfBackground(lib)
lib.appendChild(bkg)
open(outfolder+"/"+sourcename.replace(" ","")+'.xml', 'w').write(doc.toprettyxml('  '))
#######################


irfTime = CF.IrfChoice(simutime)

# setup : Time, Energy and IRFS.
tmin = 0
tmax = int(simutime*3600)
emin_table =[0.05,Etau2*1e-6] #TeV 
emax = 100 #TeV
irf = "South_z20_"+str(irfTime)+"h"
caldb = "prod3b"


config = CF.MakeconfigFromDefault(out,work,sourcename,ra,dec)
config.write(open("simu_"+sourcename.replace(" ","")+"_"+str(simutime)+"h"+".conf", 'w'))

#creation of the simulation object    
simu = CTA_ctools_sim.fromConfig(config)

simu.SetTimeRange(tmin,tmax)
simu.SetIRFs(caldb,irf)

for emin in emin_table:
    simu.SetEnergyRange(emin,emax)

    simu.config.write(open(work+"/simu_"+sourcename.replace(" ","")+".conf", 'w'))
    # run the simulation
    simu.run_sim(prefix = sourcename.replace(" ","") ,nsim = 1, write=True, clobber = True)
    simu.Print()
