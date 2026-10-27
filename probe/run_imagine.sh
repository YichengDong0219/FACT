#!/bin/bash
# usage: run_imagine.sh <sim_gpu> <port> <rollout_name>  -> runs/imagine/<name>.real_vs_imagined.mp4
set -u
G=$1; P=$2; N=$3; R=~/fact_g0_claude/runs; mkdir -p $R/imagine
cd /home/dongyicheng/RoboTwin-FACT
export PATH=/home/dongyicheng/miniconda3/envs/robotwin/bin:/home/dongyicheng/miniconda3/bin:/usr/local/cuda-12.4/bin:$PATH
export CUDA_HOME=/usr/local/cuda-12.4 TORCH_CUDA_ARCH_LIST=8.9 TORCH_EXTENSIONS_DIR=/home/dongyicheng/.cache/openwam-robotwin-torch-extensions
export CUDA_VISIBLE_DEVICES=$G PYTHONUNBUFFERED=1 FACT_PROBE_DIR=/home/dongyicheng/fact_g0_claude/code
export PYTHONPATH=/home/dongyicheng/FACT:/home/dongyicheng/RoboTwin-FACT:/home/dongyicheng/fact_g0_claude/code
t0=$(date +%s)
timeout 3000 /home/dongyicheng/miniconda3/envs/robotwin/bin/python /home/dongyicheng/fact_g0_claude/code/imagine_episode.py --rollout $R/$N.json --port $P --out $R/imagine/$N.real_vs_imagined.mp4 > $R/imagine/$N.log 2>&1
rc=$?; echo "{\"name\":\"imagine_$N\",\"gpu\":\"$G\",\"rc\":$rc,\"wall_s\":$(( $(date +%s)-t0 ))}" >> $R/ledger.jsonl
grep -o '{"video.*' $R/imagine/$N.log; echo rc=$rc
