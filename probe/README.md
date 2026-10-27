# FACT failure-recovery probes (RoboTwin)

Research code layered on FACT without modifying its sources. Commits are ordered by development stage.

| Stage | Files | Purpose |
|---|---|---|
| deploy | `../local/`, `../BASELINE_4090.md`, `../setup_logs/` | RTX 4090 baseline setup and validation |
| G0 | `g0_driver.py` (rollout / replay / branch), `g0_compare.py`, `g0_model_check.py`, `inference_server_probe.py`, `seed_plan.py`, `client_adapter.py`, `branch_compare.py` | Explicit seeds; bit-exact closed-loop reproduction, action replay and branching from a recorded prefix |
| P1 | `p1_census.sh`, `p1_label.py`, `p1_summarize.py`, `p1_render.py`, `build_results_tree.py` | Failure census, dense per-step labels, videos, categorised results tree |
| CMP / IMG | `cmp_batch.sh`, `img_census.sh`, `render_sbs.py`, `imagine_episode.py` | FACT on OpenWAM scenes; imagination recorded live; real-vs-imagined videos |
| self-sampling | `mug_failure_onset.py`, `onset_timing_codex.py`, `branch_driver_codex.py`, `run_cell.sh`, `ss_pipeline.sh` | hanging_mug failure-onset detection; multi-seed branching from before / after the failure |

Protocol notes: instruction wording is seeded with the scene seed (upstream draws it with an unseeded RNG); formal runs use the
deployment server config (prefix cache on, action-only). See `docs/FACT_G0_REPORT_CLAUDE.md` and `docs/FACT_PROBE_PLAN_CONSENSUS_V1.md`.
Paths in the launch scripts are those of the original lab machine.
