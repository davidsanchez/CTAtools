import os,numpy
cwd = os.getcwd()+"/"+srcname
os.system("mkdir -p "+cwd)
import Script.Common_Functions as CF
from ctoolsAnalysis.config import get_config,get_default_config

data = numpy.genfromtxt("AGN_Monitoring_list.dat",dtype=str,unpack=True)

for i in xrange(len(data[0])):
    srcname = data[0][i]+data[1][i]
    ra = data[2][i]
    dec = data[3][i]
    print srcname," ",ra," ",dec
    z = 0.2
    config = get_config('Template.conf')
    config = CF.MakeconfigFromFile(cwd,srcname,ra,dec,'Template.conf')

    config['out'] = cwd
    config['file']['inobs'] = cwd+"/outobs_"+srcname+".xml"
    config['file']['selectedevent'] = cwd+"/outobs_"+srcname+"_selected.xml"
    config['file']['inmodel'] = cwd+"/"+srcname+".xml"
    config["file"]["tag"] = srcname+"_DC1"
    config["file"]["outmap"] = cwd+"/"+srcname+"_DC1_skymap.fits"
    
    config["space"]["xref"] = ra
    config["space"]["yref"] = dec

    from ebltable.tau_from_model import OptDepth as OD
    tau = OD.readmodel(model = 'dominguez')
    # array with energies in TeV
    ETeV = numpy.logspace(-1,1,50)
    Tau_dominguez = tau.opt_depth(z,ETeV)

    Etau = numpy.interp([1.],Tau_dominguez,ETeV)
    config['energy']['emin'] = 0.2

    config.write(open(srcname+"_DC1.conf", 'w'))
