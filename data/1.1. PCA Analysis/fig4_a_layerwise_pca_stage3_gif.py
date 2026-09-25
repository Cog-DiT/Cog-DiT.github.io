"""Create animated layer-wise PCA overlays from every available PCA frame.

This is the animated counterpart of
``fig4_a_layerwise_pca_stage3.py``.  It deliberately keeps the original
five-field example syntax::

    BLOCK:HEAD:FEATURE:COMPONENT:FRAME

The final ``FRAME`` value selects the frame in the companion PNG, just as it
does in the original stage-3 renderer.  It is ignored only for the animated
GIF, where every frame in each selected PCA component is rendered in order.

Example (figure a):

    #figure (a)
    python3 fig4_a_layerwise_pca_stage3_gif.py \
      /work/koichi/Gear/gear_gen_angle_rad_con_auto/PCA_Gear_Motion_Normalize_HighNoise_GearFixed110GeneralGraph_Depth110_step_37000/Motion_10_LineDepth10_MinRad20_8/ \
      --timestep 1000.0 \
      --examples 8:all:x:0:1 11:5:v:3:10 13:6:v:0:1 15:0:v:1:4 \
                 16:6:v:0:4 17:5:v:0:12 18:all:v:0:12 18:0:v:0:4 \
                 19:7:v:0:3 20:1:v:0:3 \
      --output ./pca_overlays_general10_line10.gif \
      --nrow 5 --clean-gear-contour


    #figure (b)
    python3 fig4_a_layerwise_pca_stage3_gif.py   /work/koichi/Gear/gear_gen_angle_rad_con_auto/PCA_Gear_Motion_Normalize_HighNoise_GearFixed110LineGraph_Depth110_step_12000/Motion_10_MinRad20_12/   --timestep 1000.0   --examples     12:3:v:0:7     13:all:x:3:9     15:11:v:4:3     16:7:v:3:5     17:3:v:0:11     18:1:v:0:5   --output ./unseen_PCA.gif   --nrow 3 --clean-gear-contour
    
    #figure (c)
    python3 fig4_a_layerwise_pca_stage3_gif.py   /work/koichi/Gear/gear_gen_angle_rad_con_auto/PCA_Gear_Motion_Normalize_HighNoise_GearFixed110GeneralGraph_Depth110_step_37000/Motion_Depth10_Node100_MinRad25_30/   --timestep 1000.0   --examples     8:6:qkv:4:1     11:5:v:15:4     13:6:v:5:1     14:7:v:5:3     15:0:v:3:10     16:11:v:5:3     17:5:v:0:2     18:1:v:0:2     19:6:v:0:2     20:10:v:0:12   --output ./pca_overlays_general100_line10.gif   --nrow 5 --clean-gear-contour



    
The static renderer remains the single source of truth for parsing, metadata
resolution, gear-contour rendering, and figure styling.  By default it is
loaded from the sibling ``Gear`` repository in the same workspace.
"""

from __future__ import annotations

import importlib.util
import io
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Sequence

import matplotlib.pyplot as plt
from PIL import Image, ImageColor


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
STATIC_RENDERER_PATH = (
    WORKSPACE_ROOT
    / "Gear"
    / "gear_gen_angle_rad_con_auto"
    / "fig4_a_layerwise_pca_stage3.py"
)


def load_static_renderer(path: Path = STATIC_RENDERER_PATH) -> ModuleType:
    """Load the original stage-3 renderer without modifying its source."""
    path = path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(
            "Could not find the original stage-3 PCA renderer at "
            f"{path}. Keep the Cog-Dit and Gear repositories under the same "
            "workspace root."
        )

    module_name = "_fig4_a_layerwise_pca_stage3_static"
    specification = importlib.util.spec_from_file_location(module_name, path)
    if specification is None or specification.loader is None:
        raise ImportError(f"Could not load the static PCA renderer from {path}.")
    module = importlib.util.module_from_spec(specification)
    # Dataclasses inspect sys.modules while the imported module is executing.
    sys.modules[module_name] = module
    specification.loader.exec_module(module)
    return module


