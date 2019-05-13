#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jecUncertainties import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.mht import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.pdfWeightProducer import * 

from PhysicsTools.NanoAODTools.postprocessing.analysis.LQ.eventCounterHistogramModule import *

import argparse

print "args are: ",sys.argv

isMC = True
era = "2016"
#if len(sys.argv) > 1:
#    if sys.argv[1] == "0":
#        isMC = False
#if len(sys.argv) > 2:
#    era = sys.argv[2]
#if era!="2016" and era!="2017":
#    print "Run era must be 2016 or 2017, exiting.."
#    sys.exit(1)
#btagger = "deepcsv"
#if era == "2016":
#    btagger = "cmva"
dataRun = ""
#if len(sys.argv) > 3:
#    dataRun = sys.argv[3]
parser = argparse.ArgumentParser("")
parser.add_argument('-isMC', '--isMC', type=int, default=1, help="")
parser.add_argument('-jobNum', '--jobNum', type=int, default=1, help="")
parser.add_argument('-era', '--era', type=str, default="2017", help="")
parser.add_argument('-dataRun', '--dataRun', type=str, default="X", help="")
args = parser.parse_args()
print "args = ",args
isMC = args.isMC
era = args.era
dataRun = args.dataRun

print "isMC = ",isMC,"era = ",era, "dataRun = ",dataRun

modulesToRun = []
#modulesToRun.append( pdfWeightProducer() ) 

if isMC:
    if era == "2016":
        modulesToRun.extend([puAutoWeight_2016(),jetmetUncertainties2016All(),btagSFProducer("2016","cmva")])
    elif era == "2017":
        modulesToRun.extend([puAutoWeight_2017(),jetmetUncertainties2017All(),btagSFProducer("2017","deepcsv")])
    elif era == "2018":
        modulesToRun.extend([puAutoWeight_2018(),jetmetUncertainties2017All(),btagSFProducer("2018","deepcsv")])
else:
    if era == "2016":
        pass
    elif era == "2017":
        if dataRun == "B":
            modulesToRun.extend([jetRecalib2017B()])
        if dataRun == "C":
            modulesToRun.extend([jetRecalib2017C()])
        if dataRun == "D":
            modulesToRun.extend([jetRecalib2017D()])
        if dataRun == "E":
            modulesToRun.extend([jetRecalib2017E()])
        if dataRun == "F":
            modulesToRun.extend([jetRecalib2017F()])

modulesToRun.append(eventCounterHistogramModule())

preselection="(Electron_scEnergy[0]/cosh(Electron_scEta[0]))>50"

files=['root://eoscms.cern.ch//eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/customNano/scooper/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/LQ_ext1/190412_070908/0000/DYJetsToLL_Zpt-0To50_1-1.root']


p=PostProcessor(".",files,cut=preselection,branchsel='keepAndDrop.txt',modules=modulesToRun,provenance=True,fwkJobReport=True)
p.run()
