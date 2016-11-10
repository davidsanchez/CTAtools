"""
Class to read the Fermi catalogs
 author David Sanchez  david.sanchez@lapp.in2p3.fr
"""
import pyfits,string,numpy
from Plot import PlotLibrary
from environ import VERSION_3FGL,VERSION_2FGL,VERSION_1FHL,VERSION_2FHL,FERMI_CATALOG_DIR
import Loggin
from math import *

astropy = True
try :
    import Coordinates.CoordHandler as CH
    from astropy.coordinates import ICRS, Galactic, FK4, FK5 
except :
    astropy = False #for coordinate management
    print "\033[33m WARNING : you don't have astropy installed. Creation of a catalog with name will not work\033[0m"
    pass

class FermiCatalogReader(Loggin.base):
  ''' Class to read the Fermi Catalogs '''
  def __init__(self,name=None,folder=None,Representation = "e2dnde",escale = "TeV"):
    ''' init function
    Parameters
    ---------
    name    : catalog name of the source
    folder  : where the Fermi catalog are. If None, the FERMI_CATALOG_DIR environnement variable is used
    Representation : for the plot (dnde, ednde, e2dnde)
    escale  : energy scale in MeV, GeV or TeV
    '''
    super(FermiCatalogReader,self).__init__()
    Loggin.base.__init__(self)

    if folder == None :
        self.folder = FERMI_CATALOG_DIR
    else:
        self.folder = folder
    self.Representation = Representation
    self.escale = escale

    #Check the input
    supportedRep = ["dnde","ednde","e2dnde"]
    if not(Representation in supportedRep):
        raise RuntimeError("Representation not supported")
    supportedEscale = ["MeV","GeV","TeV"]
    if not(escale in supportedEscale):
        raise RuntimeError("Escale not supported")

    #all the information are in a python dictionnary
    self.CatalogData = {'3FGL':{},'2FGL':{},'1FHL':{},'2FHL':{}}
    self.CatalogData['3FGL']['fits'] = folder+"/gll_psc_v"+VERSION_3FGL+".fit"
    self.CatalogData['2FGL']['fits'] = folder+"/gll_psc_v"+VERSION_2FGL+".fit"
    self.CatalogData['1FHL']['fits'] = folder+"/gll_psch_v"+VERSION_1FHL+".fit"
    self.CatalogData['2FHL']['fits'] = folder+"/gll_psch_v"+VERSION_2FHL+".fit"

    self.CatalogData['3FGL']['data'] = pyfits.open(self.CatalogData['3FGL']['fits'])[1].data
    
    self.CatalogData['2FGL']['data'] = pyfits.open(self.CatalogData['2FGL']['fits'])[1].data
    self.CatalogData['1FHL']['data'] = pyfits.open(self.CatalogData['1FHL']['fits'])[1].data
    self.CatalogData['2FHL']['data'] = pyfits.open(self.CatalogData['2FHL']['fits'])[1].data

    #read data points
    self.CatalogData['3FGL']['Band'] = ['Flux100_300','Flux300_1000','Flux1000_3000','Flux3000_10000','Flux10000_100000']
    self.CatalogData['2FGL']['Band'] = ['Flux100_300','Flux300_1000','Flux1000_3000','Flux3000_10000','Flux10000_100000']
    self.CatalogData['1FHL']['Band'] = ['Flux10_30GeV','Flux30_100GeV','Flux100_500GeV']
    self.CatalogData['2FHL']['Band'] = ['Flux50_171GeV','Flux171_585GeV','Flux585_2000GeV']

    #upper bound of the energy bins of Fermi catalogs
    self.CatalogData['3FGL']['eMax'] = self._HandleEnergyUnit(numpy.array([300,1000,3000,10000,100000]))
    self.CatalogData['2FGL']['eMax'] = self._HandleEnergyUnit(numpy.array([300,1000,3000,10000,100000]))
    self.CatalogData['1FHL']['eMax'] = self._HandleEnergyUnit(numpy.array([30e3,100e3,500e3]))
    self.CatalogData['2FHL']['eMax'] = self._HandleEnergyUnit(numpy.array([171e3,585e3,2000e3]))


    #lower bound of the energy bins of Fermi catalogs
    self.CatalogData['3FGL']['eMin'] = self._HandleEnergyUnit(numpy.array([100,300,1000,3000,10000]))
    self.CatalogData['2FGL']['eMin'] = self._HandleEnergyUnit(numpy.array([100,300,1000,3000,10000]))
    self.CatalogData['1FHL']['eMin'] = self._HandleEnergyUnit(numpy.array([10e3,30e3,100e3]))
    self.CatalogData['2FHL']['eMin'] = self._HandleEnergyUnit(numpy.array([50e3,171e3,585e3]))

    self.name = name
    self.Spec = None

    self.info("creating catalogues Reader with\n\t "+self.CatalogData['3FGL']['fits']+"\n\t "+self.CatalogData['2FGL']['fits']+"\n\t "+self.CatalogData['1FHL']['fits']+"\n\t "+self.CatalogData['2FHL']['fits'])

    # get table indices corresponding to the source entry
    if name != None:
        self.GetIndices()
    
    
  @classmethod
  def fromName(self,name, frame = FK5,folder="",Representation = "e2dnde",escale = "TeV"):
    ''' return a FermiCatalogReader object based on a name of a source
    Parameters
    ----------
    name    : catalog name (see astropy manual for the valid names)
    frame   : Astropy coordinate frame ICRS, Galactic, FK4, FK5 , see astropy for more information
    folder  : where the Fermi catalog are
    Representation : for the plot (dnde, ednde, e2dnde)
    energy scale : MeV, GeV or TeV
    
    '''
    if astropy:
        c = CH.CoordinatesHandler.fromName(name,frame)
        catalog = FermiCatalogReader(None,folder)
        for k in ['3FGL','2FGL','2FHL','1FHL']:
            catalog.findfromCoordinate(k,c.skycoord.ra.deg,c.skycoord.dec.deg)
            if catalog.CatalogData[k]['found']:
                break
            
        return FermiCatalogReader(catalog.CatalogData[k]['name'],folder=folder,Representation = Representation, escale = escale)

    else :
        self.warning("No astropy module found, returning None")
        return None

  def GetIndices(self):
    ''' look for the table indices where the source data are in the catalog'''
    for k in self.CatalogData.keys():
      name=self.CatalogData[k]['data'].field('Source_Name')
      print 'try ',k,' catalog'
      for indice in xrange(name.size):
        if name[indice] == self.name :
          self.CatalogData[k]['indice'] = indice
          self.CatalogData[k]['name']   = name[indice]
          self.success(k+" source found")
          self.CatalogData[k]['found'] = True

          ra,dec = self.GetPosition(k)
          self.info("Catalog Position "+str(ra)+","+str(dec))
          for j in self.CatalogData.keys():
            if j!=k:
              self.findfromCoordinate(j,ra,dec)

          self.GetModels()
          self.GetClass()
          return
    self.error("cannot find the index of the source named "+self.name+". Check the name")

  def GetPosition(self,k):
    '''retrive the position of the source in J2000 '''
    ra  = self.CatalogData[k]['data'].field('RAJ2000')
    dec = self.CatalogData[k]['data'].field('DEJ2000')
    return ra[self.CatalogData[k]['indice']],dec[self.CatalogData[k]['indice']]

  def findfromCoordinate(self, k,ra0,dec0):
    '''
    find a source based on coordinates
    Parameters
    ----------
    k   : name of the catalog 2FGL, 3FGL, etc...
    ra0 : coordinate of the source in J2000. The column read is RAJ2000
    dec0 : coordinate of the source in J2000. The column read is DEJ2000
    '''
    ra  = self.CatalogData[k]['data'].field('RAJ2000')
    dec = self.CatalogData[k]['data'].field('DEJ2000')

    r = calcAngSepDeg(ra,dec,ra0,dec0)
    res = r.argmin()
    if min(r) > 0.5:
      self.warning("No source closer than 0.5 degrees in catalog ",k)
      self.CatalogData[k]['found'] = False

      return
    self.success("found a close source in the catalog "+self.CatalogData[k]['fits']+" at r="+str(r[res])+" named "+self.CatalogData[k]['data'].field('Source_Name')[res])
    self.CatalogData[k]['indice'] = res
    self.CatalogData[k]['name'] = self.CatalogData[k]['data'].field('Source_Name')[res]
    self.CatalogData[k]['found'] = True


  def GetModels(self):
    '''retrive the spectral model in the catalog and fill the dictionnary'''
    for k in self.CatalogData.keys():
      if self.CatalogData[k]['found'] == False:
        continue
      try:
        Spec = self.CatalogData[k]['data'].field('SpectrumType')
        self.CatalogData[k]['model'] = Spec[self.CatalogData[k]['indice']]
      except:
        self.CatalogData[k]['model'] = "PowerLaw"

      self.info(k+" model type: "+self.CatalogData[k]['model'])

  def GetClass(self):
    '''
    retrive the object class from the CLASS1 field and fill the dictionnary
    '''
    for k in self.CatalogData.keys():
      if self.CatalogData[k]['found'] == False:
        continue
      try : 
         Class = self.CatalogData[k]['data'].field('CLASS1')
      except : 
         Class = self.CatalogData[k]['data'].field('CLASS') #for the 2FHL
      self.CatalogData[k]['class'] = Class[self.CatalogData[k]['indice']]
      self.info(k+" Object class: "+self.CatalogData[k]['class'])

  def GetDataPoints(self,key):
    ''' read data points and fill the dictionnary
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc...
    '''
    flux  = []
    dflux = []
    try:
      if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
        return 0,0,0,0
      self.info("Results for "+key)
      for i in xrange(len(self.CatalogData[key]['Band'])):
          flux.append(self.CatalogData[key]['data'].field(self.CatalogData[key]['Band'][i])[self.CatalogData[key]['indice']])
          print self.CatalogData[key]['Band'][i]," ",self.CatalogData[key]['data'].field(self.CatalogData[key]['Band'][i])[self.CatalogData[key]['indice']]," +/- ",self.CatalogData[key]['data'].field("Unc_"+self.CatalogData[key]['Band'][i])[self.CatalogData[key]['indice']]

          if key == '3FGL' or key == '1FHL' or key == '2FHL':
            tmp = self.CatalogData[key]['data'].field("Unc_"+self.CatalogData[key]['Band'][i])[self.CatalogData[key]['indice']]
            dflux.append(abs(-tmp[0]+tmp[1])/2.)
          else:
            dflux.append(self.CatalogData[key]['data'].field("Unc_"+self.CatalogData[key]['Band'][i])[self.CatalogData[key]['indice']])

      return self.CatalogData[key]['eMin'],self.CatalogData[key]['eMax'],numpy.array(flux),numpy.array(dflux)
    except :
      self.error("No such catalog: "+key)


