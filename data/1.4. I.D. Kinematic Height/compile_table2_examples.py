"""Build the Table 2 O.O.D.-general-tree examples shown in section 1.4.

The source run is deliberately fixed here because the evaluation directory also
contains results from models trained on general trees. Table 2 uses the
``GearFixed110LineGraph`` checkpoint (linear-chain training) evaluated on
``Motion_10_MinRad20`` (10-gear general trees).

Run from any directory with::

    python "data/1.4. I.D. Kinematic Height/compile_table2_examples.py"
"""

from pathlib import Path
import sys
import tempfile

import cv2


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import stack_videos


EVAL_DATA = Path("/scratch/shared/beegfs/koichi/Gear_Eval/Motion_10_MinRad20")
RESULT_ROOT = Path(
    "/work/koichi/Gear/gear_gen_angle_rad_con_auto/eval_results/"
    "Motion_10_MinRad20/"
    "Gear_Motion_Normalize_HighNoise_GearFixed110LineGraph_Depth110_12000_"
    "SKIPLOW_MotionHighFixed110LineGraphDepth110_12000_shift1_1.0_step32b"
)
OUTPUT_DIR = REPO_ROOT / "video" / "1.4. I.D. Kinematic Height"

# Lowest E_rmd successful samples from the verified Table 2 run. Each sample's
# metadata has a repeated parent_id, which proves that its tree is non-linear.
SAMPLE_IDS = (1, 61, 68, 34, 63)
OUTPUT_OFFSET = 5


def extract_first_frame(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(source))
    try:
        ok, frame = capture.read()
    finally:
        capture.release()
    if not ok or not cv2.imwrite(str(destination), frame):
        raise RuntimeError(f"Could not extract first frame from {source}")
    return destination


def inputs_for(sample_id: int, reference_cache: Path):
    sample = EVAL_DATA / f"sample_{sample_id:06d}" / "videos"
    result_name = f"{sample_id}_loop_0_modality_0.mp4"
    reference = extract_first_frame(
        sample / "all_normalized_coordinate.mp4",
        reference_cache / f"table2_sample_{sample_id:06d}.png",
    )
    inputs = [
        ("First Frame (Condition)", reference),
        ("Driving Gear (Condition)", sample / "root_normalized_coordinate.mp4"),
        ("Ground Truth", sample / "all_normalized_coordinate.mp4"),
        ("Generated", RESULT_ROOT / "results" / result_name),
    ]
    missing = [str(path) for _, path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing Table 2 media: " + ", ".join(missing))
    return [(label, str(path)) for label, path in inputs]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    borders = {
        "First Frame (Condition)": (0, 0, 255),
        "Driving Gear (Condition)": (0, 0, 255),
        "Ground Truth": (0, 255, 0),
        "Generated": (255, 0, 0),
    }
    with tempfile.TemporaryDirectory(prefix="cogdit-table2-") as cache:
        reference_cache = Path(cache)
        for index, sample_id in enumerate(SAMPLE_IDS, start=OUTPUT_OFFSET):
            stack_videos.stack_videos(
                [inputs_for(sample_id, reference_cache)],
                str(OUTPUT_DIR / f"{index}.mp4"),
                border_colors=borders,
                target_fps=15,
            )


if __name__ == "__main__":
    main()
