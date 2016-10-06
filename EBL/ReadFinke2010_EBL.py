import numpy
import string
from os.path import join
from environ import INST_DIR

class FinkeReader():
    def __init__(self,z):
        '''init function with the user redshift'''
        self._changeRedshift(z)

    def _changeRedshift(self,z):
        '''function call at the init of the class and use is the user want to change the redshit'''
        self.z = z
        self.file1 = join(INST_DIR, 'EBL/Finke2010/tau_modelC_total_z'+str(int(z*100)/100.)+'.dat')
        self.file2 = join(INST_DIR, 'EBL/Finke2010/tau_modelC_total_z'+str(int((z+0.01)*100)/100.)+'.dat')
        self.data1 = open(self.file1,"r").readlines()
        self.data2 = open(self.file2,"r").readlines()

    def GetTau(self):
        '''Function to get the energy and the value of tau for the given redshift'''
        Size = len(self.data1)
        tau = numpy.zeros(Size)
        tau1 = numpy.zeros(Size)
        tau2 = numpy.zeros(Size)
        ener1 = numpy.zeros(Size)
        ener2 = numpy.zeros(Size)
        for i in xrange(Size):
            words = string.split(self.data1[i])
            tau1[i] = float(words[1])
            ener1[i] = float(words[0])
        for i in xrange(Size):
            words = string.split(self.data2[i])
            tau2[i] = float(words[1])
            ener2[i] = float(words[0])

        tau = (tau2-tau1)*(self.z-int(self.z*100)/100.)/0.01 + tau1
        return ener1,tau

if __name__ == '__main__':
    reader = FinkeReader(0.117)
    ener,tau = reader.GetTau()
    
    import matplotlib.pyplot as plt
    plt.plot(ener,tau)
    plt.show()
