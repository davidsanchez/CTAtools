import CTAAnalysis.LikeFit as Fitter

ana = Fitter.Analyser("ana.conf")
ana.ctselect()
ana.ctbin()
ana.create_fit()
ana.fit()
ana.PrintResults()
