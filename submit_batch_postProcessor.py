#! /usr/bin/env python

import os
import sys
import string
import re
from optparse import OptionParser


def PrepareJobScript(outputname):
    with open(outputname,"w") as outputfile:
        outputfile.write("#!/bin/bash\n")
        # use CMSSW
        outputfile.write("cd "+pwd+"\n")
        outputfile.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
        outputfile.write("eval `scramv1 runtime -sh`\n")
        #outputfile.write("cmsenv\n")
        outputfile.write("cd -\n")
        # CMSSW requires $HOME to be set
        outputfile.write('[ -z "$HOME" ] && export HOME=$PWD\n')
        if isMC:
            postProcOptions=' --mc'
        else:
            postProcOptions=' --data'
        postProcOptions+=' --era={}'.format(options.era)
        postProcOptions+=' --dataRun={}'.format(options.dataRun)
        postProcOptions+=' --inputList={}'.format(inputfilename)
        postProcOptions+=' --haddFileName={}_tree_{}.root'.format(outputPrefix,ijob)
        outputfile.write('./'+execName+postProcOptions+'\n')
        outputfile.write("mv -v FrameworkJobReport.xml "+outputmain+"/output/FrameworkJobReport_"+str(ijob)+".xml"+"\n")
        outputfile.write("xrdcp -fs "+"\""+outputPrefix+"_tree_"+str(ijob)+".root\" \""+eosHost+'/'+outputeosdir+"/"+dataset+"_tree_"+str(ijob)+".root\"\n")


def WriteSubmitFile(condorFileName):
    with open(condorFileName,'w') as condorFile:
        condorFile.write('executable  = '+outputmain+'/src/submit_$(Process).sh\n')
        condorFile.write('N = '+str(ijobmax)+'\n')
        condorFile.write('output      = output/$(Process).out\n')
        condorFile.write('error       = error/$(Process).err\n')
        condorFile.write('log         = log/$(Process).log\n')
        #http://batchdocs.web.cern.ch/batchdocs/local/submit.html
        condorFile.write('+JobFlavour = "'+options.queue+'"\n')
        # require CentOS7
        condorFile.write('requirements = (OpSysAndVer =?= "CentOS7")\n')
        # make sure the job finishes with exit code 0
        #condorFile.write('on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        condorFile.write('max_retries = 3\n')
        condorFile.write('should_transfer_files = YES\n')
        condorFile.write('transfer_output_files = ""\n')
        condorFile.write('transfer_input_files = '+options.executable+',input/input_$(Process).list,'+'\n')
        condorFile.write('queue $(N)\n')


#FIXME usage string
usage = "usage: %prog [options] \nExample: ./scripts/submit_batch.py -i HeepStudies_v1/MinimumBias__Commissioning10-SD_EG-v9__RECO_short.txt -c HeepStudies_v1/cutFile_HeepElectronStudiesV1.txt -o TestFrancesco/Mydataset -t rootTupleTree/tree -n 2 -q 1nh -d /eos/cms/store/user/eberry/"

parser = OptionParser(usage=usage)

parser.add_option("-i", "--inputlist", dest="inputlist",
                  help="list of all datasets to be used",
                  metavar="LIST")

parser.add_option("-o", "--output", dest="output",
                  help="the directory OUTDIR contains the output of the program",
                  metavar="OUTDIR")

parser.add_option("-n", "--ijobmax", dest="ijobmax",
                  help="max number of jobs, limited automatically to the number of files in inputlist",
                  metavar="IJOBMAX")

#http://batchdocs.web.cern.ch/batchdocs/local/submit.html
parser.add_option("-q", "--queue", dest="queue",
                  help="name of the queue",
                  metavar="QUEUE")

parser.add_option("-d", "--eosDir", dest="eosDir",
                  help="full path of the eos directory for the skim output",
                  metavar="EOSDIR")

parser.add_option("-m", "--eosHost", dest="eosHost",
                  help="root:// MGM URL for the eos host for the skim output",
                  metavar="EOSHOST")

parser.add_option("-e", "--exe", dest="executable",
                  help="executable",
                  metavar="EXECUTABLE")

parser.add_option("--mc", dest="isMC",
                  action='store_true',
                  help="process MC",
                  metavar="ISMC")

parser.add_option("--data", dest="isData",
                  action='store_true',
                  help="process data",
                  metavar="ISDATA")

