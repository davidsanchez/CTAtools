from environ import DIRS
import os

def check_command_line_tools():
    """Check command line tool availability"""
    from subprocess import Popen, PIPE
    print('*** COMMAND LINE TOOLS ***')
    for tool in ['python', 'ipython', 'ctlike']:
        location = Popen(['which', tool],
                         stdout=PIPE).communicate()[0]
        print('{0:.<20} {1}'.format(tool, location.strip() or 'MISSING'))


def check_python_modules():
    """Check python package availability"""
    PACKAGES = ['ebltable','pyfits', 'astropy','yaml','iminuit','numpy','scipy','matplotlib','ebl']
    print('*** PYTHON PACKAGES ***')
    for package in PACKAGES:
        try:
            exec('import %s' % package)
            filename = eval('%s.__file__' % package)
            print('{0:.<20} {1}'.format(package, filename))
        except ImportError:
            print('{0:.<20} {1}'.format(package, 'MISSING'))



def check_dirs():
    """Check directory availability"""
    print('*** DIRECTORIES ***')
    for tag in DIRS.keys():
        dir = DIRS.get(tag, 'MISSING')
        status = 'YES' if os.path.isdir(dir) else 'NO'
        print('{tag:.<20} {status:.<10} {dir}'.format(**locals()))

if __name__ == '__main__':
    check_command_line_tools()
    check_python_modules()
    check_dirs()
