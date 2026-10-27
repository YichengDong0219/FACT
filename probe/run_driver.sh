#!/bin/bash
# usage: run_driver.sh <gpu> <name> <driver args...>   (foreground; logs + wall time into runs/<name>.*)
set -u
G=$1; N=$2; shift 2
R=~/fact_g0_claude/runs
[ -e $R/$N.json ] && { echo "exists $N"; exit 2; }
cd /home/dongyicheng/RoboTwin-FACT
export PATH=/home/dongyicheng/miniconda3/envs/robotwin/bin:/home/dongyicheng/miniconda3/bin:/usr/local/cuda-12.4/bin:$PATH
export CUDA_HOME=/usr/local/cuda-12.4 TORCH_CUDA_ARCH_LIST=8.9 TORCH_EXTENSIONS_DIR=/home/dongyicheng/.cache/openwam-robotwin-torch-extensions
export CUDA_VISIBLE_DEVICES=$G PYTHONUNBUFFERED=1 FACT_PROBE_DIR=/home/dongyicheng/fact_g0_claude/code
export PYTHONPATH=/home/dongyicheng/FACT:/home/dongyicheng/RoboTwin-FACT:/home/dongyicheng/fact_g0_claude/code
t0=$(date +%s)
timeout 1500 /home/dongyicheng/miniconda3/envs/robotwin/bin/python /home/dongyicheng/fact_g0_claude/code/g0_driver.py "$@" --out $R/$N.json > $R/$N.log 2>&1
rc=$?; echo "{\"name\":\"$N\",\"gpu\":\"$G\",\"rc\":$rc,\"wall_s\":$(( $(date +%s)-t0 ))}" >> $R/ledger.jsonl
tail -1 $R/$N.log; echo rc=$rc
