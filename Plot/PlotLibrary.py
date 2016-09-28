# author David Sanchez david.sanchez@lapp.in2p3.fr
# Library to plot spectrum and SED. 


# Import
from math import *
import numpy as np
from array import *
import string

class Spectrum:
  def __init__(self,Parameters,Model,Emin,Emax,Representation = "e2dnde",escale = "TeV",Npt=200):

    supportedRep = ["dnde","ednde","e2dnde"]
    if not(Representation in supportedRep):
        raise RuntimeError("Representation not supported")
    self.Representation = Representation
    supportedEscale = ["MeV","GeV","TeV"]
    if not(escale in supportedEscale):
        raise RuntimeError("Escale not supported")
    self.escale = escale

    self.Nbp = Npt
    self.Emin  = Emin
    self.Emax  = Emax
    self.Model = Model
    Model_list = ["PowerLaw","PowerLaw2","LogParabola","PLExpCutoff"]

    #Check the input model
    if not(self.Model in Model_list):
      self.usage()
      raise RuntimeError("Model in not in the list")
    #Check the number of parameters
    Parameters = self.CheckNumParemeters(Parameters)

    #input units : cm-2 s-1 (self.escale unit)-1 for diff_flux and 
    self.Norm     = Parameters[0] 
    # Index
    self.Gamma    = Parameters[2]

      # Errors
    self.ErrNorm    = Parameters[1]#input units :  cm-2 s-1 (self.escale unit)-1
    self.ErrGamma = Parameters[3]

    if self.Model=="PowerLaw"  :
        self.Ed       = Parameters[4]  #Decorrelation Energy in self.escale unit 

    print Parameters

    if self.Model=="LogParabola" :
        self.Beta  = Parameters[4] #input units :  cm-2 s-1 (self.escale unit)-1
        self.ErrBeta = Parameters[5]
        self.Ed  = Parameters[6] #Scale energy  in self.escale unit
        self.Cov1  = Parameters[7] #input units :  cm-2 s-1 (self.escale unit)-1
        self.Cov2 = Parameters[8]
        self.Cov3  = Parameters[9]

    if self.Model=="PLExpCutoff" :
        self.Ecut       = Parameters[4]  #Cutoff energy Energy in self.escale unit
        self.ErrEcut    = Parameters[5]  #Err Cutoff energy Energy in self.escale unit
        self.Ed       = Parameters[6]  #Scale energy Energy in self.escale unit


  def CheckNumParemeters(self, Params):
    if  self.Model=="PowerLaw" and not(len(Params)==5) :
        self.usage()
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 5")

    if  self.Model=="PowerLaw2" and not(len(Params)==4) :
        self.usage()
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 4")


    if  self.Model=="LogParabola"  and not(len(Params)==10) :
      if  not(len(Params)==7) :
        self.usage()
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 10")
      else :
        import logging
        logging.warn("Add 3 zeros for the covariance terms")
        Params.append(0)
        Params.append(0)
        Params.append(0)
    if  self.Model=="PLExpCutoff"  and not(len(Params)==7) :
        self.usage()
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 7")

    return Params

  def usage(self):
    print "not implemented at the moment"

  def MakeFluxAndError(self,Emin=0,Emax=10e10):

    mylog  = lambda x: np.log(x)

    #Compute the energy array using either the parameters of the class 
    # or the input parameters given by the user when calling this function
    Emin= max(Emin,self.Emin)
    Emax= min(Emax,self.Emax)
    ene = np.logspace(log10(Emin),log10(Emax),self.Nbp)

    Phi = array('f',(self.Nbp)*[0])
    dPhi = array('f',(self.Nbp)*[0])

    if self.Model == "PowerLaw":
      Phi  = self.Norm*np.power(ene/self.Ed,-self.Gamma)
      dPhi = np.sqrt( (self.ErrNorm/self.Norm)**2 + (mylog(ene/self.Ed)*self.ErrGamma)**2 )*Phi

    if self.Model == "PowerLaw2":
      D = (np.power(self.Emax,1.-self.Gamma)-np.power(self.Emin,1.-self.Gamma))
      Phi  = self.Norm*(1.-self.Gamma)*np.power(ene,-self.Gamma)/D
#      dPhi = np.sqrt( (self.ErrNorm/self.Norm)**2 + ((1./(1-self.Gamma)-mylog(ene/self.Emin))*self.ErrGamma)**2 )*Phi
      dPhi = np.sqrt( (self.ErrNorm/self.Norm)**2 + (((1./(1-self.Gamma)-mylog(ene))-(mylog(self.Emin)*np.power(self.Emin,1-self.Gamma)-mylog(self.Emax)*np.power(self.Emax,1-self.Gamma))/D)*self.ErrGamma)**2 )*Phi

    if self.Model == "PLExpCutoff":
      Phi  = self.Norm*np.power(ene/self.Ed,-self.Gamma)*np.exp(-(ene-self.Ed)/self.Ecut)
      dPhi = np.sqrt( (self.ErrNorm/self.Norm)**2 + (mylog(ene/self.Ed)*self.ErrGamma)**2 + ((ene-self.Ed)/self.Ecut**2*self.ErrEcut)**2 )*Phi

    if self.Model == 'LogParabola' :
      x = ene/self.Ed;
      Phi = self.Norm*np.power(x,-self.Gamma-self.Beta*mylog(x))

      dPhiDNorm = 1/self.Norm
      dPhiDalpha = mylog(x)
      dPhiDbeta = mylog(x)**2
      dPhi = Phi*np.sqrt((dPhiDNorm*self.ErrNorm*np.ones(len(x)))**2+(dPhiDalpha*self.ErrGamma)**2+(dPhiDbeta*self.ErrBeta)**2)
    return ene,Phi,dPhi

  def GetModel(self,Emin=0,Emax=10e10):
    ene,Phi,_ = self.MakeFluxAndError(Emin=Emin,Emax=Emax)
    ene,Phi,_ = self._HandleUnit(ene,Phi)
    return ene,Phi

  def GetButterfly(self,Emin=0,Emax=10e10):
    ene,Phi,dPhi = self.MakeFluxAndError(Emin=Emin,Emax=Emax)

    N = 2*len(ene)+1
    but = np.array(N*[1.])
    e_but = np.array(N*[1.])

    #First loop for the butterfly
    for i in xrange(len(ene)):
      e_but[i] = ene[i]
      but[i] = Phi[i]*exp(dPhi[i]/Phi[i])

    #second loop for the butterfly
    for i in xrange(len(ene)):
      e_but[len(ene)+i] = ene[len(ene)-1-i]
      but[len(ene)+i] = Phi[len(ene)-1-i]*exp(-dPhi[len(ene)-1-i]/Phi[len(ene)-1-i])

    #Close the Butterfly
    e_but[-1] = e_but[0]
    but[-1] = but[0]
 
    e_but,but,_ = self._HandleUnit(e_but,but)
    return e_but,but


  def _HandleUnit(self,ener,flux,dflux = None):
      if self.Representation == "ednde":
          flux *= ener
          if dflux!=None:
              dflux *= ener
              
      elif self.Representation == "e2dnde":
        "in ergs.cm-2.s-1"
        fac = 1.6022
        if self.escale == "MeV":
            fac = 1e-6*1.6022
        if self.escale == "GeV":
            fac = 1e-3*1.6022
        flux *= ener**2*fac
        if dflux!=None:
              dflux *= ener**2*fac
      return ener,flux,dflux


