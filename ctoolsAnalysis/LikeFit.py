# author David Sanchez david.sanchez@lapp.in2p3.fr

import ctools as ct
import gammalib as gl
from math import log10,floor
import sys
import ctoolsAnalysis.Loggin as Loggin
from ctoolsAnalysis.config import get_config
import ctoolsAnalysis.Common as Common


class CTA_ctools_analyser(Loggin.base,Common.CTA_ctools_common):
    def __init__(self,workdir='.',outdir='.'):
        super(CTA_ctools_analyser,self).__init__()
        self.m_obs = None
        self.like  = None
        self.config  = None
        Common.CTA_ctools_common.__init__(self,workdir=workdir,outdir=outdir)
        
    @classmethod
    def fromConfig(cls, config):
        obj = cls()
        obj.config = config
        return obj

    def set_obs(self,obs):
        self.m_obs = obs #set the GObservation container

    def set_energy_boundary(self,emin,emax):
        self.SetEnergyRange(emin,emax)
        ebounds = gl.GEbounds(gl.GEnergy(emin, self.m_eunit), \
                                gl.GEnergy(emax, self.m_eunit))

        if self.m_obs:
            for obs in self.m_obs:
                obs.events().ebounds(ebounds)
        
    def ctselect(self):
        # ctselect application and set parameters
        self.info("Running ctselect to cut on events")
        if self.m_obs:
            filter = ct.ctselect(self.m_obs)
        else:
            filter = ct.ctselect()## 
            
            for k in self.config.keys():
                try:
                    for kk in self.config[k].keys():
                        if filter._has_par(kk):
                            filter[kk] = self.config[k][kk]
                except:
                    if filter._has_par(k):
                        filter[k] = self.config[k]
            
            
            filter["inobs"] = self.config['file']["rawevent"]
            filter["outobs"] = self.config['file']["selectedevent"]               
        filter.logFileOpen()

        filter.run()
        if not(self.m_obs):
            filter.save()

        if self.m_obs:
            # Make a deep copy of the observation that will be returned
            # (the ctbin object will go out of scope one the function is
            # left)
            self.m_obs = filter.obs().copy()
        
    def ctmodel(self,log=False,debug=False):
        # ctmodel application and set parameters
        self.info("Running ctmodel to create model map")
        if self.m_obs:
            model = ct.ctmodel(self.m_obs)
        else:
            model = ct.ctmodel()
            
            for k in self.config.keys():
                try:
                    for kk in self.config[k].keys():
                        if model._has_par(kk):
                            model[kk] = self.config[k][kk]
                except:
                    if model._has_par(k):
                        model[k] = self.config[k]
            
            model["inobs"] = self.config['file']["selectedevent"]               
            model["incube"] = self.config['file']["cube"]               
            model["outcube"] = self.config['file']["model"]               

        # Optionally open the log file
        if log:
            model.logFileOpen()

        # Optionally switch-on debugging model
        if debug:
            model["debug"].boolean(True)

        # Run ctbin application. This will loop over all observations in
        # the container and bin the events in counts maps
        model.run()
        model.save()
        if self.m_obs:
            # Make a deep copy of the observation that will be returned
            # (the ctbin object will go out of scope one the function is
            # left)
            self.m_obs = model.obs().copy()
    
    def ctbin(self,log=False,debug=False):
        # ctbin application and set parameters
        self.info("Running ctbin to create count map")
        if self.m_obs:
            bin = ct.ctbin(self.m_obs)
        else:
            bin = ct.ctbin()
            
            for k in self.config.keys():
                try:
                    for kk in self.config[k].keys():
                        if bin._has_par(kk):
                            bin[kk] = self.config[k][kk]
                except:
                    if bin._has_par(k):
                        bin[k] = self.config[k]
            
            bin["inobs"] = self.config['file']["selectedevent"]               
            bin["outcube"] = self.config['file']["cube"]               

        # Optionally open the log file
        if log:
            bin.logFileOpen()

        # Optionally switch-on debugging model
        if debug:
            bin["debug"].boolean(True)

        # Run ctbin application. This will loop over all observations in
        # the container and bin the events in counts maps
        bin.run()
        bin.save()
        if self.m_obs:
            # Make a deep copy of the observation that will be returned
            # (the ctbin object will go out of scope one the function is
            # left)
            self.m_obs = bin.obs().copy()
    
    
    def create_fit(self,log=False,debug=False):
        # create ctlike instance with given parameters
        self.info("Fitting Data using ctlike")
        if self.m_obs:
            self.like = ct.ctlike(self.m_obs)
        else:
            self.like = ct.ctlike()
            if self.config["analysis"]["likelihood"]:
                self.like["inobs"] = self.config['file']["cube"]   
            else:
                self.like["inobs"] = self.config['file']["selectedevent"]
                
            for k in self.config.keys():
                try:
                    for kk in self.config[k].keys():
                        if self.like._has_par(kk):
                            self.like[kk] = self.config[k][kk]
                except:
                    if self.like._has_par(k):
                        self.like[k] = self.config[k]
                        
        self.like["outmodel"] = self.config['out']+"/"+self.config['target']["name"]+"_results.xml"
        
        # Optionally open the log file
        if log:
            self.like.logFileOpen()
        # Optionally switch-on debugging model
        if debug:
            self.like["debug"].boolean(True)
            
    def fit(self,log=False,debug=False):
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
        for m in self.like.obs().models():
            if srcname == m.name() or srcname=="":
                print "Model : "+m.name()
                print m
                

