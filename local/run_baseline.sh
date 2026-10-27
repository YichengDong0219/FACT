#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/dongyicheng/FACT
export PATH=/home/dongyicheng/miniconda3/bin:/usr/local/cuda-12.4/bin:$PATH
export FACT_CONDA_ENV=/home/dongyicheng/miniconda3/envs/fact
export CUDA_HOME=/usr/local/cuda-12.4
export TORCH_EXTENSIONS_DIR=/home/dongyicheng/.cache/openwam-robotwin-torch-extensions
export MAX_JOBS=4
export PYTHONUNBUFFERED=1
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
cd "$ROOT"
mode=${1:-smoke}
shift || true
case "$mode" in
 server)
  export CUDA_VISIBLE_DEVICES=${SERVER_GPU:-0}
  exec bash evaluation/robotwin/launch_server.sh "$@"
  ;;
 client)
  export CUDA_VISIBLE_DEVICES=${CLIENT_GPU:-1}
  exec bash evaluation/robotwin/launch_client.sh "$@"
  ;;
 sweep)
  export CUDA_VISIBLE_DEVICES=${CLIENT_GPU:-1}
  exec bash evaluation/robotwin/eval_all_tasks.sh "$@"
  ;;
 smoke)
  run="$ROOT/eval_runs/smoke_$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$run"
  echo "$run"
  bash "$0" server > "$run/server.log" 2>&1 &
  server_pid=$!
  cleanup() { pkill -P "$server_pid" 2>/dev/null || true; kill "$server_pid" 2>/dev/null || true; }
  trap cleanup EXIT
  export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
  /home/dongyicheng/miniconda3/envs/fact/bin/python "$ROOT/local/wait_server.py" "$server_pid"
  EVAL_VIDEO_LOG=${EVAL_VIDEO_LOG:-1} TEST_NUM=${TEST_NUM:-1} bash "$0" client "${1:-adjust_bottle}" "${2:-demo_clean}" > "$run/client.log" 2>&1
  echo complete > "$run/status.txt"
  echo "Completed: $run"
  ;;
 *) echo "Usage: $0 {server|client [task config]|sweep [config episodes]|smoke [task config]}"; exit 2 ;;
esac
