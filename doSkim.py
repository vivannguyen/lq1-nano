#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jecUncertainties import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.jme.mht import *
# needs CMSSW?
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.analysis.LQ.eventCounterHistogramModule import *



preselection="(Electron_scEnergy[0]/cosh(Electron_scEta[0]))>50"
modulesToRun = [eventCounterHistogramModule()]

files=['root://eoscms.cern.ch//eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/customNano/scooper/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/LQ_ext1/190412_070908/0000/DYJetsToLL_Zpt-0To50_1-1.root']


p=PostProcessor(".",files,cut=preselection,branchsel='keepAndDrop.txt',modules=modulesToRun,provenance=True,fwkJobReport=True)
p.run()
