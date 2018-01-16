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


    def ctselect(self,obsXml= None, log=False,debug=False, **kwargs):
        '''
        Create ctselect instance with given parameters
        Parameters
        ---------
        log  : save or not the log file
        debug  : debug mode or not. This will print a lot of information
        '''
        self.info("Running ctselect to cut on events")


        self.filter = ct.ctselect()
        Fits_provided = False
        if obsXml:
            sim_obs = gl.GObservations(obsXml)
        elif self.config['file']["inobs"] != '':
            sim_obs = join(self.outdir,self.config['file']["inobs"])
            Fits_provided = True
        else:
            try:
                sim_obs = self.m_obs
            except:
                self.error("No observation given and no simulation run.")

        self.selectobs     = gl.GObservations()

        eventfile = sim_obs if Fits_provided else sim_obs.eventfile()

        self._fill_app( self.filter,log=log,debug=debug, **kwargs)
            
        self.filter["inobs"] = eventfile
        self.filter["outobs"] = join(self.outdir,self.config['file']["selectedevent"])

        # Optionally open the log file
        self.filter["logfile"] = self.config['file']["tag"]+"_ctselect.log"
        if log:
            self.filter.logFileOpen()

        # Optionally switch-on debugging model
        if debug:
            self.filter["debug"].boolean(True)

        if self.verbose:
            print self.filter

        self.filter.run()
        # if not(self.m_obs):
        self.filter.obs()[0].id(self.config['file']["selectedevent"])
        self.filter.obs()[0].eventfile(self.config['file']["selectedevent"])

        self.filter.save()
        self.info("Saved counts cube to {0:s}".format(self.filter["outobs"]))
        # Append result to observations
        self.selectobs.extend(self.filter.obs())

        # change the inobs (data) to the selected data set
        self.config['file']["inobs"] = self.config['file']["selectedevent"]


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

        # Optionally open the log file
        self.skymap["logfile"] = self.config['file']["tag"]+"_ctskymap.log"
        if log:
            self.skymap.logFileOpen()

        # Optionally switch-on debugging model
        if debug:
            self.skymap["debug"].boolean(True)

        if self.verbose:
            print self.skymap

        self.skymap.run()

        self.skymap.save()
        self.info("Saved sky map to {0:s}".format(self.skymap["outmap"]))

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
        Fits_provided = False
        if obsXml:
            sim_obs = gl.GObservations(obsXml)
        elif self.config['file']["selectedevent"] != '':
            sim_obs = join(self.outdir,self.config['file']["selectedevent"])
            Fits_provided = True
        else:
            try:
                sim_obs = self.m_obs
            except:
                self.error("No observation given and no simulation run.")

        self.modelobs     = gl.GObservations()

        self._fill_app( self.modelobs,log=log,debug=debug, **kwargs)

        for k in kwargs.keys():
            if self.model.has_par(k):
                if k == 'enumbins' and not kwargs['incube']:
                    self.model[k] = kwargs[k] if kwargs[k] else \
                            int(np.floor(
                            np.log10(kwargs['emax'] / \
                            kwargs['emin'])) * \
                            (kwargs['ebins_per_dec'] + 1)
                            )
                else:
                    self.model[k] = kwargs[k] if not kwargs[k]==None else self.model[k]

        self.model["inobs"] = eventfile
        self.model["incube"] = join(self.outdir,self.config['file']["cube"])
        self.model["outcube"] = join(self.outdir,self.config['file']["model"])

        # Optionally open the log file
        self.model["logfile"] = self.config['file']["tag"]+"_ctmodel.log"
        if log:
            self.model.logFileOpen()

        # Optionally switch-on debugging model
        if debug:
            self.model["debug"].boolean(True)

        if self.verbose:
            print self.model

        # Run ctbin application. This will loop over all observations in
        # the container and bin the events in counts maps
        self.model.run()
        self.model.save()
        self.info("Saved Model cube to {0:s}".format(self.model["outcube"]))
        # Append result to observations
        self.modelobs.extend(self.bin.obs())

        # if self.m_obs:
            # # Make a deep copy of the observation that will be returned
            # # (the ctbin object will go out of scope one the function is
            # # left)
            # self.m_obs = model.obs().copy()

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
        Fits_provided = False
        if obsXml:
            sim_obs = gl.GObservations(obsXml)
        elif self.config['file']["selectedevent"] != '':
            sim_obs = join(self.outdir,self.config['file']["selectedevent"])
            Fits_provided = True
        else:
            try:
                sim_obs = self.m_obs
            except:
                self.error("No observation given and no simulation run.")

        self.cubeobs     = gl.GObservations()

        self._fill_app(self.cubeobs,log=log,debug=debug, **kwargs)

        for k in kwargs.keys():
            if self.bin.has_par(k):
                if k == 'enumbins':
                    self.bin[k] = kwargs[k] if kwargs[k] else \
                        int(np.floor(
                        np.log10(kwargs['emax'] / \
                        kwargs['emin'])) * \
                        (kwargs['ebins_per_dec'] + 1)
                        )
                else:
                    self.bin[k] = kwargs[k] if not kwargs[k] == None else self.bin[k]

        self.bin["inobs"] = eventfile
        self.bin["outcube"] = join(self.outdir,self.config['file']["cube"])

        # Optionally open the log file
        self.bin["logfile"] = self.config['file']["tag"]+"_ctbin.log"
        if log:
            self.bin.logFileOpen()

        # Optionally switch-on debugging model
        if debug:
            self.bin["debug"].boolean(True)

        if self.verbose:
            print self.bin

        # Run ctbin application. This will loop over all observations in
        # the container and bin the events in counts maps
        self.bin.run()

        self.bin.obs()[0].id(self.config['file']["cube"])
        self.bin.obs()[0].eventfile(self.config['file']["cube"])

        self.bin.save()
        self.info("Saved counts cube to {0:s}".format(self.bin["outcube"]))
        # Append result to observations
        self.cubeobs.extend(self.bin.obs())

        # if self.m_obs:
        #     # Make a deep copy of the observation that will be returned
        #     # (the ctbin object will go out of scope one the function is
        #     # left)
        #     self.m_obs = bin.obs().copy()


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
                self.like["inobs"] = join(self.outdir,self.config['file']["cube"])

        self.like["outmodel"] = self.config['out']+"/"+self.config['file']["tag"]+"_results.xml"

        # Optionally open the log file
        self.like["logfile"] = self.config['file']["tag"]+"_ctlike.log"
        if log:
            self.like.logFileOpen()
        # Optionally switch-on debugging model
        if debug:
            self.like["debug"].boolean(True)

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

        self.ctbutterfly = ct.ctbutterfly()
        
        self._fill_app( self.ctbutterfly,log=log,debug=debug, **kwargs)

        # Optionally open the log file
        self.ctbutterfly["logfile"] = self.config['file']["tag"]+"_ctbutterfly.log"
        if log:
            self.ctbutterfly.logFileOpen()

        # Optionally switch-on debugging model
        if debug:
            self.ctbutterfly["debug"].boolean(True)

        self.ctbutterfly["srcname"]=self.config["target"]["name"]
        self.ctbutterfly["outfile"] = self.config["target"]["name"]+"_butterfly.dat "
        self.ctbutterfly["ebinalg"] = "LOG"
        self.ctbutterfly["emin"]=self.config["energy"]["emin"]
        self.ctbutterfly["emax"]=self.config["energy"]["emax"]

        if self.verbose:
            print self.ctbutterfly

        self.ctbutterfly.run()

        self.ctbutterfly.save()
        self.info("Saved butterfly plot to {0:s}".format(self.ctbutterfly["outfile"]))
