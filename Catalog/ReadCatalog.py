import pyfits,string,numpy
import Plot import PlotLibrary
import Loggin
from math import *

class CatalogReader(Loggin.base):
  def __init__(self,name,folder=""):
    super(CatalogReader,self).__init__()
    Loggin.base.__init__(self)

    self.SEDmode = True

    self.CatalogData = {'3FGL':{},'2FGL':{},'1FHL':{},'2FHL':{}}
    self.CatalogData['3FGL']['fits'] = folder+"/gll_psc_v14.fit"
    self.CatalogData['2FGL']['fits'] = folder+"/gll_psc_v08.fit"
    self.CatalogData['1FHL']['fits'] = folder+"/gll_psch_v07.fit"
    self.CatalogData['2FHL']['fits'] = folder+"/gll_psch_v08.fit"

    self.folder = folder
    self.CatalogData['3FGL']['data'] = pyfits.open(self.CatalogData['3FGL']['fits'])[1].data
    
    self.CatalogData['2FGL']['data'] = pyfits.open(self.CatalogData['2FGL']['fits'])[1].data
    self.CatalogData['1FHL']['data'] = pyfits.open(self.CatalogData['1FHL']['fits'])[1].data
    self.CatalogData['2FHL']['data'] = pyfits.open(self.CatalogData['2FHL']['fits'])[1].data

    self.CatalogData['3FGL']['Band'] = ['Flux100_300','Flux300_1000','Flux1000_3000','Flux3000_10000','Flux10000_100000']
    self.CatalogData['2FGL']['Band'] = ['Flux100_300','Flux300_1000','Flux1000_3000','Flux3000_10000','Flux10000_100000']
    self.CatalogData['1FHL']['Band'] = ['Flux10_30GeV','Flux30_100GeV','Flux100_500GeV']
    self.CatalogData['2FHL']['Band'] = ['Flux50_171GeV','Flux171_585GeV','Flux585_2000GeV']



    self.CatalogData['3FGL']['eMax'] = numpy.array([300,1000,3000,10000,100000])
    self.CatalogData['2FGL']['eMax'] = numpy.array([300,1000,3000,10000,100000])
    self.CatalogData['1FHL']['eMax'] = numpy.array([30e3,100e3,500e3])
    self.CatalogData['2FHL']['eMax'] = numpy.array([171e3,585e3,2000e3])


    self.CatalogData['3FGL']['eMin'] = numpy.array([100,300,1000,3000,10000])
    self.CatalogData['2FGL']['eMin'] = numpy.array([100,300,1000,3000,10000])
    self.CatalogData['1FHL']['eMin'] = numpy.array([10e3,30e3,100e3])
    self.CatalogData['2FHL']['eMin'] = numpy.array([50e3,171e3,585e3])


#    self.Info2FGL = open(folder+"/2LACselection_all","r").readlines()
#    self.Info1FHL = pyfits.open(folder+"/FHL_AGN_Table_v3.fit")[1].data
#    self.ShawData = open(folder+"/Shaw_BLLac_z.txt","r").readlines()

    self.name = name
    self.Spec = None

    self.info("creating catalogues Reader with\n\t "+self.CatalogData['3FGL']['fits']+"\n\t "+self.CatalogData['2FGL']['fits']+"\n\t "+self.CatalogData['1FHL']['fits']+"\n\t "+self.CatalogData['2FHL']['fits'])
#    self.info("Aux Info from "+folder+"/2LACselection_all, "+folder+"/FHL_AGN_Table_v3.fit and "+folder+"/Shaw_BLLac_z.txt")

    self.GetIndices()

  def SetSEDmode(self,b):
    self.SEDmode = b

  def GetIndices(self):

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
    ra  = self.CatalogData[k]['data'].field('RAJ2000')
    dec = self.CatalogData[k]['data'].field('DEJ2000')
    return ra[self.CatalogData[k]['indice']],dec[self.CatalogData[k]['indice']]

  def findfromCoordinate(self, k,ra0,dec0):
    ra  = self.CatalogData[k]['data'].field('RAJ2000')
    dec = self.CatalogData[k]['data'].field('DEJ2000')
    r = calcAngSepDeg(ra,dec,ra0,dec0)
    res = r.argmin()
    if min(r) > 0.5:
      self.warning("No source closer than 0.5 degrees")
      self.CatalogData[k]['found'] = False

      return
    self.success("found a close source in the catalog "+self.CatalogData[k]['fits']+" at r="+str(r[res])+" named "+self.CatalogData[k]['data'].field('Source_Name')[res])
    self.CatalogData[k]['indice'] = res
    self.CatalogData[k]['name'] = self.CatalogData[k]['data'].field('Source_Name')[res]
    self.CatalogData[k]['found'] = True


  def GetModels(self):
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
    flux  = []
    dflux = []
    if 1:
