import numpy
import string
from os.path import join
from environ import INST_DIR

class FranceschiniReader():
    def __init__(self,z):
        self._changeRedshift(z)


    def _changeRedshift(self,z):
        self.z = z
        if z<1:
            self.file = join(INST_DIR, 'EBL/Franceschini2018_EBL_z0_1.dat')
        else:
            self.file = join(INST_DIR, 'EBL/Franceschini2018_EBL_z1_2.dat')
        self.data = open(self.file,"r").readlines()
        self.RedshiftTable = []
        self._Read()
        
    def _Read(self):
        for i in xrange(len(self.data)):
            words = string.split(self.data[i])
            if words[0] == "redshift":
                self.RedshiftTable.append(float(words[3]))
                if len(self.RedshiftTable)>1 and float(words[3])>=self.z and self.RedshiftTable[-2]<self.z:
                    self.indice = i+2
                
    def GetTau(self):
        Size = 50
        tau = numpy.zeros(Size)
        ener = numpy.zeros(Size)
        for i in xrange(Size):
            words = string.split(self.data[i+self.indice])
            tau[i] = float(words[2])
            ener[i] = float(words[0])
        return ener,tau
        
        

                
if __name__ == '__main__':
    reader = FranceschiniReader(0.117)
    ener,tau = reader.GetTau()
    
    import matplotlib.pyplot as plt
    plt.plot(ener,tau)
    plt.show()
