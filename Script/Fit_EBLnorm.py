import os,sys,pyfits,math
from os.path import join
import ctools
import Common_Functions as CF
import numpy as np
from environ import INST_DIR
from Plot.PlotLibrary import *
from Catalog.ReadFermiCatalog import *
from Plot.PlotLibrary import *
from ebltable.tau_from_model import OptDepth as OD
import ctoolsAnalysis.xml_generator as xml
from ctoolsAnalysis.LikeFit import CTA_ctools_analyser




#logparabola func to fit
powerlaw = lambda x,norm,gamma, : norm * (x / .1) ** (-gamma)
#create Energy data
energy = np.logspace(4,8,100) #MeV

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


def create_fileFunctions(tau , sourcename ,phi,alpha,index):
    '''
    Create a file function for given alpha and index
    Parameters
    ---------
    tau: EBL effect
    sourcename: studied source
    phi: Points flux
    alpha: EBL normalisation
    index: index of the power law
    '''
    EBL_corrected_phi = phi*np.exp(-alpha * tau[0])
    os.system("mkdir -p out")
    outfile = INST_DIR+"/Script/out/"+sourcename.replace(" ","")+"_alpha="+str(alpha)+"_index="+str(index)+".txt"
    CF.MakeFileFunction(energy,EBL_corrected_phi,outfile)



def create_xml_from_fileFunctions(sourcename,ra,dec,alpha,index):
    '''
    Create xml file for given alpha and index 
    Parameters
    ---------
    sourcename: studied source
    ra,dec: coordinates of the source
    alpha: EBL normalisation
    index: index of the power law
    '''
    outfile = INST_DIR+"/Script/out/"+sourcename.replace(" ","")+"_alpha="+str(alpha)+"_index="+str(index)+".txt"
    lib,doc = xml.CreateLib()
    spec = xml.addFileFunction(lib, sourcename, type = "PointSource",filefun=outfile,flux_free=1, flux_value=1., flux_scale=1.,flux_max=100000000.0, flux_min=0.0)
    spatial = xml.AddPointLike(doc,ra,dec)
    spec.appendChild(spatial)
    lib.appendChild(spec)
    bkg = xml.addCTAIrfBackground(lib)
    lib.appendChild(bkg)
    open(INST_DIR+"/Script/out/"+sourcename.replace(" ","")+'forSimu3FGLPosition_'+str(alpha)+'_'+str(index)+'.xml', 'w').write(doc.toprettyxml('  '))

def fit_fileFuntions(ra,dec,alpha,index):
    '''
    #Do the fit of the simulated events by the created file function 
    Parameters
    ---------
    ra,dec: coordinates of the source
    alpha: EBL normalisation
    index: index of the power law
    '''

    out = INST_DIR+"/Script/out/"
    work = INST_DIR+"/Script/work/"
    #####################   Choice of the IRF and calibration
    simutime=100.
    irfTime=CF.IrfChoice(simutime)
    irf = "South_z20_"+str(int(float(irfTime)))+"h"  
    caldb = "prod3b"
    
    fitsFile = out+"/"+sourcename.replace(" ","")+"_event00001.fits"
    config = CF.MakeconfigFromDefault(out,work,sourcename,ra,dec)
    config["file"]["inobs"] = fitsFile
    config.write(open(work+"/"+sourcename.replace(" ","")+"_"+str(simutime)+"h"+".conf", 'w'))
    Analyse = CTA_ctools_analyser.fromConfig(config)
    #set up if there is no config file provided
    if len(sys.argv) == 1 :
        Analyse.SetIRFs(caldb,irf)
        Analyse.SetModel(out+"/"+sourcename.replace(" ","")+'forSimu3FGLPosition_'+str(alpha)+'_'+str(index)+'.xml')

    Analyse.create_fit(log = True,debug = False)
    Analyse.fit()
    Analyse.PrintResults()
    
def getValuets(param,sourcename):
    fichier = open(INST_DIR+'/Script/out/'+sourcename.replace(" ","")+'_results.xml','r')
    with  fichier as f:      
        for lines in f:  
            if lines.find(param+"=") != -1:
                #print "num ligne= ", lines
                    
                num = lines.index(param+"=")
                linetmp = lines[num+len(param)+2:]
                num_max = linetmp.index('"')
                value_param = float(lines[num+len(param)+2:num_max+len(param)+2+num])
                #print param+"="+str(value_param)
    fichier.close()
    return value_param

i = int(sys.argv[1])

#Define data and parameters
TableInfo = pyfits.open(INST_DIR+'/data/table_20161213.fits')
Gmin = 1.5
Gmax=6.
Gstep = 0.5 
alphamin = 0.1
alphamax = 1.5
alphastep = 0.1
norm = 2.2293e-16 #PKS2155-304 normalisation Norm = 2.2293 10^{-16} cm^{-2} s^{-1} MeV^{-1}
eblmodel = "dominguez"
out = INST_DIR+"/Script/out/"
work = INST_DIR+"/Script/work/"

#for i in range(221,221): #Long-term monitoring sources are between 215 and 228 in Salvatore's fits file
print 'i=',i
line = ''
sourcename,ra,dec,z,_,_ = GetInfoFromTable(TableInfo,i)
#Correct for EBL using EBL model
tau = OD(model = eblmodel)
TauEBL = tau.opt_depth_array(z,energy/1e6)

for index in np.arange(Gmin,Gmax,Gstep):
    phi = powerlaw(energy,norm,index)

    for alpha in np.arange(alphamin,alphamax,alphastep):
        print index,'/',Gmax,'    ',alpha,'/',alphamax
        create_fileFunctions(TauEBL, sourcename,phi,alpha,index)
        create_xml_from_fileFunctions(sourcename,ra,dec,alpha,index)
        fit_fileFuntions(ra,dec,alpha,index)
        ts=getValuets("ts",sourcename)
        line = line +str(alpha) + '\t' + str(index) + '\t' + str(ts) + '\n'
fichier = open(out+"/"+sourcename.replace(" ","")+"_results.txt", "w")
fichier.write(line)
fichier.close()





