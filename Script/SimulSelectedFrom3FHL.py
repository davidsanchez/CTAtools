#Created to read salvatore table, read 3FHL data and etrapolated (Using Biteau prescription) and simulate with CTOOLS
# Made for Rio 2017.

# author David Sanchez david.sanchez@lapp.in2p3.fr
# Gate Florian
# Piel Quentin

# ------ Imports --------------- #
import numpy,math,pyfits,os,sys
from Plot.PlotLibrary import *
from Catalog.ReadFermiCatalog import *
from environ import FERMI_CATALOG_DIR,INST_DIR
from Plot.PlotLibrary import *
from ebltable.tau_from_model import OptDepth as OD
from os.path import join
import Script.Common_Functions as CF
import ctoolsAnalysis.xml_generator as xml
from ctoolsAnalysis.config import get_config,get_default_config
from ctoolsAnalysis.SimulateSource import CTA_ctools_sim
from submit import call
# ------------------------------ #




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


def cutoff(energy,z):
    '''correct with JB cut off prescription
    Parameters
    ---------
    energy : in TeV.
    '''
    return numpy.exp(-energy/(3./(1+z)))

def ComputeExtrapolateSpectrum(sourcename,z,eblmodel = "dominguez",alpha = -1,out="."):
    try :
        Cat = FermiCatalogReader.fromName(sourcename,FK5,FERMI_CATALOG_DIR,"dnde","MeV") #read 3FHL
    except :
        print 'cannot read 3FHL for some reason, returning'
        return
    emin = 5e4 #Mev
    emax = 100e6
    params = Cat.ReadPL("3FHL")
    print params
    spec = Spectrum(params,Model="PowerLaw",Emin=emin,
                                Emax=emax,Representation="dnde",escale="MeV",
                                Npt=1000)
    energy,phi = spec.GetModel()
    # Cat.MakeSpectrum("3FHL",emin,emax)
    # _,_,energy,phi = Cat.Plot("3FHL")
    SpectreWithCutoff = cutoff(energy/1e6,z)

    #Correct for EBL using Dominguez model
    tau = OD.readmodel(model = eblmodel)
    TauEBL = tau.opt_depth(z,energy/1e6)

    Etau2 = numpy.interp([2.],TauEBL,energy/1e6)*1e6 # Input in TeV -> Get MeV at the end

    EBL_corrected_phi = phi*numpy.exp(alpha * TauEBL)

    phi_extrapolated = EBL_corrected_phi*SpectreWithCutoff
    # phi_extrapolated = EBL_corrected_phi

    outfile = out+"/"+sourcename.replace(" ","")+"_File.txt"
    CF.MakeFileFunction(energy,phi_extrapolated+1e-300,outfile)

    return outfile, Etau2

if __name__=="__main__":
    TableInfo = pyfits.open(INST_DIR+'/data/table_20161213.fits')
    outfolder = join(os.getcwd(), "out/Dominguez3TeVCutOff")
    # outfolder = join(os.getcwd(), "out/DominguezNoCutOff")
    #default work and out path.
    work = join(os.getcwd(), "work")
    os.system("mkdir -p "+outfolder)

    i = int(sys.argv[1])

    sourcename,ra,dec,z,hemisphere,_ = GetInfoFromTable(TableInfo,i)
    print 'work on source ',sourcename,' at a redsift of z=',z
    Filefunction, Etau2 = ComputeExtrapolateSpectrum(sourcename,z,eblmodel = "dominguez",alpha = -1,out=outfolder)

    ########### Create XML
    lib,doc = xml.CreateLib()
    spec = xml.addFileFunction(lib, sourcename, type = "PointSource",filefun=Filefunction,flux_free=1, flux_value=1., flux_scale=1.,flux_max=100000000.0, flux_min=0.0)
    spatial = xml.AddPointLike(doc,ra,dec)

    spec.appendChild(spatial)
    lib.appendChild(spec)

    bkg = xml.addCTAIrfBackground(lib)
    lib.appendChild(bkg)
    open(Filefunction.replace("_File.txt",'.xml'), 'w').write(doc.toprettyxml('  '))
    #######################

    simutime = 100 #Hours
    irfTime = CF.IrfChoice(simutime)

    # setup : Time, Energy and IRFS.
    tmin = 0
    tmax = int(simutime*3600)
    emin_table =[0.05,Etau2*1e-6] #TeV
    emax = 100 #TeV
    irf = "South_z20_"+str(irfTime.replace(".0",""))+"h"
    caldb = "prod3b"


    config = CF.MakeconfigFromDefault(outfolder,work,sourcename,ra,dec)
    # config.write(open("simu_"+sourcename.replace(" ","")+"_"+str(simutime)+"h"+".conf", 'w'))

    for emin in emin_table:
	print 'simu'
        #creation of the simulation object
        # simu = CTA_ctools_sim.fromConfig(config)

        # simu.SetTimeRange(tmin,tmax)
        # simu.SetIRFs(caldb,irf)
        # simu.SetEnergyRange(float(emin),emax)

        config["file"]["inmodel"] = Filefunction.replace("_File.txt",'.xml')

        config["time"]["tmin"] = tmin
        config["time"]["tmax"] = tmax

        config["irfs"]["irf"] = irf
        config["irfs"]["caldb"] = caldb


        config["energy"]["emin"] = float(emin)
        config["energy"]["emax"] = emax
        config_file = Filefunction.replace("_File.txt","_"+str(int(emin*100.)/100.)+"TeV"+".conf")
        config.write(open(config_file, 'w'))
        print "save configuration file ",config_file
        # run the simulation
        cmd = "python  "+join(os.getcwd(), "Simulate_Ctools.py")+" "+config_file
        call(cmd,config_file.replace(".conf",".sh"),config_file.replace(".conf",".log"))
        # os.system(cmd)
