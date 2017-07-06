import os,sys
from os.path import join
import ctools
from ctoolsAnalysis.config import get_config,get_default_config
from ctoolsAnalysis.LikeFit import CTA_ctools_analyser
from Script.Common_Functions import *

Astropy = True
try :
    import Coordinates.CoordHandler as CH
    import Coordinates.CoordUtilities as CU
    from astropy.coordinates import FK5
except :
    Astropy = False

#define source name. This also allows to have the coordinate if you have astropy
source = "AP Librae"
ra = None
dec = None
if Astropy:
     coord = CH.CoordinatesHandler.fromName(source,FK5)
     ra, dec = CU.GetCoordInDegrees(coord)


#default work and out path. Not use if you provide a config file in the command line
out =  join(os.getcwd(), "out")
work = join(os.getcwd(), "work")

# setup : Time, Energy and IRFS. Not use if you provide a config file in the command line
tmin = 0
tmax = 3600

emin = 0.2
emax = 10

caldb = "prod2"
irf = "South_0.5h"
config = None

try:  #conf file provided
    config = get_config(sys.argv[-1])
    # config = MakeconfigFromFile(out,work,source,ra,dec,config_tmp)
    # config["file"]["inobs"] = sys.argv[-2]
    # print config
except:    #Not use if you provide a config file in the command line
    config = MakeconfigFromDefault(out,work,source,ra,dec)
    config["file"]["inobs"] = sys.argv[-1]
    config.write(open(work+"/Fit_"+source.replace(" ","")+".conf", 'w'))

Analyse = CTA_ctools_analyser.fromConfig(config)

#set up if there is no config file provided
if config == None :
    Analyse.SetTimeRange(tmin,tmax)
    Analyse.SetEnergyRange(emin,emax)
    Analyse.SetIRFs(caldb,irf)


# Analyse.like["outmodel"] = sys.argv[-1].replace(".conf","_results.xml")
# print "Out XML ",Analyse.like["outmodel"]
Analyse.ctselect()
Analyse.create_fit(log = True,debug = False)
Analyse.fit()
Analyse.PrintResults()
print "LogLike value for ",sys.argv[-1]," ", Analyse.like.obs().logL()