def build_parser(static_renderer: ModuleType):
    """Extend the original stage-3 CLI with GIF and PNG output controls."""
    parser = static_renderer.build_parser()
    parser.description = (
        "Create an animated paper figure from every frame of selected PCA "
        "components and a selected-frame PNG, with aligned gear outlines."
    )
    for action in parser._actions:
        if action.dest == "examples":
            action.help = (
                "Panels to animate, e.g. --examples 12:3:v:0:7 "
                "13:all:x:3:9. The final frame number selects the companion "
                "PNG frame and is ignored for the all-frame GIF."
            )
        elif action.dest == "output":
            action.help = (
                "Output basename or GIF path; a companion PNG with the same "
                "basename is also saved (default: PCA_results/"
                "layerwise_pca_animated_overlays/<timestep>/"
                "animated_pca_overlays.gif). A different suffix is replaced "
                "with .gif."
            )
    parser.add_argument(
        "--duration-ms",
        type=int,
        help=(
            "Display time per output frame in milliseconds. By default, use "
            "the timing stored in the first selected PCA GIF."
        ),
    )
    parser.add_argument(
        "--loop",
        type=int,
        default=0,
        help="Number of GIF repetitions; 0 loops forever (default: 0).",
    )
    return parser


def validate_arguments(args) -> dict[int, tuple[int, ...]]:
    """Apply the original stage-3 validation plus GIF-specific checks."""
    if args.nrow < 1:
        raise ValueError("--nrow must be positive.")
    if args.width is not None and args.width <= 0:
        raise ValueError("--width must be positive.")
    if args.height is not None and args.height <= 0:
        raise ValueError("--height must be positive.")
    if args.dpi <= 0:
        raise ValueError("--dpi must be positive.")
    if args.font_size <= 0:
        raise ValueError("--font-size must be positive.")
    if args.outline_width < 1:
        raise ValueError("--outline-width must be positive.")
    if args.duration_ms is not None and args.duration_ms < 1:
        raise ValueError("--duration-ms must be positive.")
    if args.loop < 0:
        raise ValueError("--loop must be non-negative.")
    if args.circle and args.clean_gear_contour:
        raise ValueError("--circle and --clean-gear-contour cannot be used together.")
    for option_name, color in (
        ("--outline-color", args.outline_color),
        ("--driving-color", args.driving_color),
    ):
        try:
            ImageColor.getrgb(color)
        except ValueError as error:
            raise ValueError(f"Invalid {option_name} {color!r}.") from error

    manual_depth_groups: dict[int, tuple[int, ...]] = {}
    for specification in args.manual_depth_groups:
        if specification.example_index > len(args.examples):
            raise ValueError(
                "Manual depth-group panel index "
                f"{specification.example_index} exceeds the {len(args.examples)} "
                "selected examples."
            )
        if specification.example_index in manual_depth_groups:
            raise ValueError(
                "Manual depth groups were specified more than once for panel "
                f"{specification.example_index}."
            )
        manual_depth_groups[specification.example_index] = specification.widths
    return manual_depth_groups


def inspect_source_gifs(
    static_renderer: ModuleType,
    timestep_dir: Path,
    selections: Sequence,
) -> tuple[list[Path], int, list[int]]:
    """Resolve PCA GIFs and return their common length and source timing."""
    paths = [
        static_renderer.resolve_gif(timestep_dir, selection)
        for selection in selections
    ]
    frame_counts: list[int] = []
    durations: list[int] = []
    for path_index, path in enumerate(paths):
        with Image.open(path) as gif:
            frame_count = int(getattr(gif, "n_frames", 1))
            frame_counts.append(frame_count)
            if path_index == 0:
                for frame_index in range(frame_count):
                    gif.seek(frame_index)
                    durations.append(max(1, int(gif.info.get("duration", 100))))

    if len(set(frame_counts)) != 1:
        details = ", ".join(
            f"{path.name}: {count}" for path, count in zip(paths, frame_counts)
        )
        raise ValueError(
            "Selected PCA component GIFs must contain the same number of "
            f"frames; found {details}."
        )
    return paths, frame_counts[0], durations


