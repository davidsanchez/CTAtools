## Fermi catalog
export FERMI_CATALOG_DIR="/gpfs/LAPP-DATA/cta/Catalog/"
export VERSION_3FGL="16"
export VERSION_2FGL="09"
export VERSION_1FHL="07"
export VERSION_2FHL="08"
export VERSION_2FHL="11"
export FARM="LAPP"

#code location
export CTATOOLS_DIR="/grid_sw/soft-dev-cta/ScienceTools/CTAtools"
export CTATOOLS_CONF=$CTATOOLS_DIR"/ctoolsAnalysis/config"
export EBL_FILE_PATH=$CTATOOLS_DIR"/ebltable/ebl_model_files"

#manage Python
unset PYTHONPATH
export PYTHONPATH=$CTATOOLS_DIR
