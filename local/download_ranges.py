import os,json,time,hashlib,concurrent.futures,threading
from pathlib import Path
import requests
from huggingface_hub import HfApi, hf_hub_download
ROOT=Path("/home/dongyicheng/FACT/models")
REPOS=[("Bariona/fact-wam","887f66bc0be860ede339bb2843fb3c79a8553278"),("Wan-AI/Wan2.2-TI2V-5B-Diffusers","b8fff7315c768468a5333511427288870b2e9635")]
CHUNK=16*1024*1024
WORKERS=48
manifest=[]
for repo,rev in REPOS:
 info=HfApi().model_info(repo,revision=rev,files_metadata=True)
 files=sorted(info.siblings,key=lambda f:(f.rfilename.startswith("transformer/") if repo.startswith("Wan") else False,f.rfilename))
 for f in files:
  if repo.startswith("Wan") and f.rfilename.startswith("transformer/") and f.rfilename != "transformer/config.json": continue
  target=ROOT/repo.split("/")[-1]/f.rfilename
  sha=f.lfs.sha256 if f.lfs else None
  manifest.append({"repo":repo,"revision":rev,"file":f.rfilename,"size":f.size,"sha256":sha})
  if f.size<10*1024*1024:
   hf_hub_download(repo,f.rfilename,revision=rev,local_dir=ROOT/repo.split("/")[-1]);continue
  if target.exists() and target.stat().st_size==f.size:
   if not sha or hashlib.file_digest(target.open("rb"),"sha256").hexdigest()==sha:
    print("VERIFIED existing",str(target),flush=True);continue
  target.parent.mkdir(parents=True,exist_ok=True)
  part=target.with_name(target.name+".ranged")
  donepath=target.with_name(target.name+".chunks.json")
  done=set(json.loads(donepath.read_text())) if donepath.exists() and part.exists() else set()
  fd=os.open(part,os.O_CREAT|os.O_RDWR,0o644);os.ftruncate(fd,f.size)
  lock=threading.Lock()
  url="https://huggingface.co/"+repo+"/resolve/"+rev+"/"+f.rfilename
  redirect=requests.get(url,allow_redirects=False,timeout=60)
  redirect.raise_for_status();direct=redirect.headers.get("Location",url)
  count=(f.size+CHUNK-1)//CHUNK
  starttime=time.time();initial=len(done)
  print("START",repo,f.rfilename,f.size,"chunks",count,"done",len(done),flush=True)
  def fetch(i):
   if i in done:return
   start=i*CHUNK;end=min(f.size,start+CHUNK)-1
   for attempt in range(12):
    try:
     with requests.get(direct,headers={"Range":f"bytes={start}-{end}"},stream=True,timeout=(30,90)) as r:
      r.raise_for_status()
      expected=f"bytes {start}-{end}/{f.size}"
      if r.status_code!=206 or r.headers.get("Content-Range")!=expected:raise RuntimeError("bad range "+str(r.status_code)+" "+str(r.headers.get("Content-Range")))
      pos=start
      for block in r.iter_content(1024*1024):
       os.pwrite(fd,block,pos);pos+=len(block)
      if pos!=end+1:raise RuntimeError("short range")
     with lock:
      done.add(i)
      temp=donepath.with_suffix(".tmp");temp.write_text(json.dumps(sorted(done)));os.replace(temp,donepath)
      if len(done)%16==0 or len(done)==count:print("PROGRESS",f.rfilename,len(done),count,"MiB/s",round((len(done)-initial)*CHUNK/1024**2/max(1,time.time()-starttime),2),flush=True)
     return
    except Exception as e:
     print("RETRY",i,attempt,type(e).__name__,str(e)[:160],flush=True)
     if attempt==11:raise
     time.sleep(min(30,2+attempt*2))
  try:
   with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:list(pool.map(fetch,range(count)))
  finally:os.close(fd)
  actual=hashlib.file_digest(part.open("rb"),"sha256").hexdigest()
  if sha and actual!=sha:raise RuntimeError("SHA mismatch "+str(target))
  os.replace(part,target);donepath.unlink()
  print("VERIFIED",str(target),actual,flush=True)
Path("/home/dongyicheng/FACT/setup_logs/weights_manifest.json").write_text(json.dumps(manifest,indent=2))
print("ALL_DOWNLOADS_VERIFIED",flush=True)
