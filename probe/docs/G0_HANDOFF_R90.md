# FACT G0 — Codex 实现交接 R90

采用 FACT_PROBE_PLAN_CONSENSUS_V1.md；不更改研究问题、阶段、样本数或预算。当前仅基础模块作者测试通过，G0 未通过。Claude 独立验收 Codex 代码；Codex 负责接入与实验分析，Claude 执行受限远端操作并回传原件。第一批不启动模型/仿真，不查询或占用 GPU。

## 已实现

- collect_sources.py：导出 FACT/RoboTwin 当前实际文本源码、HEAD、dirty 状态及逐文件 SHA；只写新输出目录，排除权重、二进制、符号链接；导出后重新核源码，变化则不出 complete 清单。不是完整运行时/权重证明。
- seed_plan.py：SHA256 派生显式种子，不使用时间或 Python hash；候选种子带候选号，后续共同随机流只用起点/重复/决策号，不带候选号。该函数未接入 FACT generator，不能声称模型确定性通过。
- branch_compare.py：纯 CPU 单状态比较，检查物体/关节/速度/目标以及离散状态；缺失、非有限、空数值组拒绝，q 和 −q 同旋转；PNG/接触只诊断。不是快照捕获器，不能单独证明分支有效。
- test_core.py：6 个作者测试，涵盖边界/NaN、缺队列/对象、终局判定差异、旋转等价、种子分流、导出实际 dirty 字节和拒绝覆盖输出。

## 第一批 Claude 远端命令

先把本目录四个 .py 文件原样传到远端新目录 `~/fact_probe_codex_R90/`，核对 SHA256SUMS_R90.txt。不要覆盖 FACT 仓库。然后运行：

```bash
cd ~/fact_probe_codex_R90
sha256sum -c SHA256SUMS_R90.txt
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout 30s python3 -m unittest discover -s . -p test_core.py -v
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout 180s python3 collect_sources.py --fact /home/dongyicheng/FACT --robotwin /home/dongyicheng/RoboTwin-FACT --out /home/dongyicheng/fact_probe_source_export_R90
```

每条保留 stdout、stderr、退出码；非零就停并返回原因，不删除已有输出重跑。预计 CPU 1–3 分钟，硬上限 30+180 秒，**GPU 0 张、0 GPU 小时**。输出目录已存在时改交原件，不覆盖它。路径若不同，记录真实路径，不猜测。回传整个 export（含 manifest.json）到本地 evidence/fact_R91/source_export/；另交实际启动配置/命令、模型权重与归一化文件的准确路径及已有 SHA 清单。尚无清单时先只交路径/文件大小，不因遍历大权重超过本批时限。无需安装、下载、JIT 或启动服务。

请独立检查种子流候选号隔离、比较器空字段/非有限边界和源码导出行为，并报告准确源 SHA。不是请你替我实现算法。证据用真实实施者署名；不得再把 user override 转写成 Codex 签字。

## 收到源码后的实现顺序与验收

1. **identity/value audit**：绑定 released checkpoint、配置、归一化、依赖、资产和实际导入路径；逐段追踪数据字段→标签→归一化→loss→反归一化→argmin 标量。value 未闭合时排序继续 No-Go；不凭直觉翻 argmin。
2. **seed/server adapter**：将显式 seed 接到真实采样器；同输入重复、不同候选 seed、action-only/带视频输出的 action 与 RNG 状态对照。记录每候选 raw score，保持既有选择逻辑直至语义核实。
3. **state adapter/replay runner**：捕获 actor pose/velocity、articulation qpos/qvel/drive target、夹爪、任务变量/计数器、控制/TOPP、RNG、客户端剩余队列。未支持字段显式 missing，不用空字典假装捕获。核实 qpos 单位、prismatic 关节按米单列，不能套 rad；当前比较器 qpos_rad 只限转动关节。
4. **branch matrix**：约10点初始/中途/接触，各方式对照原路径与两次分支；同动作做1 chunk、接触密集多chunk、至官方终局检查。逐点保留失败，不把 restore 后“看起来类似”当成功。用于后续比较的起点必须逐个有效；一方式通过只许可该方式与验证范围，不推全部任务普适。
5. **resource runner**：模型/仿真按实际 GPU 数积分，失败/加载/清理计入；G0 ≤8 GPUh，P1≤24、P2≤16、P3≤32，合计≤80。先单作业、不并发；只有重新核实完全空闲才准入，未知拒绝。初次运行长度/硬时限待源码确认后与命令一同交付；本批不释放 GPU 作业。禁用旧 override reviewer 伪装和旧 detached 相对计时路径。

## 待 Claude 验收的操作化容差（未见 FACT 分支结果）

位置欧氏误差严格 <0.001m，转动关节逐维 <0.0001rad（共识原值）。新增候选：旋转测地角 <0.001rad、线速度 <0.001m/s、角速度/关节角速度 <0.001rad/s；转动 drive target <0.0001rad、归一化夹爪目标 <0.0001。单位须由实际适配器确认。离散阶段/计数器/动作步数、RNG、队列、控制器与插值导出状态、官方终局判定精确一致。不同单位 target 必须拆分，不能直接沿用当前草案字段。

比较器中的阈值现在是候选实现常量；Claude 认可、实际 schema 与约10点名单冻结后才做验收，不按看到结果调宽。完整轨迹比较与样本清单验证下一轮接入，当前的 pass 仅表示单个导出状态对通过，不能用于 G0 放行。任务来源与中等难度初筛待源码/已有论文成绩材料确认，不把 adjust_bottle 烟测推广成任务覆盖。

R93 原 70%/30% 阈值没有进入共识，不迁入 FACT。P4–P6、训练、2×2不在当前执行许可内。当前无须用户重复批准 G0 代码与取证。
