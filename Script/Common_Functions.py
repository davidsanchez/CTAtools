import os,sys
from os.path import join
from ctoolsAnalysis.config import get_config,get_default_config

def MakeconfigFromDefault(out,work,source,ra,dec):
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
    return MakeconfigFromFile(out,work,source,ra,dec,conf_template)

def MakeconfigFromFile(out,work,source,ra,dec,conf_template):
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
    conf_template["out"] = out
    conf_template["work"] = work
    config = get_config(conf_template)
    config['file']['inobs'] = join(work, 'event_'+source.replace(" ","")+".fits")
    config['file']['selectedevent'] = join(work, 'event_selected_'+source.replace(" ","")+".fits")
    config['file']['inmodel'] = join(out, source.replace(" ","")+'_forSimu3FGLPosition.xml')
    config['file']['cube'] = join(work, 'Cube_'+source.replace(" ","")+".fits")
    config['file']['model'] = join(work, 'Model_'+source.replace(" ","")+".fits")
    
    config['target']['name'] = source.replace(" ","")
    config['target']['ra'] = ra
    config['target']['dec'] = dec
    return config

