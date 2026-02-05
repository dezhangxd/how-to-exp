#!/bin/bash
mkdir -p slv
cd slv

git clone https://gitee.com/dezhangxd/kissat_inc.git
cd kissat_inc
chmod a+x starexec_build
./starexec_build
cd ..

git clone https://gitee.com/dezhangxd/Relaxed_LCMDCBDL_newTech.git
cd Relaxed_LCMDCBDL_newTech
chmod a+x starexec_build
./starexec_build
cd ..


git clone https://gitee.com/dezhangxd/ParKissat-RS.git
cd ParKissat-RS/kissat_mab
chmod a+x configure
chmod a+x scripts/*.sh
./configure
make -j
cd ..
make -j
cd ..


cd ../