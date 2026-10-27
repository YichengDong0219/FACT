"""Compatibility for the existing robotwin environment (Torch 2.4 / Warp 1.13).
Initialize CUDA before SAPIEN; expose Warp's legacy torch interop namespace.
No changes to task dynamics, actions, seeds, scoring, or episode limits.
"""
import types
import torch
if not torch.cuda.is_available():
    raise RuntimeError("RoboTwin CUDA is unavailable")
torch.zeros(1,device="cuda")
import warp as wp
if not hasattr(wp,"torch"):
    names=("from_torch","to_torch","dtype_from_torch","dtype_to_torch","device_from_torch","device_to_torch","stream_from_torch","stream_to_torch")
    wp.torch=types.SimpleNamespace(**{k:getattr(wp,k,None) for k in names})
from curobo.wrap.reacher.motion_gen import MotionGen
