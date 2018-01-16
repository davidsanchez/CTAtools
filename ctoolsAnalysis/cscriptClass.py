# author David Sanchez david.sanchez@lapp.in2p3.fr
import ctools as ct
import gammalib as gl
import sys,os
from os.path import join
import ctoolsAnalysis.Loggin as Loggin
from ctoolsAnalysis.config import get_config
import ctoolsAnalysis.Common as Common

import csobsselect,csspec,cssrcdetect,csresmap

class CTA_ctools_script(Loggin.base,Common.CTA_ctools_common):
    def __init__(self,outdir='.',verbose = True):
        super(CTA_ctools_script,self).__init__()
        self.config  = None
        self.verbose = verbose
        Common.CTA_ctools_common.__init__(self,outdir=outdir)

    @classmethod
    def fromConfig(cls, config,verbose = True):
        obj = cls(outdir=config["out"],verbose = verbose)
        obj.config = config
        return obj


    def csobsselect(self,obsXml= None, log=False,debug=False, **kwargs):
        '''
        Create csobsselect instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running csobsselect to select data")

        self.csobsselect = csobsselect.csobsselect()
        self._fill_app( self.csobsselect,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.csobsselect["logfile"] = self.config['file']["tag"]+"_csobsselect.log"

        self.csobsselect["inobs"] = obsXml
        self.csobsselect["outobs"] = self.config["file"]["inobs"]
        self.csobsselect["pntselect"] = "CIRCLE"

        if self.verbose:
            print self.csobsselect

        self.csobsselect.run()
        self.csobsselect.save()
        self.info("csobsselect successfuly ran")
        
    def csspec(self,nbpoint=5, log=False,debug=False, **kwargs):
        '''
        Create csspec instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running csspec to make spectral point")

        self.csspec = csspec.csspec()
        self._fill_app( self.csspec,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.csspec["logfile"] = self.config['file']["tag"]+"_csspec.log"

        self.csspec["srcname"] = self.config["target"]["name"]
        self.csspec["enumbins"] = nbpoint
        #self.csspec["method"] = "AUTO" --> (for Barbara this option generates an error)
        self.csspec["outfile"] = "spectrum_"+self.config["target"]["name"]+".fits "
        
        if self.verbose:
            print self.csspec

        self.csspec.run()
        self.csspec.save()
        self.info("csspec successfuly ran")
        
        
    def cssrcdetect(self,threshold =10, log=False,debug=False, **kwargs):
        '''
        Create cssrcdetect instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running cssrcdetect to find new sources")

        self.cssrcdetect = cssrcdetect.cssrcdetect()
        self._fill_app( self.cssrcdetect,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.cssrcdetect["logfile"] = self.config['file']["tag"]+"_cssrcdetect.log"

        self.cssrcdetect["inmap"] = self.config["file"]["outmap"]
        self.cssrcdetect["outmodel"] = self.config["target"]["name"]+"_srcdetec.xml"
        self.cssrcdetect["outds9file"] = self.config["target"]["name"]+"_srcdetec.reg"
        self.cssrcdetect["srcmodel"] = "POINT"
        self.cssrcdetect["bkgmodel"] = self.config["SkyMap"]["bkgsubtract"]
        self.cssrcdetect["threshold"] = threshold
        
        if self.verbose:
            print self.cssrcdetect

        self.cssrcdetect.run()
        self.cssrcdetect.save()
        self.info("cssrcdetect successfuly ran")
        #-------------------detect new sources
        
    def csresmap(self, log=False,debug=False, **kwargs):
        '''
        Create resmap instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running csspec to make the residual map")

        self.csresmap = csresmap.csresmap()
        self._fill_app( self.csresmap,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.csresmap["logfile"] = self.config['file']["tag"]+"_resmap.log"

        self.csresmap["outmap"] = self.config["target"]["name"]+"_resmap.fits "
        self.csresmap["inmodel"] = self.config["file"]["inmodel"]
        self.csresmap["emin"] = self.config["energy"]["emin"]
        self.csresmap["emax"] = self.config["energy"]["emax"]
        self.csresmap["coordsys"] = "CEL"
        self.csresmap["proj"] = "CAR"
        self.csresmap["xref"] = self.config["target"]["ra"]
        self.csresmap["yref"] = self.config["target"]["dec"]
        self.csresmap["nxpix"] = 200
        self.csresmap["nypix"] = 200
        self.csresmap["binsz"] = 0.02
        self.csresmap["algorithm"] = "SIGNIFICANCE"
                
        if self.verbose:
            print self.csresmap

        self.csresmap.run()
        self.csresmap.save()
        self.info("csresmap successfuly ran")
