# FACT G0 下一批交接 R91

Codex已修比较器P1/P2和种子P5，9作者测试通过。请Claude按新SHA独立复核，特别测试捕获空队列与缺失队列、未知qpos_m、非有限、候选repeat≠0；勿继续使用旧测试夹具空字典。EXACT字段现在必须为{captured:true,value:...}，计数器非负int、success为bool、队列list（允许真实捕获的[]），其余非空JSON对象。该封装是捕获声明，不代替审查真实适配器；qpos_m当前会拒绝，待移动关节schema明确后支持。

第一步将本目录全部.py和SHA256SUMS_R91.txt放入远端新目录 `~/fact_probe_codex_R91`。不改FACT仓库。CPU，无GPU，测试上限30秒：

```bash
cd ~/fact_probe_codex_R91
sha256sum -c SHA256SUMS_R91.txt
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout 30s python3 -m unittest discover -s . -p 'test_*.py' -v
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout 30s python3 build_server_probe.py --source /home/dongyicheng/FACT/scripts/inference_server.py --sha 4b824966de4663d9610495f00e514d6a6573eba3efc9c74c870c6200373bca3d --out /home/dongyicheng/fact_probe_server_R91
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 collect_metadata.py --fact /home/dongyicheng/FACT --out /home/dongyicheng/fact_probe_metadata_R91
```

单条非零即停并回传原件，不覆盖输出。实际源码集成单测在远端若缺本地证据相对路径会skip，必须如实报告；独立build命令在真实源SHA下补上生产源码生成检查，不冒称运行server。以上总硬上限180秒（外加小SHA检查），预计1–3分钟；不import模型/CUDA、不JIT、不装包，GPU0张。生成入口不能现在启动；缺完整客户端seed请求、权重身份和资源runner。

回传四条命令stdout/stderr/rc、新server源码SHA、metadata完整目录（含实际norm_stats/模型config/权重文件路径大小/已有下载校验日志）。collect_metadata不重新hash大权重；日志若缺或超过5MB不导出，请报告状态，不以旧下载日志替代启动前实际文件身份。模型来源/对应训练配置若存在，请给准确文件；没有则标unknown，不能用源码猜测发布权重训练史。

接下来Codex据stats/实际配置接完整client请求、动作重放/捕获以及有界GPU测试runner；Claude独立验收后才发首个GPU命令。G0≤8 GPUh，累计G0–P3≤80 GPUh，不修改阈值/预算。远端GPU是否空闲在真正需要GPU时再查，本批不需要查询。原OpenWAM执行器不复用，不改watcher或其他用户进程。
