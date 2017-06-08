#!/bin/bash

# -----------------------------------------------
# Environment setup
# -----------------------------------------------


#####################################################################
#This need to be in the .profile for LAPP users
#export LAPP_APP_SHARED=/gpfs/LAPP-DATA/hess/Fermi_temp/$USER

#if [ ! -d "${LAPP_APP_SHARED}" ]; then
#    mkdir ${LAPP_APP_SHARED}
#fi

#export HOME=$LAPP_APP_SHARED

#export PBS_O_HOME=$LAPP_APP_SHARED
#export PBS_O_INITDIR=$LAPP_APP_SHARED
#export TMP_DIR=/var/spool/pbs/tmpdir
#####################################################################

export HOME=$HOME



echo "~~~~~~~~ SETUP ENVIRONMENT ~~~~~~~~ "

# This will allow FTOOLS to run on the cluster, whereas if this is not
# set you get an error about '/dev/tty' e.g. when running ftcopy
export HEADASNOQUERY=1
#setenv HEADASNOQUERY 1
echo HEADASNOQUERY: $HEADASNOQUERY
echo PYTHONPATH: $PYTHONPATH
echo PATH: $PATH
