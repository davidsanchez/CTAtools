    # author David Sanchez david.sanchez@moi-hd.mpg.de
# Library to plot spectrum and SED. Also can correct for EBL


# Import
from math import *
import numpy as np
from array import *
import ROOT
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
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 6")

    if  self.Model=="PowerLaw2" and not(len(Params)==4) :
        self.usage()
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 5")


    if  self.Model=="LogParabola"  and not(len(Params)==10) :
      if  not(len(Params)==8) :
        self.usage()
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 11")
      else :
        import logging
        logging.warn("Add 3 zeros for the covariance terms")
        Params.append(0)
        Params.append(0)
        Params.append(0)
    if  self.Model=="PLExpCutoff"  and not(len(Params)==7) :
        self.usage()
        raise RuntimeError("Error : Not good numbers of input parameters\n Got "+str(len(Params))+" Need 8")

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
    ene,Phi,_ = self.GetValueAndError(Emin=0,Emax=10e10)
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
              
      if self.Representation == "e2dnde":
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

Norm = 1480.18  *1e-12*1e-3
DNorm =    70.4701*1e-12*1e-3
Index = 2.9485
DIndex =  0.22477 
Beta = 1.04002
DBeta =  0.312364   
Ec = 0.1412*1e3
Eminh2 = 0.11*1e3
Emaxh2 =4.715*1e3
cov1 =-0.0001163*1e-4*1e-3
cov2 = 0.2765*1e-4*1e-3
cov3 =-0.00322
SpecHESS = Spectrum([Norm,DNorm,Index,DIndex,Beta,DBeta,Ec,cov1,cov2,cov3],Model='LogParabola',Emin=Eminh2,Emax=Emaxh2,escale = "GeV")


enerHESS,ButHESS = SpecHESS.GetButterfly()

import ROOT
Xmin = 50/1e3
Xmax = 9.9e6/1e3
Ymin = .05e-12
Ymax = .06e-8
lsiz = 0.04
c1=ROOT.TCanvas("c1");
c1.SetLogx()
c1.SetLogy()
c1.SetTickx(0)
c1.SetTicky(0)
c1.SetTopMargin(0.12);
gh = ROOT.TH2F("gh1","",10000,Xmin,Xmax,100,Ymin,Ymax);
gh.GetXaxis().SetTitleSize(lsiz)
gh.GetXaxis().SetLabelSize(lsiz)
gh.GetYaxis().SetTitleSize(lsiz)
gh.GetXaxis().SetLabelSize(lsiz)

gh.SetStats(000)
gh.SetXTitle("E [GeV]")
gh.SetYTitle("E^{2}dN/dE [ erg cm^{-2} s^{-1} ] ")
gh.Draw()
gh.SetLabelSize(0.04,"xyz");
gh.SetTitleSize(0.04,"xyz");
gh.SetTitleOffset(1.2,"x");
gh.SetTitleOffset(1.4,"y");
gh.GetXaxis().CenterTitle()
gh.GetYaxis().CenterTitle()

tgrButHESSII = ROOT.TGraph(len(enerHESS),array('f',enerHESS),array('f',ButHESS))

tgrButHESSII.Draw("FL")
