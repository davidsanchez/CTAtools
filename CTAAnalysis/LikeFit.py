import ctools as ct
import gammalib as gl
from math import log10,floor
import sys
import Loggin

class Analyser(Loggin.base):
    def __init__(self):
        super(Analyser,self).__init__()
        self.m_obs = None
        self.like  = None
        
        self.m_evtfile  = "events_selected.fits"        
        self.m_raw_evt  = "events.fits"
        self.m_cntfile  = "cntmap.fits"
        self.m_ebinalg  = "LOG"
        self.m_eunit    = "TeV"
        self.m_ra       = 83.63
        self.m_dec      = 22.01
        self.m_roi      = 2.
        self.m_tmin     = 0.
        self.m_tmax     = 0.
        self.m_emin     = 0.1#emin
        self.m_emax     = 10.#emax
        self.m_enumbins = 10#nbins
        self.m_usepnt   = True # Use pointing for map centre
        self.m_nxpix    = 200#npix
        self.m_nypix    = 200#npix
        self.m_binsz    = 0.05#binsz
        self.m_coordsys = "GAL"#coord
        self.m_proj     = "TAN"#proj
        self.m_binned   = False
        
        self.m_stat     = "POISSON"#stat
        self.m_caldb    = "dummy"
        self.m_irf      = "cta_dummy_irf"
        self.m_edisp    = False
        self.m_xml      = "$PWD/crab.xml"
        self.m_xml_out  = "$PWD/crab_results.xml"


    def set_obs(self,obs):
        self.m_obs = obs #set the GObservation container

    def set_energy_boundary(self,emin,emax):
        self.m_emin = emin
        self.m_emax = emax
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
            filter = ct.ctselect()## TODO verife ca avec le setup de la suite
        
        filter["inobs"] = self.m_raw_evt               
        filter["outobs"] = self.m_evtfile  
        filter["usepnt"].boolean(self.m_usepnt) # Use pointing for map centre
        filter["ra"]  = self.m_ra
        filter["dec"]  = self.m_dec
        filter["rad"]  = self.m_roi
        filter["tmin"] = self.m_tmin
        filter["tmax"] = self.m_tmax
        filter["emin"].real(self.m_emin)
        filter["emax"].real(self.m_emax)
        filter["expr"] = ""
        filter.logFileOpen()

        filter.run()
        if not(self.m_obs):
            filter.save()

        if self.m_obs:
            # Make a deep copy of the observation that will be returned
            # (the ctbin object will go out of scope one the function is
            # left)
            self.m_obs = filter.obs().copy()
        
    def ctbin(self,log=False,debug=False):
        # ctbin application and set parameters
        self.info("Running ctbin to create count map")
        if self.m_obs:
            bin = ct.ctbin(self.m_obs)
        else:
            bin = ct.ctbin()
            bin["inobs"] = self.m_evtfile## TODO verife ca avec le setup de la suite
        
            
            
        bin["outcube"] = self.m_cntfile
        bin["ebinalg"].string(self.m_ebinalg)
        bin["emin"].real(self.m_emin)
        bin["emax"].real(self.m_emax)
        Nbdecade = log10(self.m_emax)-log10(self.m_emin)#Compute the number of decade
        bin["enumbins"].integer(int(self.m_enumbins*Nbdecade))
        bin["usepnt"].boolean(self.m_usepnt) # Use pointing for map centre
        bin["nxpix"].integer(self.m_nxpix)
        bin["nypix"].integer(self.m_nypix)
        bin["binsz"].real(self.m_binsz)
        bin["coordsys"].string(self.m_coordsys)
        bin["proj"].string(self.m_proj)
        
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
            if self.m_binned:
                self.like["infile"] = self.m_cntfile
            else:
                self.like["infile"] = self.m_evtfile
                
            self.like["stat"].string(self.m_stat)
            self.like["caldb"].string(self.m_caldb)
            self.like["irf"].string(self.m_irf)
            self.like["srcmdl"] = self.m_xml 
        self.like["edisp"].boolean(self.m_edisp)
        self.like["outmdl"] = self.m_xml_out

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
                
if __name__ == '__main__':
    ana = Analyser()
    ana.ctselect()
    ana.ctbin()
