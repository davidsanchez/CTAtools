# author David Sanchez david.sanchez@lapp.in2p3.fr
import ctools as ct
import gammalib as gl
import sys,os
from os.path import join
import ctoolsAnalysis.Loggin as Loggin
from ctoolsAnalysis.config import get_config
import ctoolsAnalysis.Common as Common

import csobsselect,csspec,cssrcdetect,csresmap,csresspec,csphagen

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
        if log:
            self.csobsselect.logFileOpen()

        self.csobsselect["inobs"] = obsXml
        self.csobsselect["outobs"] = self.config["file"]["inobs"]
        self.csobsselect["pntselect"] = "CIRCLE"

        if self.verbose:
            print self.csobsselect

        self.csobsselect.run()
        self.csobsselect.save()
        self.info("csobsselect successfully ran")
        
    #def csspec(self,nbpoint=5, log=False,debug=False, **kwargs):
    def csspec(self,nbpoint, log=False,debug=False, **kwargs):
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
        if log:
            self.csspec.logFileOpen()

        self.csspec["srcname"] = self.config["target"]["name"]
        self.csspec["enumbins"] = nbpoint
        self.csspec["method"] = "AUTO"
        self.csspec["outfile"] = "spectrum_"+self.config["target"]["name"]+".fits "
        
        if self.verbose:
            print self.csspec

        self.csspec.run()
        self.csspec.save()
        self.info("csspec successfully ran")
        
        
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
        if log:
            self.cssrcdetect.logFileOpen()

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
        self.info("cssrcdetect successfully ran")
        #-------------------detect new sources
        
    def csresmap(self, log=False,debug=False, **kwargs):
        '''
        Create resmap instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running csresmap to make the residual map")

        self.csresmap = csresmap.csresmap()
        self._fill_app( self.csresmap,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.csresmap["logfile"] = self.config['file']["tag"]+"_resmap.log"
        if log:
            self.csresmap.logFileOpen()

        self.csresmap["outmap"] = self.config["target"]["name"]+"_resmap.fits "
        self.csresmap["xref"] = self.config["target"]["ra"]
        self.csresmap["yref"] = self.config["target"]["dec"]
        self.csresmap["algorithm"] = "SIGNIFICANCE"
                
        if self.verbose:
            print self.csresmap

        self.csresmap.run()
        self.csresmap.save()
        self.info("csresmap successfully ran")


    def csresspec(self, log=False,debug=False, **kwargs):
        '''
        Create csobsselect instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running csresspec")

        self.csresspec = csresspec.csresspec()
        self._fill_app( self.csresspec,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.csresspec["logfile"] = self.config['file']["tag"]+"_csresspec.log"
        if log:
            self.csresspec.logFileOpen()

        self.csresspec["components"] = True
        self.csresspec["stack"] = True
        self.csresspec["mask"] = False
        self.csresspec["algorithm"] = "SIGNIFICANCE"
        self.csresspec["outfile"] = self.config['file']["tag"]+"_csresspec.fits"

        if self.verbose:
            print self.csresspec

        self.csresspec.run()
        self.csresspec.save()
        self.info("csresspec successfully ran")

    #def csphagen(self, log=False,debug=False, **kwargs):
    def csphagen(self, nbin, log=False,debug=False, **kwargs):
        '''
        Create csphagen instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running csphagen for ON/OFF analysis in energy bins")
        self.csphagen = csphagen.csphagen()
        self._fill_app( self.csphagen,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.csphagen["logfile"] = self.config['file']["tag"]+"_csphagen.log"
        if log:
            self.csphagen.logFileOpen()

        self.csphagen["inobs"] = self.config['file']["selectedevent"]
        self.csphagen["stack"] = True
        self.csphagen["bkgmethod"] = "REFLECTED"
        self.csphagen["rad"] = 0.2
        self.csphagen["outobs"] = self.config["out"]+"/"+self.config["target"]["name"]+"_csphagen.xml"

        self.csphagen["prefix"] = self.config["target"]["name"]+"_onoff"

        if self.verbose:
            print self.csphagen

        self.csphagen.run()
        self.csphagen.save()
        self.info("csphagen successfully ran")
