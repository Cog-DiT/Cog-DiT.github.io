"""
Instruct:
Given good_examples, can you look up its corresponding evaluation data, and then concatenate reference, driving gear, and ground truth videos in a row and output stacked video?
Please update the code to do that.
[Important] please leave this comment. 

python compile_video.py
"""

import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib import cm
from tqdm import tqdm

sys.path.append("./../../")
import stack_videos
import concurrent.futures
import uuid

# Handle MoviePy for generating the white spacer video if needed
try:
    from moviepy.editor import ColorClip
except ImportError:
    from moviepy.video.VideoClip import ColorClip

# Visualizer borrowed from reference code
try:
    from moviepy.editor import ImageSequenceClip
except ImportError:
    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

#################### Good examples, Do NOT change the examples ##############################
good_examples = ["/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_10_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed160GeneralGraph_Depth160_From150_LR3e6_35400_SKIPLOW_MotionHighFixed160eralGraphDepth160From150LR3e6_35400_shift1_1.0_steps1_step32b/results/0_loop_0_modality_0.gif",
                 "/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed160GeneralGraph_Depth160_From150_LR3e6_35400_SKIPLOW_MotionHighFixed160eralGraphDepth160From150LR3e6_35400_shift1_1.0_steps1_step32b/results/6_loop_0_modality_0.gif",
                 "/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_40_LineDepth40_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed160GeneralGraph_Depth160_From150_LR3e6_35400_SKIPLOW_MotionHighFixed160eralGraphDepth160From150LR3e6_35400_shift1_1.0_steps1_step32b/results/0_loop_0_modality_0.gif",
                 "/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_50_MinRad16/Gear_Motion_Normalize_HighNoise_GearFixed160GeneralGraph_Depth160_From150_LR3e6_32000_SKIPLOW_MotionHighFixed160eralGraphDepth160From150LR3e6_32000_shift1_1.0_step32b/results/1_loop_0_modality_0.gif",
                 "/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_60_MinRad16/Gear_Motion_Normalize_HighNoise_GearFixed160GeneralGraph_Depth160_From150_LR3e6_32000_SKIPLOW_MotionHighFixed160eralGraphDepth160From150LR3e6_32000_shift1_1.0_step32b/results/9_loop_0_modality_0.gif",
]
#################################################################


examples = []
base_path = "/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20/Gear_Motion_Normalize_HighNoise_18500_MotionLow_18500_shift1_1.0_step32b/"
for g in good_examples:
    example = [
        ("First Frame (Condition)", os.path.join(base_path, "vis", f"{g}_loop_0_input_modality_0_reference.png")),
        ("Driving Gear (Condition)", os.path.join(base_path, "vis", f"{g}_loop_0_input_modality_0.mp4")),
        #/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20/Gear_Motion_Normalize_HighNoise_18500_MotionLow_18500_shift1_1.0_step32b/parsed/46_loop_0_modality_0/normalized_coordinate_gear_overlay.mp4
        ("Ground-Truth (output)", os.path.join(base_path, "parsed", f"{g}_loop_0_modality_0", "normalized_coordinate_gear_overlay.mp4"))
    ]
    examples.append([example])



################### Do not modify ###############################
"""
examples = [
                [[
                    ("First Frame (Condition)", "./0.png"),
                    ("Veo 3.1", "./0_veo31.mp4"),
                    ("Ray3.14", "./0_ray314.mp4")
                ]],       
            ]
"""
########################################################################################

def get_white_video(output_path, width=832, height=480, duration=1.0, fps=15):
    """Generates a white video to be used as padding."""
    if os.path.exists(output_path):
        return output_path
    
    try:
        clip = ColorClip(size=(width, height), color=(255, 255, 255), duration=duration)
        clip.write_videofile(output_path, codec="libx264", fps=fps, audio=False, logger=None)
        return output_path
    except Exception as e:
        print(f"Failed to create white video: {e}")
        return None

def visualize(grid_inputs, output_path):
    if not grid_inputs:
        return None

    # Use Source Video for FPS/Duration, but FORCE Width/Height for visualizer
    fps = 15
        
    # FORCE RESOLUTION FOR TRACKS
    w, h = 832, 480

    # --- Step 5: Padding ---
    grid_cols = 2

    # --- Step 6: Stack Videos ---
    try:
        # --- NEW CODE: Define borders (RGB format) ---
        border_cfg = {
            "First Frame (Condition)": (0, 0, 255),      # Blue border
            "Driving Gear (Condition)": (0, 0, 255),   # Red border
            "Ground-Truth (output)": (255, 0, 0)    # Red border
        }
        
        # Pass the border_colors argument to the stacker
        stack_videos.stack_videos(grid_inputs, output_path, border_colors=border_cfg)
        # ---------------------------------------------
        
        return output_path
    except Exception as e:
        print(f"Error in stack_videos: {e}")
        return None

if __name__ == "__main__":
    output_dir = "./../../video/Non-autoregressive Simulation/"
    os.makedirs(output_dir, exist_ok=True)

    for idx, example in tqdm(enumerate(examples), desc="Processing Examples"):
        visualize(example, output_path = os.path.join(output_dir, f"{idx}.mp4"))