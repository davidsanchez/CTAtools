import os

CONFIG_DIR = os.environ.get("CTATOOLS_CONF",'')
INST_DIR = os.environ.get("CTATOOLS_DIR",'')
FERMI_CATALOG_DIR = os.environ.get('FERMI_CATALOG_DIR', '')

VERSION_3FGL = os.environ.get("VERSION_3FGL",'')
VERSION_2FGL = os.environ.get("VERSION_2FGL",'')
VERSION_1FHL = os.environ.get("VERSION_1FHL",'')
VERSION_2FHL = os.environ.get("VERSION_2FHL",'')


DIRS = {"CONFIG_DIR":CONFIG_DIR,
        "INST_DIR":INST_DIR,
        "FERMI_CATALOG_DIR":FERMI_CATALOG_DIR}