#########################
  def MakeSpectrum(self,key,Emin=100,Emax=3e5):
    '''
    Depending on the found spectral model, this function will call another function that
    read the catalog and return the data in a format readable by the plot library.
    A spectrum object  (from the plotlibrary) is then created and stored in the python dictionnary. It
    is possible to create spectrum for each catalog, they will be stored in a different
    entry.
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc...
    Emin  : minimal energy for the plot : unit is defined by the scale (see _init__ function)
    Emax  : maximal energy for the plot : unit is defined by the scale (see _init__ function)
    '''
    if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
    try:
      model = self.CatalogData[key]['model']
      if key == "2FHL" :
        model = "PowerLaw2"
        data = self.ReadPL2(key)
      if model=="PowerLaw":
        data = self.ReadPL(key)
      if model=="LogParabola":
        data = self.ReadLP(key)
    except :
      self.error("No such catalog: "+key)
    
    try :
        self.CatalogData[key]['spectrum'] = PlotLibrary.Spectrum(data,Model=model,Emin=Emin,
                                Emax=Emax,Representation=self.Representation,escale=self.escale,
                                Npt=1000)
    except :
        self.error("cannot create spectrum for model "+model+" and catalog "+key)
    self.success("Reading spectral informations from "+key+" for model "+model)


  def ReadPL(self,key):
    '''
    read the information of the catalog in the case of a Power Law model
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc...
    '''
    indice = self.CatalogData[key]['indice']
    index  = self.CatalogData[key]['data'].field('Spectral_Index')[indice]
    eindex = self.CatalogData[key]['data'].field('Unc_Spectral_Index')[indice]

    flux   = self.CatalogData[key]['data'].field('Flux_Density')[indice]
    eflux  = self.CatalogData[key]['data'].field('Unc_Flux_Density')[indice]
    pivot  = self.CatalogData[key]['data'].field('Pivot_Energy')[indice]
    
    if key == '1FHL' :
      pivot *= 1e3
      flux  *= 1e-3
      eflux *= 1e-3

    pivot = self._HandleEnergyUnit(pivot)
    flux = self._HandleFluxUnit(flux)
    eflux = self._HandleFluxUnit(eflux)
    return [flux,eflux,index,eindex,pivot]


  def ReadPL2(self,key):
    '''
    read the information of the catalog in the case of a Power Law 2 model
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc...
    '''
    if key == '2FHL':
        indice = self.CatalogData[key]['indice']
        index  = self.CatalogData[key]['data'].field('Spectral_Index')[indice]
        eindex = self.CatalogData[key]['data'].field('Unc_Spectral_Index')[indice]
        flux   = self.CatalogData[key]['data'].field('Flux50')[indice]
        eflux  = self.CatalogData[key]['data'].field('Unc_Flux50')[indice]
    else:
        self.error("No PL2 infor for catalog: "+key)
    
    return [flux,eflux,index,eindex]


  def ReadLP(self,key):
    '''
    read the information of the catalog in the case of a LogParabola model
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc...
    '''
    indice = self.CatalogData[key]['indice']
    flux   = self.CatalogData[key]['data'].field('Flux_Density')[indice]
    pivot  = self.CatalogData[key]['data'].field('Pivot_Energy')[indice]
    index  = self.CatalogData[key]['data'].field('Spectral_Index')[indice]
    eflux  = self.CatalogData[key]['data'].field('Unc_Flux_Density')[indice]
    eindex = self.CatalogData[key]['data'].field('Unc_Spectral_Index')[indice]
    beta = self.CatalogData[key]['data'].field('beta')[indice]
    ebeta = self.CatalogData[key]['data'].field('Unc_beta')[indice]
    if key == '1FHL':
      pivot *= 1e3
      flux  *= 1e-3
      eflux *= 1e-3

    pivot = self._HandleEnergyUnit(pivot)
    flux = self._HandleFluxUnit(flux)
    eflux = self._HandleFluxUnit(eflux)
    return [flux,eflux,index,eindex,beta,ebeta,pivot]

  def Plot(self,key):
    '''
    Compute model and butterfly for the catalog key
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc...
    '''
    if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
    if not('spectrum' in self.CatalogData[key]):
        self.error("No spectrum computed for "+key)

    ## Draw part
    enerbut,but = self.CatalogData[key]['spectrum'].GetButterfly()
    enerphi,phi = self.CatalogData[key]['spectrum'].GetModel()

    #enerbut = self._HandleUnit(enerbut)
    #enerphi = self._HandleUnit(enerphi)

    return enerbut,but,enerphi,phi


  def Association(self,key,asso = 'ASSOC1'):
    '''
    Look for the association of the sources based on a field given by the used; defaul is ASSOC1
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc...
    asso  : Name of the association column in the fits file
    '''
    try:
      if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
      
      return self.CatalogData[key]['data'].field(asso)[self.CatalogData[key]['indice']]

    except :
      self.error("No association "+asso+" in catalog: "+key)


  def GetVarIndex(self,key):
    '''
    return the variability index of the source
    Parameters
    ----------
    key   : name of the catalog 2FGL, 3FGL, etc... 
    '''
    try : 
      if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
      try :
        VarI=self.CatalogData[key]['data'].field('Variability_Index')
      except:
        return -1
      return VarI[self.CatalogData[key]['indice']]

    except :
      self.error("No such catalog: "+key)


  def _HandleEnergyUnit(self,ener):
      fac = 1
      if self.escale == "TeV":
          fac = 1e-6
      if self.escale == "GeV":
          fac = 1e-3
      return ener*fac

  def _HandleFluxUnit(self,flux):
      fac = 1
      if self.escale == "TeV":
          fac = 1e6
      if self.escale == "GeV":
          fac = 1e3
      return fac*flux



#Side functions
def calcAngSepDeg(ra0, dec0, ra1, dec1):
    '''Return the angular separation between two objects. Use the
    special case of the Vincenty formula that is accurate for all
    distances'''
    C = numpy.pi / 180
    d0 = C * dec0
    d1 = C * dec1
    r12 = C * (ra0 - ra1)
    cd0 = numpy.cos(d0)
    sd0 = numpy.sin(d0)
    cd1 = numpy.cos(d1)
    sd1 = numpy.sin(d1)
    cr12 = numpy.cos(r12)
    sr12 = numpy.sin(r12)
    num = numpy.sqrt((cd0 * sr12) ** 2 + (cd1 * sd0 - sd1 * cd0 * cr12) ** 2)
    den = sd0 * sd1 + cd0 * cd1 * cr12
    return numpy.arctan2(num, den) / C



