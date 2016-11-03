"""Central place for config file handling"""
import sys
from os.path import join
from ctoolsAnalysis.extern.configobj import ConfigObj, flatten_errors
from ctoolsAnalysis.extern.validate import Validator
from environ import CONFIG_DIR
import ctoolsAnalysis.Loggin as Loggin

def get_config(infile, configspec=join(CONFIG_DIR, 'default.conf')):
    """Parse config file, and in addition:
    - include default options
    - exit with an error if a required option is missing"""
    config = ConfigObj(infile, configspec=configspec,
                       file_error=True)

    validator = Validator()
    # @todo: I'm not sure we always want to copy all default options here
    results = config.validate(validator, copy=True)
    mes = Loggin.base()


    if results != True:
        for (section_list, key, _) in flatten_errors(config, results):
            if key is not None:
                mes.warning('The "%s" key in the section "%s" failed validation' %
                      (key, ', '.join(section_list)))
            else:
                mes.warning('The following section was missing:%s ' %
                      ', '.join(section_list))
        mes.warning('   Please check your config file for missing '
              'and wrong options!')
        mes.error('Config file is not valid.')

    return config


# @todo: This doesn't work because missing values are invalid!!!
# Maybe fill those values by hand?
def get_default_config(configspec=join(CONFIG_DIR, 'default.conf')):
    return ConfigObj(None, configspec=configspec)