def render_animation_frame(
    static_renderer: ModuleType,
    selections: Sequence,
    gif_paths: Sequence[Path],
    pca_frame: int,
    pca_frame_count: int,
    metadata: dict,
    args,
    manual_depth_groups: dict[int, tuple[int, ...]],
) -> list:
    """Render one synchronized frame for every selected component panel."""
    rendered = []
    video_frame_count = static_renderer.source_frame_count(metadata)
    source_frame = static_renderer.source_frame_for_pca_frame(
        pca_frame,
        pca_frame_count,
        video_frame_count,
    )
    for example_index, (selection, gif_path) in enumerate(
        zip(selections, gif_paths), start=1
    ):
        # selection.frame is intentionally ignored. pca_frame walks 1..N.
        frame, loaded_frame_count = static_renderer.load_selected_frame(
            gif_path,
            pca_frame,
        )
        if loaded_frame_count != pca_frame_count:
            raise RuntimeError(f"Frame count changed while reading {gif_path}.")
        frame = static_renderer.overlay_gear_shapes(
            frame,
            metadata,
            source_frame,
            args.outline_color,
            args.driving_color,
            example_index - 1 if args.color_depth else None,
            manual_depth_groups.get(example_index),
            args.outline_width,
            args.show_gear_ids,
            args.circle,
            args.clean_gear_contour,
        )
        rendered.append(
            static_renderer.RenderedSelection(
                selection=selection,
                image=frame,
                pca_frame_count=pca_frame_count,
                source_frame=source_frame,
            )
        )
    return rendered


def compose_figure_frame(
    static_renderer: ModuleType,
    rendered: Sequence,
    nrow: int,
    width: float | None,
    height: float | None,
    dpi: int,
    font_size: float,
) -> Image.Image:
    """Arrange panels exactly like the static renderer and return an RGB image."""
    panel_count = len(rendered)
    column_count = min(nrow, panel_count)
    row_count = math.ceil(panel_count / column_count)
    image_aspect = static_renderer.TARGET_WIDTH / static_renderer.TARGET_HEIGHT
    if width is None:
        width = max(4.2, 0.72 * column_count)
    if height is None:
        panel_width = width / column_count
        title_height = 0.14 if nrow in {3, 5} else 0.25
        height = row_count * (panel_width / image_aspect + title_height)

    longest_title = max(len(f"Layer {item.selection.block}") for item in rendered)
    panel_width_points = width * 72.0 / column_count
    desired_title_font_size = font_size * 1.125 if nrow == 3 else font_size
    title_font_size = min(
        desired_title_font_size,
        max(3.5, panel_width_points / (0.65 * longest_title)),
    )

    plt.rcParams.update(
        {
            "font.family": ["Arial", "Liberation Sans", "DejaVu Sans"],
            "font.size": font_size,
        }
    )
    figure, axes = plt.subplots(
        row_count,
        column_count,
        squeeze=False,
        figsize=(width, height),
        constrained_layout=False,
    )
    for index, item in enumerate(rendered):
        row = index // column_count
        column = index % column_count
        axis = axes[row, column]
        axis.imshow(item.image, interpolation="nearest")
        axis.set_title(
            f"Layer {item.selection.block}",
            fontsize=title_font_size,
            pad=2,
        )
        axis.set_xticks([])
        axis.set_yticks([])
        for spine in axis.spines.values():
            spine.set_visible(False)
    for index in range(panel_count, row_count * column_count):
        row = index // column_count
        column = index % column_count
        axes[row, column].set_visible(False)
    figure.subplots_adjust(
        left=0.005,
        right=0.995,
        bottom=0.005,
        top=0.98,
        wspace=0.025,
        hspace=0.02 if nrow in {3, 5} else 0.16,
    )

    buffer = io.BytesIO()
    try:
        figure.savefig(
            buffer,
            format="png",
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.02,
            facecolor="white",
        )
        buffer.seek(0)
        with Image.open(buffer) as image:
            return image.convert("RGB")
    finally:
        plt.close(figure)
        buffer.close()


