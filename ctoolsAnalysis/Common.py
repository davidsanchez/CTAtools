import ctools
import gammalib
import os
import time
from os import environ
from os import path
from ctoolsAnalysis.config import get_config
import ctoolsAnalysis.Loggin as Loggin
import Coordinates.CoordHandler as CH
from astropy.coordinates import ICRS, Galactic
from astropy import units as u

class CTA_ctools_common():
    def __init__(self,workdir='.',outdir='.'):
        self.config = None
        
        self.outdir = outdir
        if not os.path.exists(outdir):
            os.mkdir(outdir)
            
        self.workdir = workdir
        if not os.path.exists(workdir):
            os.mkdir(workdir)

        os.chdir(workdir)

    @classmethod
    def fromConfig(cls, config):
        obj = cls(workdir = config["work"],outdir = config["out"])
        obj.config = config
        obj._set_center()
        return obj
        
    def SetEnergyRange(self,E1,E2):
        self.config["energy"]["emin"] = E1
        self.config["energy"]["emax"] = E2

    def SetTimeRange(self,T1,T2):
        self.config['time']["tmin"] = T1
        self.config['time']["tmax"] = T2


    def SetSrcName(self,name):
        self.config['target']["name"] = name

    def SetRADEC(self,RA,DEC):
        c_icrs = CH.CoordinatesHandler(RA * u.degree, DEC * u.degree,ICRS)
        self.config["target"]['ra'] = c_icrs.X.degree
        self.config["target"]['dec'] =c_icrs.Y.degree
        self.config["target"]['l'] =c_icrs.skycoord.galactic.l.value
        self.config["target"]['b'] =c_icrs.skycoord.galactic.b.value
        self._set_center()

    def SetLB(self,L,B):
        c_gal = CH.CoordinatesHandler(L * u.degree, B * u.degree,Galactic)
        self.config["target"]['ra'] = c_gal.skycoord.icrs.ra.value
        self.config["target"]['dec'] = c_gal.skycoord.icrs.dec.value
        self.config["target"]['l'] =c_gal.X.degree
        self.config["target"]['b'] =c_gal.Y.degree
        self._set_center()
        
    def _set_center(self):
        if self.config['space']['coordsys'] == "CEL":
            self.config['space']['xref'] = self.config["target"]['ra']
        elif self.config['space']['coordsys'] == "GAL":
            self.config['space']['xref'] = self.config["target"]['l']

        if self.config['space']['coordsys'] == "CEL":
            self.config['space']['yref'] = self.config["target"]['dec']
        elif self.config['space']['coordsys'] == "GAL":
            self.config['space']['yref'] = self.config["target"]['b']

    def SetIRFs(self,caldb,irf):
        self.config['irfs']["caldb"] = caldb
        self.config['irfs']["irf"] = irf

    def SetOutFile(self,out):
        self.config['out'] = out
        
    def SetModel(self,xmlfile):
        self.config['file']['inmodel'] = xmlfile

            
if __name__ == '__main__':
    Sim = CTAsim()
    Sim.SetEnergyRange(0.1,100)
    Sim.SetTimeRange(0.0,1800.0)
    Sim.SetCoordinate(83.63,22.01,5.0)
    #Sim.SetIRFs("prod2","South_0.5h")
    #Sim.SetOutFile("events.fits")
    #Sim.SetModel("crab.xml")
    #Sim.Exec()
    #Sim.Print()
    #Sim.Fit()
