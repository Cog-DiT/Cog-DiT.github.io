"""
Instruct:
Given good_examples, can you look up its corresponding evaluation data, and then concatenate reference, driving gear, and ground truth videos in a row and output stacked video?
Please update the code to do that.
[Important] please leave this comment. 

python compile_video.py
"""

import os
import re
import sys
from pathlib import Path
import cv2
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import stack_videos
#################### Good examples, Do NOT change the examples ##############################
good_examples = ["/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20_LineDepth20_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed120GeneralGraph_Depth120_29000_SKIPLOW_MotionHighFixed120eralGraphDepth120_29000_shift1_1.0_steps10_step32b/results/2_loop_0_modality_0.gif",
"/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20_LineDepth20_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed120GeneralGraph_Depth120_29000_SKIPLOW_MotionHighFixed120eralGraphDepth120_29000_shift1_1.0_steps10_step32b/results/3_loop_0_modality_0.gif",
"/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed120LineGraph_Depth120_12000_SKIPLOW_MotionHighFixed120LineGraphDepth120_12000_shift1_1.0_steps1_step32b/results/4_loop_0_modality_0.gif",
"/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed120LineGraph_Depth120_12000_SKIPLOW_MotionHighFixed120LineGraphDepth120_12000_shift1_1.0_steps1_step32b/results/5_loop_0_modality_0.gif",
"/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed120LineGraph_Depth120_12000_SKIPLOW_MotionHighFixed120LineGraphDepth120_12000_shift1_1.0_steps1_step32b/results/6_loop_0_modality_0.gif",
"/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/Motion_20_MinRad20/Gear_Motion_Normalize_HighNoise_GearFixed120LineGraph_Depth120_12000_SKIPLOW_MotionHighFixed120LineGraphDepth120_12000_shift1_1.0_steps1_step32b/results/7_loop_0_modality_0.gif",
]
#################################################################


EVAL_DATA_ROOT = Path(
    os.environ.get("GEAR_EVAL_ROOT", "/scratch/shared/beegfs/koichi/Gear_Eval")
)
RESULT_PATTERN = re.compile(r"^(?P<sample>\d+)_loop_(?P<loop>\d+)_modality_(?P<modality>\d+)\Z")

def _first_existing(paths):
    """Return the first existing path from *paths*, or ``None``."""
    return next((Path(path) for path in paths if Path(path).is_file()), None)

def _result_info(result_path):
    """Extract the dataset/sample identity encoded by a result GIF path."""
    result_path = Path(result_path)
    match = RESULT_PATTERN.fullmatch(result_path.stem)
    if match is None or result_path.parent.name != "results":
        raise ValueError(
            "Expected a result path like <experiment>/results/7_loop_0_modality_0.gif: "
            f"{result_path}"
        )
    experiment_root = result_path.parent.parent
    return {
        "result_path": result_path,
        "experiment_root": experiment_root,
        "dataset_name": experiment_root.parent.name,
        "sample_id": int(match.group("sample")),
        "loop": int(match.group("loop")),
        "modality": int(match.group("modality")),
    }

def _extract_reference_frame(video_path, output_path):
    """Extract the first frame of a source video for the static reference cell."""
    if output_path.exists():
        return output_path
    capture = cv2.VideoCapture(str(video_path))
    try:
        ok, frame = capture.read()
    finally:
        capture.release()
    if not ok:
        raise ValueError(f"Could not read a reference frame from {video_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), frame):
        raise ValueError(f"Could not write extracted reference frame to {output_path}")
    return output_path

def _resolve_example(result_path, eval_data_root, reference_cache_dir):
    """Resolve one result GIF to its source-condition and ground-truth files."""
    info = _result_info(result_path)
    experiment_root = info["experiment_root"]
    sample_id = info["sample_id"]
    loop = info["loop"]
    dataset_name = info["dataset_name"]
    sample_name = f"sample_{sample_id:06d}"
    videos_root = Path(eval_data_root) / dataset_name / sample_name / "videos"
    vis_dir = experiment_root / "vis"
    vis_prefix = f"{sample_id}_loop_{loop}_input_modality_0"
    reference_video = videos_root / "all_normalized_coordinate.mp4"
    reference_cache_path = reference_cache_dir / f"{dataset_name}_{sample_name}_reference.png"
    reference_path = _first_existing([
        vis_dir / f"{vis_prefix}_reference.png",
        reference_cache_path,
    ])
    if reference_path is None:
        if not reference_video.is_file():
            raise FileNotFoundError(
                f"No reference image or evaluation sample video found for {result_path}. "
                f"Expected {reference_video} or a saved vis reference under {vis_dir}."
            )
        reference_path = _extract_reference_frame(reference_video, reference_cache_path)

    driving_fallback = videos_root / "root_normalized_coordinate.mp4"
    generated_fallback = Path(result_path).with_suffix(".mp4")
    driving_path = _first_existing([vis_dir / f"{vis_prefix}.mp4", driving_fallback])
    generated_path = _first_existing([generated_fallback])

    missing = []
    if driving_path is None:
        missing.append(f"driving condition: {driving_fallback}")
    if generated_path is None:
        missing.append(f"generated video: {generated_fallback}")
    if missing:
        raise FileNotFoundError(
            f"Could not resolve evaluation data for {result_path}: " + "; ".join(missing)
        )

    return [
        ("First Frame (Condition)", str(reference_path)),
        ("Driving Gear (Condition)", str(driving_path)),
        ("Generated", str(generated_path)),
    ]

def build_examples(eval_data_root, reference_cache_dir):
    """Build one horizontal comparison row for each configured good example."""
    return [
        [_resolve_example(result_path, eval_data_root, reference_cache_dir)]
        for result_path in good_examples
    ]



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
            "Generated": (255, 0, 0)    # Red border
        }
        
        # Pass the border_colors argument to the stacker
        stack_videos.stack_videos(grid_inputs, output_path, border_colors=border_cfg)
        # ---------------------------------------------
        
        return output_path
    except Exception as e:
        print(f"Error in stack_videos: {e}")
        return None

if __name__ == "__main__":
    output_dir = REPO_ROOT / "video" / "20-Gear Count"
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_cache_dir = output_dir / ".references"
    examples = build_examples(EVAL_DATA_ROOT, reference_cache_dir)

    for idx, example in tqdm(enumerate(examples), desc="Processing Examples"):
        visualize(example, output_path=str(output_dir / f"{idx}.mp4"))
