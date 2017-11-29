
import os,sys
from os.path import join
import ctools
from ctoolsAnalysis.config import get_config,get_default_config
from ctoolsAnalysis.LikeFit import CTA_ctools_analyser
from Script.Common_Functions import *
import  ctoolsAnalysis.xml_generator as xml
# ------------------------------ #
try:
    get_ipython().magic(u'pylab')
except :
    pass


try:  #conf file provided
    config = get_config(sys.argv[-1])
except :
    print "usage : python "+sys.argv[0]+" config_file"
    exit()


#------------------ Make the XML model
lib,doc = xml.CreateLib()


srcname = config["target"]["name"]
#SOURCE SPECTRUM
spec = xml.addPowerLaw1(lib,srcname,"PointSource",flux_value=1e-14,flux_max=1000.0, flux_min=1e-5)
ra = config["target"]["ra"]
dec = config["target"]["dec"]
spatial = xml.AddPointLike(doc,ra,dec)
spec.appendChild(spatial)
lib.appendChild(spec)


#CTA BACKGROUND
#bkg = xml.addCTABackgroundPolynom(lib,[.1,.1,3,5],[0,1,1,1])
#bkg = xml.addCTABackgroundProfile(lib)
bkg = xml.addCTAIrfBackground(lib)
lib.appendChild(bkg)

#open(srcname+'.xml', 'w').write(doc.toprettyxml('  '))

#--------------------------

import matplotlib.pyplot as plt

#----------------- make the first DC1 selection 
import csobsselect
selection = csobsselect.csobsselect()
selection["inobs"] = "$CTADATA/obs/obs_agn_baseline.xml"
selection["outobs"] = config["file"]["inobs"]

selection["pntselect"] = "CIRCLE"
selection["coordsys"] = "CEL"
selection["ra"] = ra
selection["dec"] = dec
selection["rad"] = 3.0
selection.execute()
print selection

#------------------- Select the files
Analyse = CTA_ctools_analyser.fromConfig(config)
Analyse.ctselect(log = True)

#------------------- make a skymap
Analyse.ctskymap(log = True)

#-------------------detect new sources
import cssrcdetect
srcdetect = cssrcdetect.cssrcdetect()
srcdetect["inmap"] = config["file"]["outmap"]
srcdetect["outmodel"] = srcname+"_srcdetec.xml"
srcdetect["outds9file"] = srcname+"_srcdetec.reg"
srcdetect["srcmodel"] = "POINT"
srcdetect["bkgmodel"] = config["SkyMap"]["bkgsubtract"]
srcdetect["threshold"] = 10.
srcdetect.run()
srcdetect.save()
