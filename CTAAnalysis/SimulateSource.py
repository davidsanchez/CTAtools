import ctools


class CTAsim():
    def __init__(self,*argv):
        self.sim = ctools.ctobssim()

        
    def SetEnergyRange(self,E1,E2):
        self.sim["emin"] = E1
        self.sim["emax"] = E2

    def SetTimeRange(self,T1,T2):
        self.sim["tmin"] = T1
        self.sim["tmax"] = T2

    def SetCoordinate(self,RA,DEC,rad):
        self.sim["ra"] = RA
        self.sim["dec"] = DEC
        self.sim["rad"] = rad

    def SetIRFs(self,caldb,irf):
        self.sim["caldb"] = caldb
        self.sim["irf"] = irf

    def SetOutFile(self,out):
        self.sim["outevents"] = out
        
    def SetModel(self,xmlfile):
        self.sim["inmodel"] = xmlfile

    def Exec(self,write=True):
        if write:
            self.sim.execute()
        else:
            self.sim.run()

    def Print(self):
        print(self.sim.obs())
        for obscontainer in self.sim.obs():
            print(obscontainer.events())
            
    def Fit(self):
        self.like = ctools.ctlike(self.sim.obs())
        self.like.run()
        print(self.like.opt())
        
if __name__ == '__main__':
    Sim = CTAsim()
    Sim.SetEnergyRange(0.1,100)
    Sim.SetTimeRange(0.0,1800.0)
    Sim.SetCoordinate(83.63,22.01,5.0)
    Sim.SetIRFs("prod2","South_0.5h")
    Sim.SetOutFile("events.fits")
    Sim.SetModel("crab.xml")
    Sim.Exec()
    Sim.Print()
    Sim.Fit()
