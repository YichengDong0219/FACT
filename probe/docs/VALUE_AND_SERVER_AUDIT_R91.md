# FACT G0 源码审计 R91

范围是 R95 回传的实际源码（1576个文件SHA核对通过），并非发布权重训练来源的证明。源码引用均相对于 evidence/fact_R91/source_export/FACT。

## value 链路

1. `fact_datasets/datasets/lerobot_dataset.py:633–647`：future_state_index=min(当前帧+实际action索引数量,L−1)；failure清单提供failure_episode、failure_active_from_frame；failure_active按当前帧达到onset判定，并非预测未来是否失败。
2. `world_action_model/transformers/wa_transforms_lerobot.py:494–511`：L>1时raw=(L−future_state_index−1)/(L−1)，否则0；failure_active加value_penalty_scale（构造默认1）；按value min/max映射[-1,1]并裁剪。它是轨迹相对剩余进度带失败惩罚，不是任务成功概率。
3. 同文件513：failure_episode使action_loss_mask=0；`trainer/wa_casual_trainer.py:717,849–853`：value目标为noise−normalized value，value损失为flow预测MSE且不使用action mask。不能把metadata里的validation action_mse同名value混进标签解释。
4. `pipeline/utils.py:108–112`：推理value反归一化=((v+1)/2)*(max−min+1e−8)+min。`scripts/inference_server.py:347–350,424–428`：排序用反归一化且未裁剪raw scalar，非有限换+inf，然后argmin；输出value另行裁剪[-1,1]。评估必须保存values_per_sample，不能用展示value反推排序。
5. `scripts/compute_norm_stats.py:119–130`：默认min实际为−1，max2；注释提到gt_raw∈[0,1]不等于文件min为0。必须取发布checkpoint同目录真实norm_stats_delta.json确认，不能用注释代替数据。

**代码内部低分优先有依据，不翻转argmin。发布权重是否按该标签/惩罚与训练集训练仍未闭合**：需要准确权重身份、实际stats和对应训练配置/来源。源码含failure mask不证明发布模型已接受失败训练。排序实验仍No-Go；保留所有非有限候选，不能因原实现全非有限时argmin返回0而将其称为有效选择。

## ENABLE_SAMPLE 与采样

`evaluation/robotwin/launch_client.sh:98`传enable_sample；接口563使用_as_bool，332仅enable_sample且N>1才发送best_of_N。因此当前配置0/N4实际请求省略N，服务端297默认N1。原N1 `_run_pipe(None)`使用全局随机流；原N>1以time_ns生成base seed。

已实现独立probe server生成器，源SHA固定为 `4b824966de4663d9610495f00e514d6a6573eba3efc9c74c870c6200373bca3d`。不改导出证据或上游源码。新入口要求probe_seeds，每候选一个uint63显式seed、N1亦使用torch.Generator；N>1保存完整物理动作候选池与原raw values、selected_index，原argmin不变。`attach_probe_request`明确填写N，绕过旧enable_sample缺省行为；尚未接入正式RoboTwin客户端，默认客户端对新server会缺seed报错，不能拿旧baseline命令直接启动。

K=3复用同一保存的首chunk候选池。candidate/selection重复号只能0，continuation随repeat变化，并按起点/决策号共用。重复生成候选不代替复用，部署时还须绑定候选动作SHA。

`pipeline/wa_pipeline.py:312–318`同generator依次抽video/action/future_state/value噪声；553后stage1只生成action，708后stage2生成future_state/value/可选video。**action_only切换还会影响prefix cache是否可用**（572）；不能仅凭“两阶段”就断言动作逐位相同。G0需同输入同seed，在固定cache关闭下比较action-only/带视频，再单列默认cache模式的差异。当前仅静态编译/结构与wire协议测试，不声称模型数值等价。

## 状态分支仍待完成

RoboTwin-FACT `_base_task.py:1479` take_action默认qpos，1538后有TOPP与双臂控制局部变量；没有在本轮找到可直接调用、覆盖Python控制状态的既有snapshot接口。先实现完整动作重放适配器与边界捕获，再评估scene物理快照的Python状态补全；不得把仅scene.pack视为完整恢复。当前比较器只接收标准JSON状态，修复不是G0分支已通过。
