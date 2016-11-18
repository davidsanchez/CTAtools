import ctools
import gammalib
import os,time
from os import environ, path
from ctoolsAnalysis.config import get_config
import ctoolsAnalysis.Loggin as Loggin
import ctoolsAnalysis.Common as Common
import Coordinates.CoordHandler as CH
from astropy.coordinates import ICRS, Galactic
from astropy import units as u

class CTA_ctools_sim(Loggin.base,Common.CTA_ctools_common):
    ''' Class to simulate source with the ctools framework'''
    def __init__(self,workdir='.',outdir='.'):
        ''' init function
        Parameters
        ---------
        workdir : place where fits file will be temporarily stored and where the log file will be kept
        outdir : place where the fits file 
        '''
        super(CTA_ctools_sim,self).__init__()
        self.sim = ctools.ctobssim()
        self.outfiles = []
        self.workfiles = []
        Common.CTA_ctools_common.__init__(self,workdir=workdir,outdir=outdir)

    @classmethod
    def fromConfig(cls, config):
        ''' return a CTA_ctools_sim object based on a config file
        Parameters
        ----------
        config    : config instance 
        '''
        obj = cls(workdir = config["work"],outdir = config["out"])
        obj.config = config
        obj._set_center()
        return obj
        
    def run_sim(self,prefix = "",nsim = 1, write=True, clobber = True):
        ''' set up and run the simulations
        Parameters
        ----------
        prefix  : prefix for all files produced
        nsim : number of simulation to perform
        write : save file on disk
        clobber : Erase already excisting files
        '''
        for k in self.config.keys():
            try:
                for kk in self.config[k].keys():
                    if self.sim._has_par(kk):
                        self.sim[kk] = self.config[k][kk]
            except:
                if self.sim._has_par(k):
                    self.sim[k] = self.config[k]
                    
        self.sim['inobs'] = "" #be sure that this field is empty for the simulation
        
        for i in range(1,nsim + 1):#run each simulation
            self.outfiles.append(path.join(self.outdir,
                '{0:s}_event{1:05n}.fits'.format(prefix,i)))
            self.workfiles.append(path.join(self.workdir,
                '{0:s}_event{1:05n}.fits'.format(prefix,i)))
                
            self.sim['outevents'] = self.workfiles[-1]

            if not path.isfile(self.outfiles[-1]) or clobber: #check the excistance of the file
                self.info("\nRunning {0} at {1} ...\n".format('ctobssim',
                    time.strftime("%d %b %Y %H:%M", time.gmtime())))
                self.sim.run() #run simulation
                self.success("\nDone with {0} at {1} ...\n".format('ctobssim',
                    time.strftime("%d %b %Y %H:%M", time.gmtime())))
                if write: #save file
                    self.sim.save() # save fits file to disk
                self.info("Move "+self.workfiles[-1]+" to "+self.outfiles[-1])
                os.system("mv "+self.workfiles[-1]+" "+self.outfiles[-1])
            else:
                self.warning("Found {0:s} and clobber = {1:n}".format(self.sim,clobber))


    def Print(self):
        '''
        print some usefull information
        '''
        print(self.sim.obs())
        for obscontainer in self.sim.obs():
            print(obscontainer.events())
            
