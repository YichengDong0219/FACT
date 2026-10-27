from huggingface_hub import snapshot_download
from pathlib import Path
import json,time
root=Path("/home/dongyicheng/FACT")
repos=[("Wan-AI/Wan2.2-TI2V-5B-Diffusers","b8fff7315c768468a5333511427288870b2e9635"),("Bariona/fact-wam","887f66bc0be860ede339bb2843fb3c79a8553278")]
for repo,rev in repos:
 for attempt in range(10):
  try:
   print("Downloading",repo,rev,flush=True)
   snapshot_download(repo_id=repo,revision=rev,local_dir=root/"models"/repo.split("/")[-1],max_workers=4)
   break
  except Exception as e:
   print(type(e).__name__,str(e),flush=True)
   if attempt==9:raise
   time.sleep(10)
(root/"setup_logs/download_complete.json").write_text(json.dumps(dict(repos),indent=2))
