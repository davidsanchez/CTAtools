## Fermi catalog
export FERMI_CATALOG_DIR="Where are the Fermi catalog in fits format"
export VERSION_3FGL="16"
export VERSION_2FGL="09"
export VERSION_1FHL="07"
export VERSION_2FHL="08"

export FARM="LAPP"

#code location
export CTATOOLS_DIR="Where is the CTAtools code"
export CTATOOLS_CONF=$CTATOOLS_DIR"/ctoolsAnalysis/config"
export EBL_FILE_PATH=$CTATOOLS_DIR"/ebltable/ebl_model_files"

#manage Python
unset PYTHONPATH
export PYTHONPATH=$CTATOOLS_DIR
