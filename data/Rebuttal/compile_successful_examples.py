"""Build the four-panel CogVideoX-5B rebuttal examples.

Run from any directory with a Python environment containing OpenCV, imageio,
imageio-ffmpeg, NumPy, and Pillow:

    python data/Rebuttal/compile_successful_examples.py
"""

from pathlib import Path
import shutil
import sys
import tempfile

import cv2
import imageio


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import stack_videos


EVAL_DATA = Path(
    "/scratch/shared/beegfs/koichi/Gear_Eval/"
    "Motion_Depth10_Node100_MinRad25_Efficient2"
)
MEDIA_ROOT = REPO_ROOT / "data" / "Rebuttal" / "CogvideoX-5b"
GENERATED_DIR = MEDIA_ROOT / "successful_100_gear"
OUTPUT_DIR = MEDIA_ROOT / "successful_100_gear_comparisons"
# Original sample IDs from CogVideoX5B_1_20_Resize_35500_frames17_noise0.98-1_steps15_step32.
SAMPLE_IDS = (0, 1, 2, 3, 4)
NUM_FRAMES = 17
FPS = 15


def prepare_input(source, destination, reference=None):
    """Keep the same leading frames used by the inference dataset loader."""
    capture = cv2.VideoCapture(str(source))
    try:
        with imageio.get_writer(
            str(destination), fps=FPS, codec="libx264", pixelformat="yuv420p",
            quality=None, ffmpeg_params=["-crf", "0"],
        ) as writer:
            for index in range(NUM_FRAMES):
                ok, frame = capture.read()
                if not ok:
                    raise ValueError(f"Could not read frame {index} from {source}")
                if index == 0 and reference is not None:
                    if not cv2.imwrite(str(reference), frame):
                        raise RuntimeError(f"Could not save {reference}")
                writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    finally:
        capture.release()


def main():
    # Check every source before building any output.
    for index, sample_id in enumerate(SAMPLE_IDS):
        videos = EVAL_DATA / f"sample_{sample_id:06d}" / "videos"
        for source in (
            videos / "all_normalized_coordinate.mp4",
            videos / "root_normalized_coordinate.mp4",
            GENERATED_DIR / f"{index}.mp4",
        ):
            if not source.is_file():
                raise FileNotFoundError(source)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    borders = {
        "First Frame (Condition)": (0, 0, 255),
        "Driving Gear (Condition)": (0, 0, 255),
        "Ground Truth": (0, 255, 0),
        "Generated": (255, 0, 0),
    }
    with tempfile.TemporaryDirectory(prefix="cogdit-rebuttal-") as directory:
        cache = Path(directory)
        for index, sample_id in enumerate(SAMPLE_IDS):
            videos = EVAL_DATA / f"sample_{sample_id:06d}" / "videos"
            reference = cache / f"{index}_reference.png"
            ground_truth = cache / f"{index}_ground_truth.mp4"
            driving = cache / f"{index}_driving.mp4"
            prepare_input(videos / "all_normalized_coordinate.mp4", ground_truth, reference)
            prepare_input(videos / "root_normalized_coordinate.mp4", driving)
            panels = [
                ("First Frame (Condition)", str(reference)),
                ("Driving Gear (Condition)", str(driving)),
                ("Ground Truth", str(ground_truth)),
                ("Generated", str(GENERATED_DIR / f"{index}.mp4")),
            ]
            temporary_output = cache / f"{index}.mp4"
            stack_videos.stack_videos(
                [panels], str(temporary_output), border_colors=borders, target_fps=FPS,
            )
            shutil.copy2(temporary_output, OUTPUT_DIR / f"{index}.mp4")


if __name__ == "__main__":
    main()
