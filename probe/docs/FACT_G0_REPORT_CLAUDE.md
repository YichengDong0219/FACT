# FACT G0 验收报告（Claude，2026-10-27）

背景：Codex 额度用尽（10-26 23:20），用户指示 Claude 收束结论、自行执行。本报告按共识方案 v1（[FACT_PROBE_PLAN_CONSENSUS_V1.md](FACT_PROBE_PLAN_CONSENSUS_V1.md)）G0 规则判定。**结论：G0 通过（动作重放分支方式），附三项约束。** 原件：[evidence/fact_G0_claude/](evidence/fact_G0_claude/)。

## 1. 实现

| 文件 | 作者 | 说明 |
|---|---|---|
| `fact_probe/inference_server_probe.py` | Codex（R91 生成，源 SHA 4b824966） | 显式 seed 入口，argmin 逻辑不变 |
| `client_adapter.py`、`seed_plan.py`、`probe_request.py` | Codex | 客户端显式 seed；R95 修复 P5 后经 Claude 验收 |
| `g0_driver.py` | Claude | rollout / replay / branch 三模式；SAPIEN 3 状态捕获 |
| `g0_model_check.py` | Claude | 模型侧数值对照 |
| `g0_compare.py` | Claude | 按共识阈值做离线比较，阈值不调 |

Codex 未完成的 `replay_adapter.capture_physics` 在 SAPIEN 3.0.0b1 上不可用（`Entity` 没有 `get_velocity`，articulation 没有 `get_drive_target`），已由 `g0_driver.capture` 替代。捕获内容：全部 actor 的位姿和刚体速度、articulation 的根位姿、qpos、qvel、逐关节 drive target 与 drive velocity target、夹爪值、动作步数、eval/check success、numpy 与 Python 随机状态的摘要。

## 2. 发现的问题与协议修正

**指令随机性**：RoboTwin 的 `generate_episode_descriptions` 用**从未设种子的 Python `random`** 抽取指令措辞，同一场景在不同进程中指令不同，模型因此出不同动作。
- 首轮 R1/R1b 动作从第 0 步就不同；同 seed 的服务器请求 seed 一致，但指令不同。
- 修正：抽取指令前执行 `random.seed(env_seed)`。replay 和 branch 模式强制使用源 rollout 的指令，并在不一致时报错。
- 这是对官方评测的偏离：官方每次运行指令措辞随机。本项目改为「措辞按场景固定」，所有下游结果都按这一协议解释。
- 修正前的 R 系列结果保留为问题证据。

## 3. 分支验收结果（server 变体 A：prefix cache 开、只返回动作，即部署配置）

| 任务 | 结局 | 同 seed 闭环两次 | 无模型重放 | 分支点（重放到 t 后交给模型） |
|---|---|---|---|---|
| hanging_mug，seed 100000 | **自然失败**（900 步耗尽） | 900 步动作逐位相同，20 个边界误差为 0 | 20 个边界误差为 0 | 96、192、288 三点均逐位复现原后续，终局一致 |
| place_empty_cup，seed 100000 | 成功（150 步） | 逐位相同，5 个边界误差为 0 | 误差为 0 | 48、96、144 三点均逐位复现 |

- 所有状态量的最大差：位置、速度、qpos、qvel、drive target、夹爪均为 **0**；旋转为 5e-8（四元数归一化的数值噪声）。均远低于共识阈值。
- 合计 2 个任务、6 个内部分支点加初始态，覆盖初始、搬运与接触阶段，以及成功和失败两种终局；多 chunk 后续与官方终局判定一致。
- **快照方式**未尝试：重放方式已通过，且 SAPIEN 没有现成的完整快照接口。后续分支一律用「同 seed 场景 + 重放已执行动作前缀」。

## 4. 模型侧数值对照（同一真实观测）

| 检查 | A：cache 开 | B：cache 关 | C：cache 关 + 返回视频 |
|---|---|---|---|
| 同 seed 两次 N=1 | 逐位相同 | 逐位相同 | 逐位相同 |
| 不同 seed 的动作差 | 0.074 | 0.074 | 0.074 |
| 池中第 3 个候选 vs 同 seed 单独 N=1 | **不逐位相同**，最大差 0.013 | 同左 | 同左 |
| 8 候选两两平均最大差 | 0.072 | 0.071 | 0.071 |

- **B 与 C**：动作完全相同（N=1 和 8 个候选都逐位相同），说明返回视频不改变动作。但 **value 会变**（例如 B 为 [0.948, …, 0.954, …]，C 为 [0.951, …, 0.957, …]），value 的计算与是否生成视频耦合。
- **A 与 B**：动作最大差 0.008（N=1）和 0.013（候选池）。prefix cache 改变了数值路径，因此正式实验固定使用 A。
- **value 分辨率粗**：8 个候选的 raw value 都在 0.948–0.969 之间，其中 5 个恰好都是 0.951171875（bf16 精度）。对 8 个候选排序时并列很多，这是 P3 排序分析的风险，需要报告并列率。

## 5. 对后续阶段的约束

1. **分支**：从同 seed 场景重放已执行动作前缀，再交给模型，延续原决策编号的 continuation seed。指令按场景固定。
2. **P3 候选**：必须执行保存下来的 N=8 候选池原动作，不能用单独 N=1 重新生成（批处理差 0.013，约为候选间差的 18%）。value 排序须报告并列情况。排序实验仍为 No-Go，直到发布权重的语义确认，这一条不变。
3. **配置固定**：server 变体 A（prefix cache 开、只返回动作）。value 只在该配置下解释。

## 6. 资源

G0 共约 **1.1 GPU 小时**（仿真 1703 s；模型服务各次运行 2180 s），上限 8。未触碰他人进程（GPU3 为 liwenqi 所用，未使用）。

## 7. 状态

G0 已通过。P1 失败普查已启动（10-27 01:4x）：
- 任务：hanging_mug、turn_switch、move_stapler_pad（论文 clean 成功率分别为 36、61–66、54–62），demo_clean 各 20 个有效 episode；
- adjust_bottle 4 个健全性 episode；
- 单客户端串行执行，server 变体 A。
