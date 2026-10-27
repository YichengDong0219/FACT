import os,sys
from pathlib import Path
import yaml
sys.path.insert(0,"/home/dongyicheng/FACT")
import local.robotwin_compat
sim=Path("/home/dongyicheng/RoboTwin-FACT")
sys.path.insert(0,str(sim));os.chdir(sim)
from envs.adjust_bottle import adjust_bottle
from envs.utils.create_actor import UnStableError
args=yaml.safe_load((sim/"task_config/demo_clean.yml").read_text())
robot=sim/"assets/embodiments/aloha-agilex"
args.update(task_name="adjust_bottle",task_config="demo_clean",ckpt_setting="fact_preflight",policy_name="evaluation.robotwin.model2robotwin_interface",eval_mode=True,left_robot_file=str(robot),right_robot_file=str(robot),dual_arm_embodied=True,eval_video_log=False)
emb=yaml.safe_load((robot/"config.yml").read_text())
args.update(left_embodiment_config=emb,right_embodiment_config=emb)
cam=yaml.safe_load((sim/"task_config/_camera_config.yml").read_text())["D435"]
args.update(head_camera_h=cam["h"],head_camera_w=cam["w"])
env=adjust_bottle()
for seed in range(100000,100010):
 try:
  env.setup_demo(now_ep_num=0,seed=seed,is_test=True,**args)
  print("STABLE_SEED",seed,flush=True);break
 except UnStableError:
  env.close_env()
else:raise RuntimeError("No stable candidate")
obs=env.get_obs();print("TASK_SETUP_PASS",list(obs),flush=True)
info=env.play_once();success=env.check_success()
print("EXPERT_PREFLIGHT_SUCCESS",success,info,flush=True)
env.close_env()
if not success:raise RuntimeError("Expert failed")