parser.add_option("--era", dest="era",
                  help="data/MC era",
                  metavar="ERA")

parser.add_option("--dataRun", dest="dataRun",
                  help="data Run [A,B,C, etc.]",
                  metavar="DATARUN")


(options, args) = parser.parse_args()

optionMissing = False
if not options.inputlist:
    print 'ERROR: inputlist not specified'
    optionMissing = True
if not options.output:
    print 'ERROR: outputDir not specified'
    optionMissing = True
if not options.ijobmax:
    print 'ERROR: ijobmax not specified'
    optionMissing = True
if not options.queue:
    print 'ERROR: queue not specified'
    optionMissing = True
if not options.eosDir:
    print 'ERROR: eosDir not specified'
    optionMissing = True
if not options.eosHost:
    print 'ERROR: eosHost not specified'
    optionMissing = True
if not options.executable:
    print 'ERROR: executable not specified'
    optionMissing = True
if not options.isMC and not options.isData:
    print 'ERROR: mc/data not specified'
    optionMissing = True
if not options.dataRun:
    print 'ERROR: dataRun not specified'
    optionMissing = True
if not options.era:
    print 'ERROR: era not specified'
    optionMissing = True
if optionMissing:
    print
    parser.print_help()
    sys.exit(-1)

isMC = options.isMC
if isMC==options.isData:
    print 'ERROR: cannot specify both --mc and --data!'
    parser.print_help()
    sys.exit(-1)

eosHost = options.eosHost.rstrip('/')
################################################
pwd = os.getcwd()

outputmain = options.output.rstrip("/")
if not re.search("^/", outputmain):
    outputmain = pwd + "/" + outputmain

inputlist = options.inputlist
if not re.search("^/", inputlist):
    inputlist = pwd + "/" + inputlist

execName = options.executable.split('/')[-1]
################################################
# write on local disk
################################################
os.system("mkdir -p "+outputmain)
os.system("mkdir -p "+outputmain+"/log/")
os.system("mkdir -p "+outputmain+"/error/")
os.system("mkdir -p "+outputmain+"/input/")
os.system("mkdir -p "+outputmain+"/src/")
os.system("mkdir -p "+outputmain+"/output/")
#os.system("mkdir -p "+outputmain+"/skim/")
#################################################
# output prefix
outputPrefix = string.split(outputmain,"/")[-1]
#################################################
# dataset
dataset = string.split(outputPrefix,"___")[0]
################################################
# create eos dir
################################################
outputeosdir = options.eosDir    
outputeosdir = outputeosdir.rstrip('/') + '/' + dataset
os.system("/usr/bin/eos mkdir -p "+outputeosdir)
#################################################
numfiles = len(file(inputlist).readlines())
ijobmax=int(options.ijobmax)
if ijobmax > numfiles:
    ijobmax=numfiles
filesperjob = int(numfiles/ijobmax)
if numfiles%ijobmax!=0:
    filesperjob = filesperjob+1
    ijobmax = int(numfiles/filesperjob)
    if numfiles%filesperjob!=0:
        ijobmax = ijobmax+1
#################################################
input = open(inputlist)
#################################################
for ijob in range(ijobmax):
    # prepare the list file
    inputfilename = outputmain+"/input/input_"+str(ijob)+".list"
    inputfile = open(inputfilename,"w")
    for i in range(filesperjob):
        line = input.readline()
        if line != "":
            inputfile.write(line)
        continue
    inputfile.close()

    # prepare the exec script
    outputname = outputmain+"/src/submit_"+str(ijob)+".sh"
    PrepareJobScript(outputname)

input.close()

# write condor submit file
condorFileName = outputmain+'/condorSubmit.sub'
WriteSubmitFile(condorFileName)

failedToSub = False
print 'submit jobs for',options.output.rstrip("/")
#FIXME don't cd and use absolute paths in the condor submission instead
oldDir = os.getcwd()
os.chdir(outputmain)
exitCode = os.WEXITSTATUS(os.system('condor_submit '+condorFileName))
#print 'got exit code='+str(exitCode)
if exitCode != 0:
    print '\exited with '+str(exitCode)+'; try to resubmit'
    exitCode = os.WEXITSTATUS(os.system('condor_submit '+condorFileName))
    if exitCode != 0:
        failedToSub = True
os.chdir(oldDir)
if failedToSub:
    exit(-1)

