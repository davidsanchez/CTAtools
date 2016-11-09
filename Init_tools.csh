## Fermi catalog
setenv FERMI_CATALOG_DIR "Where are the Fermi catalog in fits format"
setenv VERSION_3FGL "16"
setenv VERSION_2FGL "09"
setenv VERSION_1FHL "07"
setenv VERSION_2FHL "08"


#code location
setenv CTATOOLS_DIR "Where is the CTAtools code"
setenv CTATOOLS_CONF $CTATOOLS_DIR"/ctoolsAnalysis/config"
setenv EBL_FILE_PATH $CTATOOLS_DIR"/ebltable/ebl_model_files"

#manage Python
unset PYTHONPATH
setenv PYTHONPATH $CTATOOLS_DIR
