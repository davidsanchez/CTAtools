.. _setup:

Installation
============

Download
--------

To checkout the code just typ :

.. code-block:: bash

    git clone https://github.com/davidsanchez/CTAtools.git



Setup
-----

The setup of the code is quite simple but require to edit the file name Init_tools.sh and replace the lines


.. code-block:: bash

    export CTATOOLS_DIR="Where is the CTAtools code"
    export FERMI_CATALOG_DIR = "Where are the Fermi catalog in fits format"

by the actual location of the code and the Fermi catalogs. You can also change the version of the catalogs with the variable "VERSION_XXX"



Then to test the installation and if you have all the libraries, you can run

.. code-block:: bash

    python test_setup.py
    
In the output, the section "DIRECTORIES" has to be correct. The tool check a lot of libraries but the mandatory one are : pyfits, astropy, numpy, scipy, and matplotlib. More on the needed libraries to come
