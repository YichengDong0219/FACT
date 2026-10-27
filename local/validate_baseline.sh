#!/usr/bin/env bash
set -euo pipefail
cd /home/dongyicheng/FACT
echo waiting_for_weights > setup_logs/baseline_status.txt
while [[ ! -f setup_logs/weights_manifest.json ]]; do
 if ! kill -0 "${1:?download PID required}" 2>/dev/null; then
  echo download_failed > setup_logs/baseline_status.txt
  exit 1
 fi
 sleep 15
done
run="/home/dongyicheng/FACT/eval_runs/validation_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$run"
echo "$run" > setup_logs/validation_run.txt
export PYTHONPATH="/home/dongyicheng/FACT:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1
echo starting_server > setup_logs/baseline_status.txt
setsid bash local/run_baseline.sh server > "$run/server.log" 2>&1 &
pid=$!
cleanup() { kill -- "-$pid" 2>/dev/null || true; }
trap cleanup EXIT
trap 'echo validation_failed > setup_logs/baseline_status.txt' ERR
/home/dongyicheng/miniconda3/envs/fact/bin/python local/wait_server.py "$pid"
for mode in demo_clean demo_randomized; do
 echo "running_$mode" > setup_logs/baseline_status.txt
 TEST_NUM=1 EVAL_VIDEO_LOG=1 bash local/run_baseline.sh client adjust_bottle "$mode" > "$run/client_$mode.log" 2>&1
done
echo complete > "$run/status.txt"
echo complete > setup_logs/baseline_status.txt
echo "VALIDATION_COMPLETE $run"
