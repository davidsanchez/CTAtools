import ctools
import gammalib
import os
import time
from os import environ
from os import path
from ctoolsAnalysis.config import get_config
import ctoolsAnalysis.Loggin as Loggin
import ctoolsAnalysis.Common as Common
import Coordinates.CoordHandler as CH
from astropy.coordinates import ICRS, Galactic
from astropy import units as u

class CTA_ctools_sim(Loggin.base,Common.CTA_ctools_common):
    def __init__(self,workdir='.',outdir='.'):
        super(CTA_ctools_sim,self).__init__()
        self.sim = ctools.ctobssim()
        Common.CTA_ctools_common.__init__(self,workdir=workdir,outdir=outdir)

    @classmethod
    def fromConfig(cls, config):
        obj = cls(workdir = config["work"],outdir = config["out"])
        obj.config = config
        obj._set_center()
        return obj
        
    def run_sim(self,prefix = "",nsim = 1, write=True, clobber = True):
        for k in self.config.keys():
            try:
                for kk in self.config[k].keys():
                    if self.sim._has_par(kk):
                        self.sim[kk] = self.config[k][kk]
            except:
                if self.sim._has_par(k):
                    self.sim[k] = self.config[k]
                    
                    
                    
        for i in range(1,nsim + 1):
            self.outfiles['events'].append(path.join(self.outdir,
                '{0:s}event{1:05n}.fits'.format(prefix,i)))
            self.sim['outevents'] = self.outfiles['events'][-1]

            if not path.isfile(self.outfiles['events'][-1]) or clobber:
                self.info("\nRunning {0} at {1} ...\n".format('ctobssim',
                    time.strftime("%d %b %Y %H:%M", time.gmtime())))
                self.sim.run()
                self.info("\nDone with {0} at {1} ...\n".format('ctobssim',
                    time.strftime("%d %b %Y %H:%M", time.gmtime())))
                if write:
                    self.sim.save() # save fits file to disk
            else:
                self.warning("Found {0:s} and clobber = {1:n}".format(self.sim['outevents'],clobber))

    def Print(self):
        print(self.sim.obs())
        for obscontainer in self.sim.obs():
            print(obscontainer.events())
            
