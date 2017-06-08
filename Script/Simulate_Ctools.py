import os,sys
from os.path import join
import ctools
from ctoolsAnalysis.config import get_config,get_default_config
from ctoolsAnalysis.SimulateSource import CTA_ctools_sim
from Common_Functions import *

Astropy = True
try :
    import Coordinates.CoordHandler as CH
    import Coordinates.CoordUtilities as CU
    from astropy.coordinates import FK5
except :
    Astropy = False

#define source name. This also allows to have the coordinate if you have astropy
source = "AP Librae"
ra = 229.42423006
dec = -24.3720738456
if Astropy:
     coord = CH.CoordinatesHandler.fromName(source,FK5)
     ra, dec = CU.GetCoordInDegrees(coord)

#default work and out path. Not use if you provide a config file in the command line
out =  join(os.getcwd(), "out")
work = join(os.getcwd(), "work")

# setup : Time, Energy and IRFS. Not use if you provide a config file in the command line
tmin = 0
tmax = 36000

emin = 0.2
emax = 10

caldb = "prod2"
irf = "South_0.5h"

# Not use if you provide a config file in the command line
try :#conf file provided
    config_tmp = get_config(sys.argv[1])
    config = MakeconfigFromFile(out,work,source,ra,dec,config_tmp)
except :
    config = MakeconfigFromDefault(out,work,source,ra,dec)
    config.write(open("simu_"+source.replace(" ","")+".conf", 'w'))

#creation of the simulation object
simu = CTA_ctools_sim.fromConfig(config)

#set up if there is no config file provided
if len(sys.argv) == 1 :
    simu.SetTimeRange(tmin,tmax)
    simu.SetEnergyRange(emin,emax)
    simu.SetIRFs(caldb,irf)

simu.config.write(open(work+"/simu_"+source.replace(" ","")+".conf", 'w'))
# run
simu.run_sim(prefix = source.replace(" ","") ,nsim = 1, write=True, clobber = True)
simu.Print()
