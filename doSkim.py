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

def GetFileList(inputList):
    fileList = []
    if len(inputList) > 0:
        with open(inputList,'r') as filelist:
            for line in filelist:
                fileList.append(line.strip())
    else:
        # default file
        #fileList.append('root://eoscms.cern.ch//eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/customNano/scooper/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/LQ_ext1/190412_070908/0000/DYJetsToLL_Zpt-0To50_1-1.root')
        fileList.append('root://eoscms.cern.ch//eos/cms/store/group/phys_exotica/leptonsPlusJets/LQ/customNano/scooper/SinglePhoton/Run2016C-17Jul2018-v1/190412_103959/0000/SinglePhoton_Run2016C-17Jul2018-v1_1-1.root')
    return fileList


parser = argparse.ArgumentParser("")
parser.add_argument('-isMC','--mc', dest='isMC', action='store_true')
parser.add_argument('-isData','--data', dest='isMC', action='store_false')
parser.set_defaults(isMC=True)
#parser.add_argument('-jobNum', '--jobNum', type=int, default=1, help="")
parser.add_argument('-era', '--era', type=str, default="2016", help="")
parser.add_argument('-dataRun', '--dataRun', type=str, default="X", help="")
parser.add_argument('-haddFileName', '--haddFileName', type=str, default="tree.root", help="")
parser.add_argument('-inputList', '--inputList', type=str, default="", help="")
args = parser.parse_args()
print "args = ",args
isMC = args.isMC
era = args.era
dataRun = args.dataRun
haddFileName = args.haddFileName
inputList = args.inputList

print "isMC =",isMC,"era =",era,"dataRun =",dataRun,"haddFileName =",haddFileName,"inputList=",inputList

modulesToRun = []
#modulesToRun.append( pdfWeightProducer() ) 
jsonFile=None

if isMC:
    if era == "2016":
        #modulesToRun.extend([puAutoWeight_2016(),jetmetUncertainties2016All(),btagSFProducer("2016","cmva")])
        #FIXME put back jetmetUncertainties once they aren't so bloated
        modulesToRun.extend([puAutoWeight_2016(),btagSFProducer("2016","cmva")])
    elif era == "2017":
        #modulesToRun.extend([puAutoWeight_2017(),jetmetUncertainties2017All(),btagSFProducer("2017","deepcsv")])
        modulesToRun.extend([puAutoWeight_2017(),btagSFProducer("2017","deepcsv")])
    elif era == "2018":
        #modulesToRun.extend([puAutoWeight_2018(),jetmetUncertainties2017All(),btagSFProducer("2018","deepcsv")])
        modulesToRun.extend([puAutoWeight_2018(),btagSFProducer("2018","deepcsv")])
else:
    if era == "2016":
        jsonFile='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt'
    elif era == "2017":
        jsonFile='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
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
    elif era == "2018":
        jsonFile='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt'
        #FIXME TODO
    else:
        print 'ERROR: Did not understand the given era!  Should be one of 2016,2017,2018. Quitting.'
        exit(-1)

modulesToRun.append(eventCounterHistogramModule())

# Require SCEt > 35
#preselection="(Electron_caloEnergy[0]/cosh(Electron_scEta[0]))>35"
preselection="( (((((Muon_pt[0])>17)*((Muon_pt[1])>8))+(((Electron_pt[0])>23)*((Electron_pt[1])>12)))>0)*((Jet_pt[0])>17)*((Jet_pt[1])>17) )"
keepAndDrop='/afs/cern.ch/work/v/vinguyen/public/LQ2Analysis/CMSSW_10_2_10/src/PhysicsTools/NanoAODTools/python/postprocessing/analysis/LQ/keepAndDrop.txt'
files=GetFileList(inputList)
print 'files=',files

p=PostProcessor(".",files,cut=preselection,outputbranchsel=keepAndDrop,modules=modulesToRun,provenance=True,fwkJobReport=True,jsonInput=jsonFile,haddFileName=haddFileName)
p.run()
