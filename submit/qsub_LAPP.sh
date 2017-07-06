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

export HOME=$LAPP_APP_SHARED


