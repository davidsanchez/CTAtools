.. _FermiCatalog:

Catalog Reader
=============

Supported catalog
-----------------

Currently the catalogs that can be read are the 2FGL, the 3FGL, the 1FHL and the 2FHL. Fits files should be :
  * gll_psc_v14.fit
  * gll_psc_v08.fit
  * gll_psch_v07.fit
  * gll_psch_v08.fit


Code
----

A Catalog instance can be created using 


.. code-block:: python

	Cat = FermiCatalogReader(source,"Where are the catalog files","e2dnde","TeV")

The usere need to provide :

   * catalog name of the source
   * folder where the Fermi catalog are
   * Representations for the plot (dnde, ednde, e2dnde)
   * energy scale : MeV, GeV or TeV


Capability
----------

Most of the information are in a dictionnary name CatalogData. The keys of this dictionnary are the catalog acronyms (2FGL, 3FHL, etc...)

This module can :

   * Provide the spectral model from a catalog using GetModel
   * Provide the source Class
   * Provide the source variability index
   * Provide the source position
   * Retrive the data point to plot them
   * Retrive the source model parameters
   * Be used to plot the spectral models


Exemple
-------

An exemple of the capability and how to use the code can be found un the exemple folder. The script is named ExReadFermiCatalog.py and will produce a nice plot with 3 catalog results and 

.. figure::  _static/Catalog_Ex.png
   :align:   center
	
   2FGL, 3FGL and 2FHL butterfly from the Fermi catalog for the source 2FGL J1015.1+4925