def default_output_path(attention_root: Path, timestep_dir: Path) -> Path:
    """Return the animated equivalent of the static renderer's default path."""
    if (
        attention_root.name == "attn_nodes"
        and attention_root.parent.name == "PCA_results"
    ):
        output_root = attention_root.parent / "layerwise_pca_animated_overlays"
    else:
        output_root = attention_root / "layerwise_pca_animated_overlays"
    return output_root / timestep_dir.name / "animated_pca_overlays.gif"


def gif_output_path(requested: Path | None, default: Path) -> Path:
    """Resolve an output path and guarantee the GIF suffix."""
    output = requested.expanduser().resolve() if requested is not None else default
    if output.suffix.lower() != ".gif":
        output = output.with_suffix(".gif")
    return output


def save_animation(
    frames: Sequence[Image.Image],
    output_path: Path,
    durations: Sequence[int],
    loop: int,
) -> None:
    """Save RGB figure frames as one looping animated GIF."""
    if not frames:
        raise ValueError("Cannot save an animation with no frames.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output_path,
        format="GIF",
        save_all=True,
        append_images=list(frames[1:]),
        duration=list(durations),
        loop=loop,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    """Save an all-frame GIF and an original-style selected-frame PNG."""
    static_renderer = load_static_renderer()
    args = build_parser(static_renderer).parse_args()
    manual_depth_groups = validate_arguments(args)

    attention_root = static_renderer.find_attention_root(args.input)
    timestep_dir = static_renderer.find_timestep_dir(attention_root, args.timestep)
    experiment_root = static_renderer.experiment_root_from_attention_root(
        attention_root
    )
    metadata_path = static_renderer.resolve_metadata_path(
        args.metadata,
        experiment_root,
        args.eval_data_root,
    )
    metadata = static_renderer.load_metadata(metadata_path)
    gif_paths, frame_count, source_durations = inspect_source_gifs(
        static_renderer,
        timestep_dir,
        args.examples,
    )

    output_path = gif_output_path(
        args.output,
        default_output_path(attention_root, timestep_dir),
    )
    png_output_path = output_path.with_suffix(".png")
    durations = (
        [args.duration_ms] * frame_count
        if args.duration_ms is not None
        else source_durations
    )

    selected_frames = static_renderer.render_selections(
        args.examples,
        timestep_dir,
        metadata,
        args.outline_color,
        args.driving_color,
        bool(args.color_depth),
        manual_depth_groups,
        args.outline_width,
        args.show_gear_ids,
        args.circle,
        args.clean_gear_contour,
    )
    static_renderer.save_figure(
        rendered=selected_frames,
        output_path=png_output_path,
        nrow=args.nrow,
        width=args.width,
        height=args.height,
        dpi=args.dpi,
        font_size=args.font_size,
    )

    animation_frames: list[Image.Image] = []
    for pca_frame in range(1, frame_count + 1):
        rendered = render_animation_frame(
            static_renderer,
            args.examples,
            gif_paths,
            pca_frame,
            frame_count,
            metadata,
            args,
            manual_depth_groups,
        )
        animation_frames.append(
            compose_figure_frame(
                static_renderer,
                rendered,
                args.nrow,
                args.width,
                args.height,
                args.dpi,
                args.font_size,
            )
        )
        print(f"Rendered PCA frame {pca_frame}/{frame_count}")

    save_animation(animation_frames, output_path, durations, args.loop)
    print(f"Using gear metadata: {metadata_path}")
    for item in selected_frames:
        print(
            f"Layer {item.selection.block}: selected PCA frame "
            f"{item.selection.frame}/{item.pca_frame_count} in PNG"
        )
    print(f"Saved selected-frame image to {png_output_path}")
    print(f"Saved {frame_count}-frame animation to {output_path}")


if __name__ == "__main__":
    main()
