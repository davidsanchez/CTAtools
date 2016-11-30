import os

print "\033[34m Cloning ebltable repo\033[0m"
os.system("git clone https://github.com/me-manu/ebltable.git")


#print "\033[34m Updating ebltable repo\033[0m"
#os.system("git pull https://github.com/me-manu/ebltable.git")

print "\033[34m Test the setup\033[0m"
os.system("python test_setup.py")
