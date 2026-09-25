#!/usr/bin/env python3
"""Animate a pairwise-probe run one transformer layer at a time."""

import argparse
import re
from pathlib import Path

from PIL import Image


FRAME_RE = re.compile(r"frame_\d+_layer_(?P<layer>\d+)\.png$")


def layer_number(path: Path) -> int:
    match = FRAME_RE.fullmatch(path.name)
    if match is None:
        raise ValueError(f"Unexpected probe-frame filename: {path.name}")
    return int(match.group("layer"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a browser-sized GIF from node-to-node probe frames."
    )
    parser.add_argument("input", type=Path, help="Probe run or frame directory")
    parser.add_argument("output", type=Path)
    parser.add_argument("--duration-ms", type=int, default=450)
    parser.add_argument("--max-width", type=int, default=900)
    args = parser.parse_args()

    frame_dir = args.input
    if frame_dir.name != "node_to_node_accuracy_frames":
        frame_dir = frame_dir / "node_to_node_accuracy_frames"
    paths = sorted(frame_dir.glob("frame_*_layer_*.png"), key=layer_number)
    if not paths:
        raise SystemExit(f"No probe frames found in {frame_dir}")

    frames = []
    for path in paths:
        with Image.open(path) as source:
            frame = source.convert("RGB")
            if frame.width > args.max_width:
                height = round(frame.height * args.max_width / frame.width)
                frame = frame.resize((args.max_width, height), Image.Resampling.LANCZOS)
            frames.append(
                frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=192)
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=args.duration_ms,
        loop=0,
        disposal=2,
        optimize=True,
    )
    print(f"Saved {len(frames)} layers to {args.output}")


if __name__ == "__main__":
    main()
