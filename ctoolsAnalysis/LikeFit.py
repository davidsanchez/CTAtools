# author David Sanchez david.sanchez@lapp.in2p3.fr
import ctools as ct
import gammalib as gl
import sys,os
from os.path import join
import ctoolsAnalysis.Loggin as Loggin
from ctoolsAnalysis.config import get_config
import ctoolsAnalysis.Common as Common


class CTA_ctools_analyser(Loggin.base,Common.CTA_ctools_common):
    def __init__(self,outdir='.',verbose = True):
        super(CTA_ctools_analyser,self).__init__()
        self.m_obs = None
        self.like  = None
        self.config  = None
        self.verbose = verbose
        Common.CTA_ctools_common.__init__(self,outdir=outdir)

    @classmethod
    def fromConfig(cls, config,verbose = True):
        obj = cls(outdir=config["out"],verbose = verbose)
        obj.config = config
        return obj

    def set_obs(self,obs):
        self.m_obs = obs #set the GObservation container


    def ctselect(self, log=False,debug=False, **kwargs):
        '''
        Create ctselect instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctselect to cut on events")

        self.filter = ct.ctselect()
        self._fill_app( self.filter,log=log,debug=debug, **kwargs)

        self.filter["outobs"] = join(self.outdir,self.config['file']["selectedevent"])

        if self.verbose:
            print self.filter

        self.filter.run()

        self.filter.save()
        self.info("Saved selected events to {0:s}".format(self.filter["outobs"]))

        # change the inobs (data) to the selected data set
        self.config['file']["inobs"] = self.config['file']["selectedevent"]

        del self.filter

    def ctskymap(self,log=False,debug=False, **kwargs):
        '''
        Create ctskymap instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctskymap to make map")


        self.skymap = ct.ctskymap()
        
        self._fill_app( self.skymap,log=log,debug=debug, **kwargs)

        self.skymap["xref"] = self.config['target']["ra"]
        self.skymap["yref"] = self.config['target']["dec"]

        if self.verbose:
            print self.skymap

        self.skymap.run()

        self.skymap.save()
        self.info("Saved sky map to {0:s}".format(self.skymap["outmap"]))

        del self.skymap

    def ctmodel(self,obsXml= None, log=False,debug=False, **kwargs):
        '''
        Create ctmodel instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctmodel to create model map")

        self.model= ct.ctmodel()

        self._fill_app( self.model,log=log,debug=debug, **kwargs)

        self.model["incube"] = join(self.outdir,self.config['file']["cntcube"])
        self.model["outcube"] = join(self.outdir,self.config['file']["model"])

        if self.verbose:
            print self.model

        # Run ctmodel application. This will loop over all observations in
        # the container and bin the events in counts maps
        self.model.run()
        self.model.save()
        self.info("Saved Model cube to {0:s}".format(self.model["outcube"]))

        del self.model

    def ctbin(self,obsXml= None, log=False,debug=False, **kwargs):
        '''
        Create ctbin instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctbin to create count map")

        self.bin = ct.ctbin()

        self._fill_app( self.bin,log=log,debug=debug, **kwargs)
        self.bin["outcube"] = join(self.outdir,self.config['file']["cntcube"])

        if self.verbose:
            print self.bin

        # Run ctbin application. This will loop over all observations in
        # the container and bin the events in counts maps
        self.bin.run()

        self.bin.save()
        self.info("Saved counts cube to {0:s}".format(self.bin["outcube"]))

        self.bin

    def create_fit(self,log=False,debug=False, **kwargs):
        '''
        Create ctlike instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Fitting Data using ctlike")
        if self.m_obs:
            self.like = ct.ctlike(self.m_obs)
        else:
            self.like = ct.ctlike()
            self._fill_app(self.like,log=log,debug=debug, **kwargs)

            if self.config["analysis"]["likelihood"] == "binned":
                self.like["inobs"] = join(self.outdir,self.config['file']["cntcube"])

        self.like["outmodel"] = self.config['out']+"/"+self.config['file']["tag"]+"_results.xml"
        self.like["edisp"] = self.config['analysis']["edisp"]

        if self.verbose:
            print self.like

    def fit(self,log=False,debug=False):
        '''
        Actually run the fit. Create a like object if this has not be already done
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        if not(self.like):
            self.warning("ctlike object not created, creating now")
            self.create_fit(log,debug)

        # Run ctlike application.
        self.like.run()
        # Save the results in XML
        self.like.save()
        self.success("Fit performed")


    def PrintResults(self,srcname = ""):
        self.info("Results of the Fit")
        print self.like.obs().models()
        
    def ctbutterfly(self,log=False,debug=False, **kwargs):
        '''
        Create butterfly instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctbuttefly to make butterfly plot")

        self.ctbutterfly = ct.ctbutterfly(self.like.obs())
        
        self._fill_app( self.ctbutterfly,log=log,debug=debug, **kwargs)

        self.ctbutterfly["srcname"]=self.config["target"]["name"]
        self.ctbutterfly["outfile"] = self.config["target"]["name"]+"_butterfly.dat "

        if self.verbose:
            print self.ctbutterfly

        self.ctbutterfly.run()

        self.ctbutterfly.save()
        self.info("Saved butterfly plot to {0:s}".format(self.ctbutterfly["outfile"]))


        self.ctbutterfly

    def ctexpcube(self,log=False,debug=False, **kwargs):
        '''
        Create ctexpcube instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctexpcube to compute the instrument response for the counts cube")


        self.expcube = ct.ctexpcube()
        
        self._fill_app( self.expcube,log=log,debug=debug, **kwargs)

        self.expcube["incube"] = self.config['file']["cntcube"]
        self.expcube["outcube"] = self.config['file']["expcube"]

        if self.verbose:
            print self.expcube

        self.expcube.run()

        self.expcube.save()
        self.info("Saved expcube to {0:s}".format(self.expcube["outcube"]))

        self.expcube

    def ctpsfcube(self,log=False,debug=False, **kwargs):
        '''
        Create ctpsfcube instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctpsfcube to compute point spread function (PSF) cube")

        self.ctpsfcube = ct.ctpsfcube()
        
        self._fill_app( self.ctpsfcube,log=log,debug=debug, **kwargs)

        self.ctpsfcube["incube"] = self.config['file']["cntcube"]
        self.ctpsfcube["outcube"] = self.config['file']["psfcube"]

        if self.verbose:
            print self.ctpsfcube

        self.ctpsfcube.run()

        self.ctpsfcube.save()
        self.info("Saved psfcube to {0:s}".format(self.ctpsfcube["outcube"]))

        self.ctpsfcube

    def ctbkgcube(self,log=False,debug=False, **kwargs):
        '''
        Create ctbkgcube instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctbkgcube to compute the predicted background rate")

        self.ctbkgcube = ct.ctbkgcube()
        
        self._fill_app( self.ctbkgcube,log=log,debug=debug, **kwargs)

        self.ctbkgcube["incube"] = self.config['file']["cntcube"]
        self.ctbkgcube["outcube"] = self.config['file']["bkgcube"]

        self.ctbkgcube["outmodel"] = self.config['out']+"/binned_models.xml"
        self.config["file"]["inmodel"] = self.config['out']+"/binned_models.xml"

        if self.verbose:
            print self.ctbkgcube

        self.ctbkgcube.run()

        self.ctbkgcube.save()
        self.info("Saved background cube to {0:s}".format(self.ctbkgcube["outcube"]))

        self.ctbkgcube

    def ctedispcube(self,log=False,debug=False, **kwargs):
        '''
        Create ctbkgcube instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctedispcube to compute the edisp rate")

        self.ctedispcube = ct.ctedispcube()
        
        self._fill_app( self.ctedispcube,log=log,debug=debug, **kwargs)

        self.ctedispcube["incube"] = self.config['file']["cntcube"]
        self.ctedispcube["outcube"] = self.config['file']["edispcube"]

        if self.verbose:
            print self.ctedispcube

        self.ctedispcube.run()

        self.ctedispcube.save()
        self.info("Saved edisp cube to {0:s}".format(self.ctedispcube["outcube"]))

        del self.ctedispcube