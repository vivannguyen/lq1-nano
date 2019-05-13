## LQ1 nanoAOD tools

### run the following to setup the area
    cmsrel CMSSW_10_2_12
    cd $CMSSW_BASE/src
    git clone git@github.com:cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
    git clone git@github.com:CMSLQ/lq1-nano.git PhysicsTools/NanoAODTools/python/postprocessing/analysis/LQ
    cd PhysicsTools/NanoAODTools
    scram b

