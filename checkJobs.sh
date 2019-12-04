#!/bin/bash

localdir=$1
eosdir=$2

#echo -n "Grepping error files..."
##find $localdir -iname "*.err" -exec grep -ivH "no dict" {} \;
#find $localdir -iname "*.err" -exec grep -ivH "No branch name is matching wildcard" {} \;
#echo "done."
##echo "submit files: `find $localdir -iname "submit*sh" | wc -l`"
##echo "files on eos: `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir | grep -v '.sys.v#.' | wc -l`"

dirlist=`find $localdir -maxdepth 1 -type d | tail -n +2`
#echo 'dirlist'$dirlist
declare -i numOKDatasets=0
declare -i numBadDatasets=0
declare -i numDatasets=0
echo
echo "Checking files on eos..."
txtOut="dataset    submitFiles    filesOnEOS    status    \n"
#echo -e $txtOut | column -t
for dir in $dirlist
do
  #echo $dir
  #echo "dataset=${dir##*/}  submit files: `find $localdir -iname \"submit*sh\" | wc -l` files on eos: `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir | grep -v '.sys.v#.' | wc -l`"
  # works
  #txtOut=$txtOut"${dir##*___} `find $dir -iname \"submit*sh\" | wc -l` `EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir/${dir##*___} | grep -v '.sys.' | wc -l`\n"

  numDatasets+=1
  numSubmitFiles=`find $dir -iname "submit*sh" | wc | awk '{print $1}'`
  submitFiles=`find $dir -iname "submit*sh"`
  #numEosFiles=`EOS_MGM_URL=root://eosuser.cern.ch eos find -f $eosdir/${dir##*___} | grep -v '.sys.' | wc -l`
  lastDirWithSuffix=$eosdir/${dir##*/}
  lastDir=${lastDirWithSuffix%___*}
  #echo "eos find -f $lastDir"
  numEosFiles=`eos find -f $lastDir | grep -v '.sys.' | wc -l`
  eosFiles=`eos find -f $lastDir | grep -v '.sys.'`
  eosDirCurrent=`eos find -f $lastDir -type d`

  #This will find any failed jobs and append them to failedJobs.txt
  for submit in $submitFiles; do
    submitNoPre=${submit##*_}
    submitNoExt=${submitNoPre%.*}
    #echo $submitNoExt
    check=`eos find -f $lastDir -maxdepth 1 -type f | grep "_$submitNoExt.root"`
    #echo $submit
    if [ -z "$check" ]; then
      echo "$submit" >> failedJobs2017.txt
      echo "found failed job:" $submit
    fi
  done

  for file in $eosFiles; do 
    size=`eos find --size $file | awk -F= '{size+=$3} END {print size/1024/1024}'` # MB
    test=`echo "$size < 1"| bc`
    if [ $test != "0" ]; then
      echo "--->Found file with small size: $file has $size MB"
    fi
  done
  #echo "lastDir=$lastDir"
  dataset=${lastDir##*/}
  #echo "dataset=$dataset"
  if [ "$numSubmitFiles" != "$numEosFiles" ]; then
    txtOut=$txtOut"$dataset $numSubmitFiles $numEosFiles BAD <<====\n"
    #echo -e "$dataset $numSubmitFiles $numEosFiles BAD <<====\n" | column -t
    #echo "numSubmitFiles=$numSubmitFiles"
    #echo "numEosFiles=$numEosFiles"
    numBadDatasets+=1
  else
    #txtOut=$txtOut"$dataset $numSubmitFiles $numEosFiles OK\n"
    #echo -e "$dataset $numSubmitFiles $numEosFiles OK <<====\n" | column -t
    numOKDatasets+=1
  fi
  echo -ne "Checked: $numDatasets datasets"'\r'
done
echo
echo "Done"
echo
echo "####################################################################################################"
echo "$numOKDatasets/$numDatasets datasets were checked and are OK."
if [ $numBadDatasets -gt 0 ]; then
  echo "$numBadDatasets/$numDatasets datasets have problems:"
  echo -e $txtOut | column -t
fi