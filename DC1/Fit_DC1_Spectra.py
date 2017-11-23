
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
spec = xml.addPowerLaw1(lib,srcname,"PointSource",flux_value=1e-14)
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

open(srcname+'.xml', 'w').write(doc.toprettyxml('  '))

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

#------------------- fit the data
Analyse.create_fit(log = True,debug = False)
Analyse.fit()
Analyse.PrintResults()
# print "LogLike value for ",sys.argv[-1]," ", Analyse.like.obs().logL()

#------------------- make spectral point
import csspec
app = csspec.csspec(Analyse.like.obs())
#app["inobs"]=config["file"]["inobs"]
#app["inmodel"]=config["file"]["inmodel"]
app["srcname"]=config["target"]["name"]
app["ebinalg"]="LOG"

app["emin"]=config["energy"]["emin"]
app["emax"]=config["energy"]["emax"]
app["enumbins"]= 5
app["method"] = "AUTO"
app["outfile"] = "spectrum_"+srcname+".fits "
app.execute()

#------------------- plot the points
import show_spectrum
show_spectrum.plot_spectrum(app["outfile"].value(),app["outfile"].value().replace("fits","png"))

