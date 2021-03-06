import os,sys,numpy
from os.path import join
from ctoolsAnalysis.config import get_config,get_default_config

def MakeconfigFromDefault(out,source,ra,dec):
    '''
    Generate a config file from another the module default config
    Parameters
    ---------
    out : place where the fits file
    work : place where fits file will be temporarily stored and where the log file will be kept
    source : source name
    ra : right Ascension of the source
    dec : dec of the source
    '''
    conf_template = get_default_config()
    return MakeconfigFromFile(out,source,ra,dec,conf_template)

def MakeconfigFromFile(out,source,ra,dec,conf_template):
    '''
    Generate a config file from another default config file given in the parameters
    Parameters
    ---------
    out : place where the fits file
    work : place where fits file will be temporarily stored and where the log file will be kept
    source : source name
    ra : right Ascension of the source
    dec : dec of the source
    conf_template : default config provided by the user
    '''
    config = get_config(conf_template)
    config["out"] = out
    config['file']['inobs'] = 'event_'+source.replace(" ","")+".fits"
    config['file']['selectedevent'] =  'event_selected_'+source.replace(" ","")+".fits"
    config['file']['inmodel'] = source.replace(" ","")+'.xml'
    config['file']['cube'] = 'Cube_'+source.replace(" ","")+".fits"
    config['file']['model'] = 'Model_'+source.replace(" ","")+".fits"

    config['target']['name'] = source.replace(" ","")
    config['target']['ra'] = ra
    config['target']['dec'] = dec
    return config

def MakeFileFunction(energy,flux, name = 'output.txt'):
    ''' Make file function for ctools
    Parameters
    ---------
    energy : in MeV
    flux : ph/MeV/s/cm2
    '''

    datafile = numpy.array([energy,flux+1.e-200]).T
    print "write file function in ",name
    fileout=open(name,'w+')
    numpy.savetxt(fileout, datafile, fmt=['%.8E','%.8E'])
    fileout.close()
    print "done"

def IrfChoice(simutime):
    available_time = numpy.array([.5,5,50])
    indice =  numpy.abs(available_time-simutime).argmin()
    return str(available_time[indice])
