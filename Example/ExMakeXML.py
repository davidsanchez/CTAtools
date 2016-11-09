import  ctoolsAnalysis.xml_generator as xml

lib,doc = xml.CreateLib()

#SOURCE SPECTRUM
spec = xml.addPowerLaw1(lib,"crab","PointSource", 1e6)
#spec = xml.addPowerLaw2(lib,"crab","PointSource")
#spec = xml.addLogparabola(lib,"crab","PointSource")
#spec = xml.addExponotialCutOffPL(lib, "crab","PointSource", 1e6)
#spec = xml.addGaussian(lib, "crab","PointSource")
#spatial = xml.AddPointLike(doc,83.6331,22.0145)
#spatial = xml.AddDisk(doc,83.6331,22.0145,0.2)
#spatial = xml.AddGauss(doc,83.6331,22.0145,0.2)
spatial = xml.AddMapCube(doc,1)
spec.appendChild(spatial)
lib.appendChild(spec)

#CTA BACKGROUND
#bkg = xml.addCTABackgroundPolynom(lib,[.1,.1,3,5],[0,1,1,1])
#bkg = xml.addCTABackgroundProfile(lib)
bkg = xml.addCTAIrfBackground(lib)
lib.appendChild(bkg)

open('Test_xml_generator.xml', 'w').write(doc.toprettyxml('  '))