#    try:
      if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
#        return 0,0,0,0
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
#    except :
#      self.error("No such catalog: "+key)


#########################
  def MakeSpectrum(self,key,Emin=100,Emax=3e5):
    if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
    try:
      model = self.CatalogData[key]['model']
      if key == "2FHL" :
        model = "PowerLaw2"
        data = self.ReadPL2(key)
      if model=="PowerLaw":
        data = self.ReadPL(key)
#        print data
      if model=="LogParabola":
        data = self.ReadLP(key)

      self.CatalogData[key]['spectrum'] = PlotLibrary.Spectrum(data,Model=model,Emin=Emin,Emax=Emax,Npt=1000)

      self.success("Reading spectral informations from "+key)

    except :
      self.error("No such catalog: "+key)
  def ReadPL(self,key):
    indice = self.CatalogData[key]['indice']
    index  = self.CatalogData[key]['data'].field('Spectral_Index')[indice]
    eindex = self.CatalogData[key]['data'].field('Unc_Spectral_Index')[indice]

#    try :
    flux   = self.CatalogData[key]['data'].field('Flux_Density')[indice]
    eflux  = self.CatalogData[key]['data'].field('Unc_Flux_Density')[indice]
    pivot  = self.CatalogData[key]['data'].field('Pivot_Energy')[indice]
#    except :
#        flux   = self.CatalogData[key]['data'].field('Flux50')[indice]
##        eflux  = self.CatalogData[key]['data'].field('Unc_Flux50')[indice]
#        eindex = 0
#        eflux  = 0 #TODO
#        pivot  = 5e5
#        flux *= (-index+1)*numpy.power(5e4,-index)/(numpy.power(5e5,-index+1)-numpy.power(5e4,-index+1))
#        eflux *= 1./elf.CatalogData[key]['data'].field('Flux50')[indice]*flux

    if key == '1FHL' :
      pivot *= 1e3
      flux  *= 1e-3
      eflux *= 1e-3
    return [self.name,flux,eflux,index,eindex,pivot]


  def ReadPL2(self,key):
    indice = self.CatalogData[key]['indice']
    index  = self.CatalogData[key]['data'].field('Spectral_Index')[indice]
    eindex = self.CatalogData[key]['data'].field('Unc_Spectral_Index')[indice]
    flux   = self.CatalogData[key]['data'].field('Flux50')[indice]
    eflux  = self.CatalogData[key]['data'].field('Unc_Flux50')[indice]
    return [self.name,flux,eflux,index,eindex]


  def ReadLP(self,key):
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
    return [self.name,flux,eflux,index,eindex,beta,ebeta,pivot]

  def Plot(self,key):


    if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
    if not('spectrum' in self.CatalogData[key]):
        self.error("No spectrum computed for "+key)
#    try:
    if 1:
      ## Draw part
      ener,but = self.CatalogData[key]['spectrum'].GetButterfly(SED=self.SEDmode)
      tgrbut = PlotLibrary.MakeTGraph(ener,but)
      ener,phi = self.CatalogData[key]['spectrum'].GetModel(SED=self.SEDmode)
      tgrphi = PlotLibrary.MakeTGraph(ener,phi)
      self.success("Building TGRAPH from "+key)

      return tgrphi,tgrbut
#    except :
#      self.error("No such catalog: "+key)


  def Association(self,key,asso = 'ASSOC1'):
    try:
      if self.CatalogData[key]['found'] == False: 
        self.error("This source does not belong to "+key)
      
      return self.CatalogData[key]['data'].field(asso)[self.CatalogData[key]['indice']]

    except :
      self.error("No association "+asso+" in catalog: "+key)


  def GetVarIndex(self,key):
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



