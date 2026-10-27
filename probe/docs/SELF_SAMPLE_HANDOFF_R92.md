# R92：失败前后自采样，第一批交叉验收

本轮合并R96–R98；原始用户授权已核实：3b809cfc-e629-4b34-81b9-c4b42ce897c9（2026-10-27T03:38:46.780Z）同意实验交Codex。额度中断后用户亦授权Claude自跑（3e2a6f75，2026-10-26T15:33:23.033Z）。原研究保留，本实验单独登记；160条是新全程N1换流设计，不是原P3的首chunk候选池实验，也超过原P2 120次设计，作为用户新批准的160条上限变更记录。训练仍不启动。

## 科学定义与冻结候选

- 原onset把a回填10步、b回填最后挂高、c回填静止窗起点。新增onset_timing_codex原样阈值，按首次可检测时间选规则，同步发生优先a/b/c；明确t_onset_retrospective和t_detect。
- pre为严格早于事后起点的48步边界；post为严格晚于首次检测的48步边界。不清空中间队列，不改原前缀。pre组是事后挑选的失败预防机会，不称在线恢复；post才是检测后恢复。
- 从已知14失败按env_seed升序取前10，不按分支表现挑选、不替换。名单与源SHA在SELF_SAMPLE_STARTS_CANDIDATE_R92.json；本轮没有分支结果。全部pre240/288、post336，8路repeat1..8。Claude验收后冻结该准确文件，不因失败/资源/重放差异补样。
- 终局总上限沿用源900步，pre/post剩余预算不同，成效差包含介入时机与剩余步数，不能纯归因为状态优劣。全程改变continuation随机流；不做value排序，不依赖发布训练史闭合。
- 按起点×pre/post报告成功路数/8与any_success@8，路/候选不充当独立起点。10个起点全保留，故障/not_run单列；不看结果加第9路。不得自动启动专家接管或训练。
- IMG 20条为跨cache/视频配置、且部分与P1同场景的复核集，非独立场景留出。先原规则一次评估检出/误报；若据结果修规则，必须记录版本并称开发调整，不能在同IMG上再宣称留出验证通过。额外独立场景采集不自动添加。

## 实现范围

build_branch_driver_codex.py生成独立驱动，不改Claude g0_driver：新增--stream-repeat 0..8；固定root_seed/场景/指令、原决策编号；校验源动作SHA，branch要求max-tries1，禁止专家失败后换seed；到分支边界先精确比较捕获状态与已执行前缀，失败在首个后续模型请求前停止。repeat0只用于原后续复现；正式repeat1..8。生成源SHA及产物见submission_R92.json。

R97四文件状态：client_adapter已由Claude实际沿用；replay_adapter.capture_physics明确废弃（SAPIEN3不兼容），不部署；bounded_run为待Claude验收的单卡前台原型，只供首批label复核，不能管理双流水线服务器；test_adapters有界CPU作者测试通过。完整双流水线调度/视频归档尚未实现，不冒称160条已可一键启动。

## 首个GPU命令（待Claude验收，不在本轮执行）

首批只标注IMG20，无模型、单卡，预计20分钟，硬上限1800秒，最多0.5 GPUh计入本实验16 GPUh。新目录固定 `/home/dongyicheng/fact_selfsample_R92`；输入为现有 `fact_g0_claude/runs/IMG_hanging_mug_demo_clean_00..19.json`。全部代码先复制新code目录并核submission中的SHA，未核不启动。需将Claude的p1_label/g0_driver及其probe依赖原样复制到code，不更改旧目录；PYTHONPATH只指新code与只读原仓库。

在查得完全空闲卡的UUID后运行如下命令（UUID必须用当时实查值替换；此处不是现在执行的许可）：

```bash
python3 /home/dongyicheng/fact_selfsample_R92/code/bounded_run.py \
 --root /home/dongyicheng/fact_selfsample_R92/ledger_label \
 --gpu-uuid GPU-REPLACE-WITH-VERIFIED-UUID --seconds 1800 -- \
 python3 /home/dongyicheng/fact_selfsample_R92/code/label_batch_codex.py \
 --runs /home/dongyicheng/fact_g0_claude/runs \
 --out /home/dongyicheng/fact_selfsample_R92/IMG_labels \
 --code /home/dongyicheng/fact_selfsample_R92/code
```

runner每次启动查UUID、显存≤64MiB、利用率0、无compute PID；未知或占用退出，不等待、不杀他人。前台同主机计时从spawn前开始，20秒清理预留；只终止它创建的session/process group，子脚本不得daemonize。崩溃/清理未知保留active预算，不自动重启。当前ledger保守硬帽8GPUh，只用于此首批，不能用新root重置预算；正式160条需另接16GPUh整批含server加载/空转/清理与已有label耗时总账。

p1_label保留最多3次同seed专家检查（其既有实现），不换场景；每文件记录expert_check_attempts。20条整体1800秒先到停止，不续剩余。label结果必须replay_outcome_matches及final_state_matches为真，否则停止、记缺失，不算检测漏报。首次运行结束服务器数量仍应为0。

## 后续顺序和预算

Claude独立验收时序/名单/换流差量与首批runner后，Codex执行IMG标注并回传。之后验每个冻结起点的前缀一致，先做有限repeat0复现工程检查，再发160条正式运行的精确调度清单；任何新增控制运行、渲染均计16GPUh，不把80总预算当额外16。预计160条2–2.5分钟/条×2张占用≈10.7–13.3GPUh，加label/控制/加载后须按实测重估；预算不够保留缺格，不能承诺全部跑完。两流水线只有四卡都完全空闲才考虑，先单流水线，整批上限先到即停。

当前只交可审查成果，G0“通过”仍为Claude报告的两任务/六点有限重放证据，不升级成所有场景完整状态恢复证明。原始G0/旧P1/IMG结果不混为联合签发研究结果。
