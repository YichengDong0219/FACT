# FACT baseline on <lab-4090-host>

Repository: /home/dongyicheng/FACT
Upstream: https://github.com/Bariona/FACT
Commit: 5b299a2059f00c043fedc5c9dd17bf43fa14cbec

## Run

The helper sets the conda interpreter, CUDA toolkit, extension cache, offline
model loading, and GPU visibility. No proxy is needed for evaluation.

Terminal 1:
```bash
cd /home/dongyicheng/FACT
bash local/run_baseline.sh server
```

Terminal 2:
```bash
cd /home/dongyicheng/FACT
TEST_NUM=50 bash local/run_baseline.sh client beat_block_hammer demo_clean
# Or all 50 tasks, 50 valid episodes each:
bash local/run_baseline.sh sweep demo_clean 50
# Randomized suite:
bash local/run_baseline.sh sweep demo_randomized 50
```

Standalone smoke (starts/stops its own server, writes timestamped logs):
```bash
bash /home/dongyicheng/FACT/local/run_baseline.sh smoke adjust_bottle demo_clean
```

Default model GPU: physical GPU 0. Default simulator GPU: physical GPU 1.
Override with SERVER_GPU / CLIENT_GPU. Both are set before CUDA initialization.
Default port: 8093, localhost only. Set PORT for both terminals to change it.
Do not launch standalone smoke while another server occupies this port.

## Environment and assets

- Model conda env: /home/dongyicheng/miniconda3/envs/fact
  Python 3.11, torch 2.6.0+cu124, torchvision 0.21.0,
  diffusers 0.36.0, transformers 4.51.3; upstream pinned dependencies.
- Simulator env: /home/dongyicheng/miniconda3/envs/robotwin
- Simulator checkout: /home/dongyicheng/RoboTwin-FACT
  Commit 0aeea2d669c0f8516f4d5785f0aa33ba812c14b4.
- objects, embodiments, background_texture reuse existing assets via symlinks
  into /home/dongyicheng/RoboTwin-OpenWAM/assets. Keep that directory available.
- CUDA toolkit: /usr/local/cuda-12.4
- cuRobo extension cache:
  /home/dongyicheng/.cache/openwam-robotwin-torch-extensions

Weights:
- models/fact-wam: Bariona/fact-wam at
  887f66bc0be860ede339bb2843fb3c79a8553278.
- models/Wan2.2-TI2V-5B-Diffusers: Wan-AI/Wan2.2-TI2V-5B-Diffusers at
  b8fff7315c768468a5333511427288870b2e9635.
  Includes tokenizer, text encoder, VAE, scheduler, configs. The base Wan
  transformer weights are unnecessary for released FACT inference, which
  loads its own transformer; they are intentionally omitted.
- Training demonstrations and preprocessing caches are not needed for
  evaluation and are not downloaded. This setup targets released baseline
  evaluation, not immediate training from raw demonstrations.

## Local changes

- evaluation/robotwin/launch_config.yml contains actual simulator/env paths,
  RTX 4090 architecture 8.9, request timeout 300 seconds, startup wait 600 seconds.
- RoboTwin receives the upstream FACT test_num patch so requested episode
  counts and result denominators match.
- local/robotwin_compat.py initializes CUDA/cuRobo before SAPIEN and supplies
  the legacy warp.torch namespace required by the existing cuRobo version.
  Only RoboTwin-FACT/script/eval_policy.py imports this compatibility module.
- The helper sets the CUDA/ffmpeg/ninja paths. No task dynamics, scoring,
  action scaling, or seed filtering changes were made.
- Inference uses upstream settings: 20 denoising steps, action chunk 48,
  execute 48 actions per plan, CFG 0, prefix cache enabled, best-of-N disabled,
  future-state/value denoising enabled. Full sweeps disable video by default;
  smoke enables simulator video.
- setup_env.local.sh uses the Tsinghua PyPI mirror to install the same pinned
  versions; upstream setup_env.sh is retained unchanged.

## Evidence

setup_logs/render_preflight.log: RENDER_PREFLIGHT_PASS.
setup_logs/task_preflight.log: TASK_SETUP_PASS and EXPERT_PREFLIGHT_SUCCESS True.
setup_logs/server_help.log: inference server imports and argument parsing passed.
setup_logs/weights_manifest.json: created only after all requested weight
files download successfully and every large file passes SHA-256 verification.
setup_logs/baseline_status.txt and validation.log: final smoke status/evidence.
eval_runs/smoke_*/: server/client logs; status.txt is created on successful exit.
RoboTwin-FACT/eval_result/: per-episode results and simulator videos.

Environment snapshots: setup_logs/fact_environment.yml, fact_pip_freeze.txt.
Patch snapshots: setup_logs/fact_local.patch, robotwin_local.patch.
pip_check.log reports only upstream-documented LeRobot optional-dependency and
datasets-version mismatches; these are not used by the baseline path.

## Downloads

local/download_ranges.py uses resumable 16 MiB ranges with SHA-256 verification
against Hugging Face LFS metadata from the pinned revisions.
Download logs: setup_logs/download_ranges.log.
Download proxy configuration is private, excluded from git, and is not needed
for baseline execution. Do not publish it.

## Verified completion (2026-10-26)

Offline validation completed at 16:48 CST; logs audited after 22:11 CST.
Real-model closed-loop results on adjust_bottle:
- demo_clean: 1/1 success, seed 100001.
- demo_randomized: 1/1 success, seed 100000.

These are smoke results, not a full benchmark score. Full 50-task sweeps have
not been run.

Evidence: eval_runs/validation_20261026_164352/ contains status.txt (complete),
client_demo_clean.log, client_demo_randomized.log, and server.log.
Both episode videos and result files are saved under:
/home/dongyicheng/RoboTwin-FACT/eval_result/adjust_bottle/

The validation server exited after testing. No FACT server or dedicated
FACT download proxy remains running. Evaluation requires no proxy.
