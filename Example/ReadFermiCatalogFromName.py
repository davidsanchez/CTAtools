# author David Sanchez david.sanchez@lapp.in2p3.fr

# ------ Imports --------------- #
from Catalog.ReadFermiCatalog import *
from environ import FERMI_CATALOG_DIR
# ------------------------------ #
#use the source name to create the cataloog and have acess to all the Fermi results
#This use the astropy SkyCoord.from_name function to resolve the source name
source = "M 87"
Cat = FermiCatalogReader.fromName(source,FK5,FERMI_CATALOG_DIR,"e2dnde","TeV")

#print some information
print "2FGL association ",Cat.Association('3FGL')
print "3FGL Name ",Cat.Association('2FHL','3FGL_name')
print "3FGL Var Index ",Cat.GetVarIndex("3FGL")







