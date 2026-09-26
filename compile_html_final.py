"""
How to run:
    python compile_html_final.py

Input:
./video/
    mesh/    
        0.mp4
        1.mp4
    ...
    {application_name}/
"""
import os
import glob
import json
import argparse
import urllib.parse

# --- CONFIGURATION ---

PAPER_TITLE = "Probing Kinematic Chain Reasoning in Video Diffusion Transformers: A Study of 2D Gear System"

if True:
    AUTHORS = [
        ("Anonymous Authors", [0], "https://Cog-DiT.github.io/"),
    ]

    INSTITUTIONS = [
        "Anonymous Institutions", 
    ]



ARXIV_LINK = "https://Cog-DiT.github.io/"
CODE_LINK = "https://Cog-DiT.github.io/"


SUCCESS_HEIGHTS = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
SUCCESS_TABLES = {
    20: (
        (10, (100, None, None, None, None, None, None, None, None, None)),
        (20, (100, 100, None, None, None, None, None, None, None, None)),
        (30, (100, 99, 68, None, None, None, None, None, None, None)),
        (40, (99, 98, 63, 42, None, None, None, None, None, None)),
        (50, (98, 86, 49, 23, 12, None, None, None, None, None)),
        (60, (98, 80, 33, 18, 9, 6, None, None, None, None)),
        (70, (100, 70, 22, 16, 12, 7, 2, None, None, None)),
        (80, (100, 54, 19, 7, 10, 3, 2, 3, None, None)),
        (90, (100, 46, 10, 5, 4, 7, 2, 3, 0, None)),
        (100, (97, 28, 15, 4, 5, 1, 2, 1, 3, 4)),
    ),
    30: (
        (10, (100, None, None, None, None, None, None, None, None, None)),
        (20, (100, 99, None, None, None, None, None, None, None, None)),
        (30, (99, 99, 97, None, None, None, None, None, None, None)),
        (40, (99, 99, 94, 84, None, None, None, None, None, None)),
        (50, (99, 98, 86, 74, 58, None, None, None, None, None)),
        (60, (97, 88, 78, 66, 47, 32, None, None, None, None)),
        (70, (100, 80, 72, 37, 34, 30, 14, None, None, None)),
        (80, (100, 70, 59, 31, 27, 16, 11, 12, None, None)),
        (90, (100, 68, 47, 24, 24, 12, 16, 5, 2, None)),
        (100, (98, 53, 38, 24, 15, 7, 7, 3, 5, 3)),
    ),
    40: (
        (10, (99, None, None, None, None, None, None, None, None, None)),
        (20, (99, 99, None, None, None, None, None, None, None, None)),
        (30, (99, 100, 100, None, None, None, None, None, None, None)),
        (40, (100, 99, 100, 97, None, None, None, None, None, None)),
        (50, (99, 97, 98, 96, 84, None, None, None, None, None)),
        (60, (98, 90, 88, 86, 66, 54, None, None, None, None)),
        (70, (100, 96, 81, 60, 44, 47, 30, None, None, None)),
        (80, (100, 92, 78, 58, 46, 31, 25, 17, None, None)),
        (90, (100, 83, 69, 51, 43, 31, 23, 20, 10, None)),
        (100, (99, 84, 71, 40, 35, 16, 12, 10, 9, 6)),
    ),
    50: (
        (10, (100, None, None, None, None, None, None, None, None, None)),
        (20, (100, 100, None, None, None, None, None, None, None, None)),
        (30, (99, 100, 100, None, None, None, None, None, None, None)),
        (40, (99, 100, 100, 100, None, None, None, None, None, None)),
        (50, (99, 99, 97, 98, 95, None, None, None, None, None)),
        (60, (99, 95, 97, 96, 95, 85, None, None, None, None)),
        (70, (100, 99, 89, 67, 56, 54, 43, None, None, None)),
        (80, (100, 97, 84, 62, 57, 42, 35, 31, None, None)),
        (90, (100, 90, 74, 63, 46, 38, 29, 25, 19, None)),
        (100, (99, 92, 73, 47, 35, 20, 23, 13, 15, 5)),
    ),
    100: (
        (10, (99, None, None, None, None, None, None, None, None, None)),
        (20, (100, 98, None, None, None, None, None, None, None, None)),
        (30, (99, 100, 100, None, None, None, None, None, None, None)),
        (40, (100, 99, 99, 100, None, None, None, None, None, None)),
        (50, (99, 96, 97, 95, 97, None, None, None, None, None)),
        (60, (96, 95, 92, 97, 98, 96, None, None, None, None)),
        (70, (100, 99, 97, 97, 93, 91, 98, None, None, None)),
        (80, (99, 100, 98, 92, 93, 94, 86, 99, None, None)),
        (90, (100, 100, 96, 94, 90, 84, 90, 84, 98, None)),
        (100, (100, 99, 95, 93, 90, 87, 83, 87, 86, 89)),
    ),
}


def render_success_table(train_limit, rows):
    """Render one success_all.tex table without duplicating its values in HTML."""
    headings = "".join(f"<th>{height}</th>" for height in SUCCESS_HEIGHTS)
    body_rows = []
    for gear_count, values in rows:
        cells = []
        for height, value in zip(SUCCESS_HEIGHTS, values):
            in_training_envelope = gear_count <= train_limit and height <= gear_count
            cell_class = ' class="training-region"' if in_training_envelope else ""
            if value is None:
                cells.append(f"<td{cell_class}>&mdash;</td>")
            else:
                cells.append(f'<td{cell_class} data-value="{value}">{value}</td>')
        body_rows.append(f'<tr><th scope="row">{gear_count}</th>{"".join(cells)}</tr>')
    return f"""
        <section class="success-table-card">
            <h5>Training: <i>N</i><sub>train</sub>, <i>h</i><sub>train</sub> &le; {train_limit}</h5>
            <div class="table-wrap">
                <table class="latex-table success-heatmap" aria-label="Simulation success rate after training on up to {train_limit} gears and kinematic height {train_limit}">
                    <thead>
                        <tr><th rowspan="2"><i>N</i></th><th colspan="10">Test kinematic height <i>h</i></th></tr>
                        <tr>{headings}</tr>
                    </thead>
                    <tbody>{"".join(body_rows)}</tbody>
                </table>
            </div>
        </section>
    """



MANUALLY_EMBEDDED_VIDEO_SECTIONS = {"1.4. I.D. Kinematic Height"}


def render_inline_video_gallery(section_name, indices):
    """Render selected scanned examples at a specific point in a narrative."""
    figures = []
    for index in indices:
        caption_path = os.path.join("video", section_name, f"{index}.json")
        caption_lines = []
        try:
            with open(caption_path, "r", encoding="utf-8") as handle:
                caption_data = json.load(handle)
            if isinstance(caption_data, list):
                for line in caption_data:
                    text = line.get("text", "")
                    color = line.get("color", [70, 70, 70])
                    hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                    caption_lines.append(f"<span style=\"display:block;color:{hex_color};\">{text}</span>")
        except (OSError, ValueError, TypeError):
            pass
        figures.append(f"""
            <figure class="pca-media-panel" style="padding:14px;border:1px solid #e0e0e0;border-radius:8px;background:#fff;">
                <video class="lazy" data-src="./video/{section_name}/{index}.mp4" preload="none" controls autoplay loop muted playsinline style="display:block;width:100%;height:auto;border-radius:6px;"></video>
                <figcaption style="margin-top:10px;line-height:1.5;">{"".join(caption_lines)}</figcaption>
            </figure>
        """)
    return "<div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px;margin:18px 0 30px;\">" + "".join(figures) + "</div>"



def render_inline_video_carousel(section_name, indices):
    """Render an unlabeled, self-contained carousel inside narrative HTML."""
    video_paths = [f"./video/{section_name}/{index}.mp4" for index in indices]
    encoded_paths = urllib.parse.quote(json.dumps(video_paths))
    dots = []
    for position in range(len(video_paths)):
        active = " active" if position == 0 else ""
        dots.append(
            f"<button class=\"carousel-dot{active}\" onclick=\"setInlineCarousel(this.closest(&quot;.inline-carousel&quot;), {position})\" aria-label=\"Slide {position + 1}\"></button>"
        )
    return f"""
        <div class="inline-carousel" data-videos="{encoded_paths}" data-index="0">
            <div class="carousel-wrapper">
                <button class="carousel-btn left" onclick="moveInlineCarousel(this, -1)">&#10094;</button>
                <video class="lazy" data-src="{video_paths[0]}" preload="none" controls autoplay loop muted playsinline></video>
                <button class="carousel-btn right" onclick="moveInlineCarousel(this, 1)">&#10095;</button>
                <div class="slide-counter">1 / {len(video_paths)}</div>
            </div>
            <div class="carousel-dots">{"".join(dots)}</div>
        </div>
    """

def render_mlp_probe_gallery():
    figures = []
    for count in (20, 30, 40, 50, 100):
        filename = f"train_{count}_eval_{count}.png"
        figures.append(f"""
            <figure>
                <a class="pca-media-link" href="data/2.2.%20MLP%20Probing/{filename}" target="_blank" rel="noopener noreferrer">
                    <img src="data/2.2.%20MLP%20Probing/{filename}" alt="Root-relative parity probing after training and evaluation at {count} gears" loading="lazy" decoding="async">
                </a>
                <figcaption><i>N</i><sub>train</sub>, <i>h</i><sub>train</sub> &le; {count}; evaluated on the {count}-gear linear chain.</figcaption>
            </figure>
        """)
    return '<div class="mlp-probing-figures analysis2-probe-grid">' + "".join(figures) + "</div>"


def render_pairwise_gallery():
    cases = []
    for count in (5, 10, 20, 30, 40, 50, 100):
        static_name = f"pairwise_parity_all_{count}.png"
        gif_name = f"pairwise_parity_all_{count}.gif"
        cases.append(f"""
            <section class="pca-case">
                <div class="pca-case-header">
                    <h5>Pairwise parity prediction accuracy across transformer layers</h5>
                </div>
                <p class="pca-case-summary">
                    Trained through <i>N</i>, <i>h</i> &le; {count} and evaluated on a linear chain of height {count}.
                </p>
                <div class="pca-media-pair">
                    <figure class="pca-media-panel">
                        <div class="pca-media-heading">Paper figure</div>
                        <a class="pca-media-link" href="data/2.2.%20MLP%20Probing/{static_name}" target="_blank" rel="noopener noreferrer">
                            <img src="data/2.2.%20MLP%20Probing/{static_name}" alt="Paper figure showing all pairwise parity probing matrices for {count} gears" loading="lazy" decoding="async">
                        </a>
                    </figure>
                    <figure class="pca-media-panel">
                        <div class="pca-media-heading">Animation</div>
                        <a class="pca-media-link" href="data/2.2.%20MLP%20Probing/{gif_name}" target="_blank" rel="noopener noreferrer">
                            <img src="data/2.2.%20MLP%20Probing/{gif_name}" alt="Animation of pairwise parity probing matrices across transformer layers for {count} gears" loading="lazy" decoding="async">
                        </a>
                    </figure>
                </div>
            </section>
        """)
    return '<div class="pca-analysis-gallery pairwise-gallery">' + "".join(cases) + "</div>"


ABSTRACT_TEXT = """

<p>
Video diffusion transformers (DiTs) are increasingly viewed as promising models for learning physical dynamics directly from video.
However, off-the-shelf models struggle to generate physically plausible gear motions, even in simple scenarios involving only two gears.
Simulating gear mechanisms is conceptually simple yet challenging, as the motion of a single gear strictly dictates the kinematics of the entire system.
In particular, determining the rotation direction of each gear requires computing its rotational parity by traversing the underlying kinematic chain.
</p>
<p>
To investigate whether video DiTs can learn such kinematic chain reasoning, we utilize 2D involute gear trains as a testbed to train and analyze video DiTs.
Our analysis reveals that models can indeed learn kinematic chain reasoning, but they acquire two distinct types of reasoning mechanisms depending on the kinematic heights encountered during training:
when trained on mechanisms with short kinematic heights, the model acquires a parallel BFS-like reasoning, using transformer layers as breadth-first search steps to incrementally determine parity across the kinematic tree.
Conversely, when exposed to large kinematic heights during training, the model adopts a divide-and-conquer-like strategy—first resolving parity within local neighborhoods and subsequently merging them to achieve global consistency.
Overall, this work demonstrates that video DiTs are capable of learning algorithmic reasoning over kinematic chains, while also uncovering their generalization limits and highlighting the critical role of training data complexities.
</p>
"""


# --- 3-LEVEL HIERARCHY CONFIG ---
# The script automatically detects if an item is a "Group" (tuple with list) or "Single" (string)
SIDEBAR_CONFIG = [
    ("Introduction",["Task Definition"]),
    ("Motivation: Why study gear simulation? ", [
        "Animating Gear Systems with Commercial Video Models",
    ]),
    ("Qualitative Results",[
            "10-Gear Count",
            "20-Gear Count",
            "30-Gear Count",
            "40-Gear Count",
            "50-Gear Count",
            "100-Gear Count"
    ]),
    ("Analysis: How Do Video Diffusion Transformers Simulate Gear Systems?", [
                    ("Analysis 1: Emergence of Parallel BFS-like Reasoning in Short Kinematic Chains", [
                        "1.1. PCA Analysis",
                        "1.2. MLP Probing",
                        "1.3. O.O.D. Kinematic Height",
                        "1.4. I.D. Kinematic Height",
                    ]),
                    ("Analysis 2: Emergence of Divide-and-Conquer-like Reasoning in Long Kinematic Chains", [
                        "2.1. PCA Analysis",
                        "2.2.1. Root-relative MLP Probing",
                        "2.2.2. Pairwise MLP Probing",
                        "2.3. Generalizability",
                    ]),
                ]
    )
]


DATASET_DESCRIPTIONS = {
    "Task Definition": """
    <div>
    <p>
        In this paper, we adopt 2D involute gear trains as a testbed for evaluating the ability of video diffusion transformers to simulate systems of simultaneously interacting physical objects with potentially long-chain kinematic dependencies.
        Specifically, as visualized below, the model is provided with the initial spatial layout of a gear system as the first frame. A single gear is designated as the <b>driving gear</b>, and its full rotational trajectory is provided as a conditioning video. 
        The objective is to synthesize the resulting motion of all remaining gears while satisfying the underlying kinematic constraints. 
        We fine-tune the Wan2.1 (1.3B) text-to-video model.  Below, we visualize a few examples of the input and ground-truth data. 
    </p>
    </div>
    """,
    "Motivation: Why study gear simulation? ": """
    Gear systems are governed by a simple local rule: meshed gears rotate in opposite directions, with absolute angular velocities inversely proportional to their diameters. 
    Despite this simple rule, simulating a gear train provides a challenging testbed for long-chain kinematic reasoning. 
    In particular, determining the rotational direction of each gear requires computing its rotational <b>parity</b>, which is determined by the number of meshing interactions along the kinematic path from the driving gear. 
    Thus, simulating a gear system requires propagating kinematic information across potentially long chains of gears. Notably, once the rotational parity is determined, the angular velocity magnitude follows directly from the gear diameters, independent of the kinematic graph topologies. 
    """,
    "Animating Gear Systems with Commercial Video Models": """
    <div>
    <p>
       Indeed off-the-shelf video generation models<sup>*</sup> struggle to synthesize kinematically plausible animations of gear systems, even for the simple case of two meshing gears, where the gears rotate in conflicting directions.
       This raises the question of whether video diffusion transformers are capable of reasoning about such kinematic chain dependencies and, if so, how they achieve this.
    </p>
    <p style="margin-top: 1em;">
        <small><sup>*</sup>Videos were generated using <a href="https://lumalabs.ai" target="_blank" rel="noopener noreferrer">lumalabs.ai</a>.</small>
    </p>
    </div>
    """,
   "Qualitative Results": """
    <div>
    <p>
       Despite the aforementioned failures of commercial video diffusion models, our initial findings suggest that, with appropriate fine-tuning, video diffusion transformers can successfully generate videos of gear systems that satisfy the underlying kinematic constraints, even as the number of gears increases substantially.
       Below demonstrate the some generated examples. 
    </p>
    </div>
    """,
    "10-Gear Count": """
    <div>
    <p>
        Herem the mode is trained and tested up to 10-gear system.
    </p>
    </div>
    """,
    "20-Gear Count": """
    <div>
    <p>
        Here the model is trained and tested up to 20-gear system.
    </p>
    </div>
    """,
    "30-Gear Count": """
    <div>
    <p>
        Here the model is trained and tested up to 30-gear system.
    </p>
    </div>
    """,
    "40-Gear Count": """
    <div>
    <p>
        Here the model is trained and tested up to 40-gear system.
    </p>
    </div>
    """,
    "50-Gear Count": """
    <div>
    <p>
        Here the model is trained and tested up to 50-gear system.
    </p>
    </div>
    """,
    "100-Gear Count": """
    <div>
    <p>
        Here the model is trained and tested up to 100-gear system.
    </p>
    </div>
    """,
    "Analysis: How Do Video Diffusion Transformers Simulate Gear Systems?": """
    <div>
        <p>
            Fine-tuned video diffusion transformers can generate kinematically consistent gear motion, but doing so requires resolving rotational parity across the entire kinematic chain.
            We therefore perform feature probing on trained DiTs to investigate what reasoning mechanisms emerge internally.
        </p>
        <p>
            Crucially, the model learns two distinct types of algorithms depending on the **kinematic height** *h*—the maximum graph distance from the driving gear—seen during training:
        </p>
        <ul>
            <li><b>Parallel bfs strategy:</b> When the model is trained on a small number of gears, the successive transformer layers behave like parallel breadth-first search steps, determining parity one graph depth at a time. </li>
            <li><b>Divide-and-Conquer like strategy:</b> When the required number of BFS steps exceeds the available network depth, the model switches to a divide-and-conquer strategy, in which it forms locally consistent parity regions and later merges them.</li>
        </ul>
        <p>The sections below demonstrate these mechanisms.</p>
    </div>
    """,
    "Analysis 1: Emergence of Parallel BFS-like Reasoning in Short Kinematic Chains": """
    <p>
        We first study models trained on mechanisms with at most 10 gears and kinematic height.
        Notably, kinematic height is much smaller than the number of layers (30) in the network.
    </p>
    """,
    "1.1. PCA Analysis": """
    <div class="pca-analysis-gallery">
        <p class="pca-lead">
        The PCA analysis below reveals an interesting pattern: there is a principal axis that separates features associated with gears of different rotational parity.
        Remarkably, this parity signal first emerges around the driving gear, and then progressively propagates to neighboring gears across successive transformer layers, resembling a parallel BFS-like progression.
        </p>
        <div class="mlp-probing-figures">
            <figure><a href="data/1.1.%20PCA%20Analysis/pca_overlays_general10_line10.gif" target="_blank" rel="noopener noreferrer"><img src="data/1.1.%20PCA%20Analysis/pca_overlays_general10_line10.gif" alt="Animated layer-wise PCA overlays for an in-distribution 10-gear chain" loading="lazy" decoding="async"></a></figure>
            <figure><a href="data/1.1.%20PCA%20Analysis/unseen_PCA.gif" target="_blank" rel="noopener noreferrer"><img src="data/1.1.%20PCA%20Analysis/unseen_PCA.gif" alt="Animated layer-wise PCA overlays for an unseen branching topology" loading="lazy" decoding="async"></a></figure>
        </div>
        <div class="mlp-probing-figures" style="grid-template-columns:minmax(0,80%);justify-content:center;">
            <figure><a href="data/1.1.%20PCA%20Analysis/pca_overlays_general100_line10.gif" target="_blank" rel="noopener noreferrer"><img src="data/1.1.%20PCA%20Analysis/pca_overlays_general100_line10.gif" alt="Animated layer-wise PCA overlays for a 100-gear height-10 mechanism" loading="lazy" decoding="async"></a></figure>
        </div>
    </div>
    """,
    "1.2. MLP Probing": """
    <p>
        To quantitatively verify this process, we perform MLP probing to measure the amount of information each transformer layer stores about the rotational parity of individual gears relative to the driving gear.
        As shown in the table below, the probing accuracy increases almost linearly with network depth, providing evidence that gear parity is determined incrementally across layers.
        (Note: Each heatmap reports the probing accuracy for predicting the parity of each gear relative to the driving gear, across transformer blocks (vertical axis) and gear depth from the driving gear (horizontal axis).)
    </p>
    <div class="mlp-probing-figures">
        <figure>
            <a href="data/1.2%20MLP%20Probing/train_5_eval_5.png" target="_blank" rel="noopener noreferrer">
                <img src="data/1.2%20MLP%20Probing/train_5_eval_5.png" alt="MLP parity-probing accuracy across transformer blocks and depths for training and evaluation height 5" loading="lazy" decoding="async">
            </a>
            <figcaption><b>Train and evaluate at <i>h</i> &le; 5.</b> </figcaption>
        </figure>
        <figure>
            <a href="data/1.2%20MLP%20Probing/train_10_eval_10.png" target="_blank" rel="noopener noreferrer">
                <img src="data/1.2%20MLP%20Probing/train_10_eval_10.png" alt="MLP parity-probing accuracy across transformer blocks and depths for training and evaluation height 10" loading="lazy" decoding="async">
            </a>
            <figcaption><b>Train and evaluate at <i>h</i> &le; 10.</b> </figcaption>
        </figure>
    </div>
    <p>
        <strong>Key observation:</strong> the high-accuracy region advances approximately one graph depth at a time as transformer depth increases, quantitatively supporting the parallel-BFS reasoning mechanisms. 
    </p>
    """,
    "1.3. O.O.D. Kinematic Height": """
    <div>
        <p>
        The learned Parallel-BFS reasoning mechanisms generalize poorly to unseen kinematic heights.
        As shown in the table below, the model achieves a success rate of almost $0$ on out-of-distribution cases when the kinematic height exceeds the training range.
        </p>
        <div class="success-table-grid comparison-table-pair">
            <!-- Table 6: five-gear training regime (left) -->
            <section class="success-table-card">
                <div class="table-wrap" style="margin: 0;">
                    <table class="latex-table comparison-success-table" aria-label="Table 6 simulation success rates for a model trained on up to 5 gears and height 5">
                        <caption style="caption-side: top; text-align: left; padding: 0 0 10px; color: #333; line-height: 1.5;">
                            <strong>Table 6. Model trained on up to 5 gears.</strong>
                        </caption>
                        <thead>
                            <tr><th rowspan="2" scope="col">Gears (<i>N</i>)</th><th colspan="5" scope="colgroup">Kinematic height (<i>h</i>)</th></tr>
                            <tr><th scope="col">5</th><th scope="col">10</th><th scope="col">20</th><th scope="col">30</th><th scope="col">40</th></tr>
                        </thead>
                        <tbody>
                            <tr><th scope="row">5</th><td style="background:#dff1e1;">100%</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">10</th><td style="background:#dff1e1;">100%</td><td class="focus-ood-height" style="background:#f7e4e2;">3%</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">20</th><td style="background:#e3eee2;">94%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">30</th><td style="background:#e2efe2;">96%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td></tr>
                            <tr><th scope="row">40</th><td style="background:#e8ebe0;">88%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Table 1: ten-gear training regime (right) -->
            <section class="success-table-card">
                <div class="table-wrap" style="margin: 0;">
                    <table class="latex-table comparison-success-table" aria-label="Table 1 simulation success rates for a model trained on up to 10 gears and height 10">
                        <caption style="caption-side: top; text-align: left; padding: 0 0 10px; color: #333; line-height: 1.5;">
                            <strong>Table 1. Model trained on up to 10 gears.</strong>
                        </caption>
                        <thead>
                            <tr><th rowspan="2" scope="col">Gears (<i>N</i>)</th><th colspan="10" scope="colgroup">Kinematic height (<i>h</i>)</th></tr>
                            <tr>
                                <th scope="col">10</th><th scope="col">20</th><th scope="col">30</th><th scope="col">40</th><th scope="col">50</th>
                                <th scope="col">60</th><th scope="col">70</th><th scope="col">80</th><th scope="col">90</th><th scope="col">100</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><th scope="row">10</th><td style="background:#dff1e1;">100%</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">20</th><td style="background:#dff1e1;">100%</td><td class="focus-ood-height" style="background:#f8e1e1;">1%</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">30</th><td style="background:#e1f0e2;">97%</td><td class="focus-ood-height" style="background:#f8e1e1;">1%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">40</th><td style="background:#dff1e1;">100%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">50</th><td style="background:#e3eee2;">94%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">60</th><td style="background:#e6ece1;">90%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">70</th><td style="background:#dff1e1;">100%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">80</th><td style="background:#e0f0e1;">99%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td><td>—</td></tr>
                            <tr><th scope="row">90</th><td style="background:#e7ebe0;">89%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td>—</td></tr>
                            <tr><th scope="row">100</th><td style="background:#ebeadf;">82%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td><td class="focus-ood-height" style="background:#f8dfdf;">0%</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </div>

        <!-- Figure 4 -->
        <h5 style="margin: 34px 0 8px; font-size: 1.05rem; color: #333;">Feature probing on out-of-distribution kinematic heights</h5>
        <p>
        Feature probing below also reveals that the model successfully propagates parity information across transformer layers up to the height observed during training, but that this iterative propagation ceases beyond that height.
        </p>
        <div class="mlp-probing-figures figure4-probe-grid">
            <figure>
                <a href="data/1.3.%20O.O.D.%20Kinematic%20Height/train_5_eval_10.png" target="_blank" rel="noopener noreferrer">
                    <img src="data/1.3.%20O.O.D.%20Kinematic%20Height/train_5_eval_10.png" alt="Feature probing for height-5 training evaluated on a height-10 linear chain" loading="lazy" decoding="async">
                </a>
                <figcaption><b>Train: <i>h</i> &le; 5; evaluate: <i>N</i> = <i>h</i> = 10.</b></figcaption>
            </figure>
            <figure>
                <a href="data/1.3.%20O.O.D.%20Kinematic%20Height/train_10_eval_20.png" target="_blank" rel="noopener noreferrer">
                    <img src="data/1.3.%20O.O.D.%20Kinematic%20Height/train_10_eval_20.png" alt="Feature probing for height-10 training evaluated on a height-20 linear chain" loading="lazy" decoding="async">
                </a>
                <figcaption><b>Train: <i>h</i> &le; 10; evaluate: <i>N</i> = <i>h</i> = 20.</b></figcaption>
            </figure>
        </div>
        <h5 style="margin: 30px 0 8px; font-size: 1.05rem; color: #333;">O.O.D. failure examples</h5>
    </div>
    """,
    "1.4. I.D. Kinematic Height": f"""
    <div class="full-width-analysis">
        <p>
        The model can generalize to unseen gear counts and branching factors as long as the kinematic height remains within the training distribution.
        As shown in the tables below, the model performs well on mechanisms containing 100 gears, despite being trained only on mechanisms with up to 10 gears, provided that the kinematic height remains in-distribution (i.e. h = 10).
        </p>

        <div class="success-table-grid comparison-table-pair">
            <!-- Table 6: five-gear training regime (left) -->
            <section class="success-table-card">
                <div class="table-wrap" style="margin:0;">
                    <table class="latex-table comparison-success-table" aria-label="Table 6 highlighting larger gear counts at in-distribution height after training on up to 5 gears">
                        <caption style="caption-side:top;text-align:left;padding:0 0 10px;color:#333;line-height:1.5;">
                            <strong>Table 6. Model trained on up to 5 gears.</strong>
                            Here <i>N</i><sub>train</sub>, <i>h</i><sub>train</sub> &le; 5.
                        </caption>
                        <thead>
                            <tr><th rowspan="2" scope="col">Gears (<i>N</i>)</th><th colspan="5" scope="colgroup">Kinematic height (<i>h</i>)</th></tr>
                            <tr><th scope="col">5</th><th scope="col">10</th><th scope="col">20</th><th scope="col">30</th><th scope="col">40</th></tr>
                        </thead>
                        <tbody>
                            <tr><th scope="row">5</th><td style="background:#dff1e1;">100%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">10</th><td class="focus-ood-count" style="background:#dff1e1;">100%</td><td style="background:#f7e4e2;">3%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">20</th><td class="focus-ood-count" style="background:#e3eee2;">94%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">30</th><td class="focus-ood-count" style="background:#e2efe2;">96%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td></tr>
                            <tr><th scope="row">40</th><td class="focus-ood-count" style="background:#e8ebe0;">88%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Table 1: ten-gear training regime (right) -->
            <section class="success-table-card">
                <div class="table-wrap" style="margin:0;">
                    <table class="latex-table comparison-success-table" aria-label="Table 1 highlighting larger gear counts at in-distribution height after training on up to 10 gears">
                        <caption style="caption-side:top;text-align:left;padding:0 0 10px;color:#333;line-height:1.5;">
                            <strong>Table 1. Model trained on up to 10 gears.</strong>
                            Here <i>N</i><sub>train</sub>, <i>h</i><sub>train</sub> &le; 10.
                        </caption>
                        <thead>
                            <tr><th rowspan="2" scope="col">Gears (<i>N</i>)</th><th colspan="10" scope="colgroup">Kinematic height (<i>h</i>)</th></tr>
                            <tr><th scope="col">10</th><th scope="col">20</th><th scope="col">30</th><th scope="col">40</th><th scope="col">50</th><th scope="col">60</th><th scope="col">70</th><th scope="col">80</th><th scope="col">90</th><th scope="col">100</th></tr>
                        </thead>
                        <tbody>
                            <tr><th scope="row">10</th><td style="background:#dff1e1;">100%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">20</th><td class="focus-ood-count" style="background:#dff1e1;">100%</td><td style="background:#f8e1e1;">1%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">30</th><td class="focus-ood-count" style="background:#e1f0e2;">97%</td><td style="background:#f8e1e1;">1%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">40</th><td class="focus-ood-count" style="background:#dff1e1;">100%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">50</th><td class="focus-ood-count" style="background:#e3eee2;">94%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">60</th><td class="focus-ood-count" style="background:#e6ece1;">90%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">70</th><td class="focus-ood-count" style="background:#dff1e1;">100%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">80</th><td class="focus-ood-count" style="background:#e0f0e1;">99%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td><td>&mdash;</td></tr>
                            <tr><th scope="row">90</th><td class="focus-ood-count" style="background:#e7ebe0;">89%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td>&mdash;</td></tr>
                            <tr><th scope="row">100</th><td class="focus-ood-count" style="background:#ebeadf;">82%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td><td style="background:#f8dfdf;">0%</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
        <h5 style="margin:28px 0 8px;font-size:1.05rem;color:#333;">Successful 100-Gear Examples (Models Trained on Mechanisms with Up to 10 Gears, Applied to 100-Gear Mechanisms)</h5>
        {render_inline_video_carousel("1.4. I.D. Kinematic Height", range(0, 5))}

        <section class="pca-case">
            <div class="pca-case-header"><h5>Parity propagation scales to 100 gears at height 10</h5></div>
            <p class="pca-case-summary">The parallel-BFS-like feature progression appears on 100 gears even when the model is trained only up to 10 Gears.</p>
            <div class="pca-media-pair">
                <figure class="pca-media-panel"><div class="pca-media-heading">All video frames</div><a class="pca-media-link" href="data/1.1.%20PCA%20Analysis/pca_overlays_general100_line10.gif" target="_blank" rel="noopener noreferrer"><img src="data/1.1.%20PCA%20Analysis/pca_overlays_general100_line10.gif" alt="Animated PCA overlays for 100 gears at height 10" loading="lazy" decoding="async"></a></figure>
                <figure class="pca-media-panel"><div class="pca-media-heading">Selected paper frame</div><a class="pca-media-link" href="data/1.1.%20PCA%20Analysis/pca_overlays_general100_line10.png" target="_blank" rel="noopener noreferrer"><img src="data/1.1.%20PCA%20Analysis/pca_overlays_general100_line10.png" alt="Static PCA overlays for 100 gears at height 10" loading="lazy" decoding="async"></a></figure>
            </div>
        </section>

        <h5 style="margin:34px 0 8px;font-size:1.08rem;color:#333;">Generalization to unseen tree topologies</h5>
        <p>
         we train the model exclusively on gear mechanisms forming linear kinematic chains, in which each interior gear has exactly two neighboring gears.
         Interetingly, the trained model still performs well on arbitrary tree topologies during inference as demonstrated below.
        </p>
        <div class="table-wrap" style="margin:18px 0 10px;">
            <table class="latex-table" style="min-width:650px;" aria-label="Table 2 generalization from linear chains to unseen general tree topologies">
                <caption style="caption-side:top;text-align:left;padding:0 0 10px;color:#333;line-height:1.5;"><strong>Table 2. Generalization to unseen tree topologies.</strong> Simulation success rate (SSR; higher is better) and relative motion disparity (<i>E</i><sub>rmd</sub>; lower is better) for linear-chain training evaluated on linear chains and general trees.</caption>
                <thead><tr><th rowspan="2">Training bound</th><th colspan="2">Linear chain (I.D.)</th><th colspan="2" style="color:#b42318;">General tree (O.O.D.)</th></tr><tr><th>SSR &uarr;</th><th><i>E</i><sub>rmd</sub> &darr;</th><th>SSR &uarr;</th><th><i>E</i><sub>rmd</sub> &darr;</th></tr></thead>
                <tbody>
                    <tr><th><i>N</i><sub>train</sub>, <i>h</i><sub>train</sub> &le; 5</th><td style="background:#dff1e1;">100%</td><td style="background:#dff1e1;">0.058</td><td style="background:#dff1e1;">100%</td><td style="background:#dff1e1;">0.058</td></tr>
                    <tr><th><i>N</i><sub>train</sub>, <i>h</i><sub>train</sub> &le; 10</th><td style="background:#e1f0e2;">97%</td><td style="background:#e1f0e2;">0.046</td><td style="background:#e0f0e1;">99%</td><td style="background:#e0f0e1;">0.040</td></tr>
                </tbody>
            </table>
        </div>

        <h5 style="margin:28px 0 8px;font-size:1.05rem;color:#333;">Successful unseen-topology examples (Trained on linear graph, tested on general graph)</h5>
        {render_inline_video_carousel("1.4. I.D. Kinematic Height", range(5, 10))}

        <section class="pca-case">
            <div class="pca-case-header"><h5>PCA analysis on unseen kinematic topologies.</h5></div>
            <p class="pca-case-summary">The transformer layers successfully propagate parity information to previously unseen numbers of neighboring gears in parallel. </p>
            <div class="pca-media-pair">
                <figure class="pca-media-panel"><div class="pca-media-heading">All video frames</div><a class="pca-media-link" href="data/1.1.%20PCA%20Analysis/unseen_PCA.gif" target="_blank" rel="noopener noreferrer"><img src="data/1.1.%20PCA%20Analysis/unseen_PCA.gif" alt="Animated PCA overlays on an unseen branching topology" loading="lazy" decoding="async"></a></figure>
                <figure class="pca-media-panel"><div class="pca-media-heading">Selected paper frame</div><a class="pca-media-link" href="data/1.1.%20PCA%20Analysis/unseen_PCA.png" target="_blank" rel="noopener noreferrer"><img src="data/1.1.%20PCA%20Analysis/unseen_PCA.png" alt="Static PCA overlays on an unseen branching topology" loading="lazy" decoding="async"></a></figure>
            </div>
        </section>
    </div>
    """,
    "Analysis 2: Emergence of Divide-and-Conquer-like Reasoning in Long Kinematic Chains": """
    <p>
        We next demonstrate the emergence of divide-and-conquer-like reasoning by training models on gear mechanisms with numbers of gears and kinematic heights up to 50.
        Notably, our video DiT contains only 30 transformer layers.
        Therefore, a straightforward parallel BFS strategy is infeasible.
    </p>
    """,
    "2.1. PCA Analysis": """
    <div class="pca-analysis-gallery">
        <div class="pca-lead">
            <p>
            Our PCA analysis below reveals an intriguing departure from the short-chain setting.
            In the early layers, we continue to observe the parallel BFS pattern.
            However, in mid-late layers, parity signals begin to emerge simultaneously in gears that have not yet been reached by the BFS process.
            Importantly, these newly emerging signals are initially consistent only within their respective neighborhoods, but subsequently become globally consistent.
            </p>
        </div>
        <section class="pca-case">
            <div class="pca-case-header">
                <h5>Layer-wise PCA visualization</h5>
            </div>
            <div class="pca-media-pair">
                <figure class="pca-media-panel">
                    <div class="pca-media-heading">Paper figure</div>
                    <a class="pca-media-link" href="data/2.1.%20PCA%20Analysis/pca_overlays_general30_line30.png" target="_blank" rel="noopener noreferrer">
                        <img src="data/2.1.%20PCA%20Analysis/pca_overlays_general30_line30.png" alt="Paper PCA figure for a model trained and evaluated on 30-gear height-30 mechanisms" loading="lazy" decoding="async">
                    </a>
                </figure>
                <figure class="pca-media-panel">
                    <div class="pca-media-heading">All frames</div>
                    <a class="pca-media-link" href="data/2.1.%20PCA%20Analysis/pca_overlays_general30_line30_blue.gif" target="_blank" rel="noopener noreferrer">
                        <img src="data/2.1.%20PCA%20Analysis/pca_overlays_general30_line30_blue.gif" alt="Animated layer-wise PCA for 30 gears with all gear contours automatically overlaid in blue" loading="lazy" decoding="async">
                    </a>
                </figure>
            </div>
        </section>
    </div>
    """,
    "2.2.1. Root-relative MLP Probing": f"""
    <p>
    MLP probing provides further evidence for this behavior.
    In the shallow layers, probing accuracy for the relative parity between the driving gear and each gear increases approximately linearly with kinematic depth.
    In later layers, however, the accuracy increases rapidly.
    </p>
    {render_mlp_probe_gallery()}
    """,
    "2.2.2. Pairwise MLP Probing": f"""
    <p>
        The matrix below visualizes the per-layer pairwise parity prediction accuracy across the linear gear chain.
        When the model is trained on larger gear counts (e.g., 20, 30, ...), we observe the formation of clusters in which parity predictions are highly accurate locally but remain globally inconsistent.
        In later layers, these local clusters progressively merge, ultimately yielding a globally consistent parity representation. 
    </p>
    {render_pairwise_gallery()}
    """,
    "2.3. Generalizability": f"""
    <p>
    The learned divide-and-conquer strategy does not exhibit the same degree of generalizability as the parallel BFS strategy.
    As shown below, we observe weaker generalization to unseen gear counts, even when the kinematic height remains within the training distribution.
    The main exception is when the kinematic height is up to around $10$, where the model continues to generalize.
    This is because the model can still rely on parallel BFS reasoning.
    Another notable difference is that the model starts exhibiting non-zero success rates on unseen kinematic heights, which was not the case in experiments with shorter kinematic chains.
    </p>
    <div class="success-table-grid">
        {render_success_table(20, SUCCESS_TABLES[20])}
        {render_success_table(30, SUCCESS_TABLES[30])}
        {render_success_table(40, SUCCESS_TABLES[40])}
        {render_success_table(50, SUCCESS_TABLES[50])}
        {render_success_table(100, SUCCESS_TABLES[100])}
    </div>
    """,
}

# --- HTML Template ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_title}</title>
    <meta name="description" content="{paper_title}">
    
    <style>
        :root {{
            /* --- COLOR PALETTE --- */
            --primary-color: #0078d4;        
            --primary-hover: #005a9e;        
            --text-main: #333333;            
            --text-title: #222222;           
            --text-secondary: #555555;       
            --bg-sidebar: #f4f4f4;
            --bg-body: #ffffff;
            --border-color: #e0e0e0;
            --bg-section: #f4f4f4;
            --bg-level1: #e6f2fb; 
            
            /* Standard System Sans-Serif Stack */
            --font-stack: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        }}

        body {{
            font-family: var(--font-stack);
            background-color: var(--bg-body);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            display: flex; 
            overflow-x: hidden;
        }}

        /* --- HIDE CLUSTRMAPS CONTAINER --- */
        #clustrmaps-widget-container {{
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            position: absolute;
            top: -9999px;
            left: -9999px;
        }}
        
        /* --- Sidebar --- */
        .dataset-nav {{
            position: fixed;
            top: 0;
            left: 0;
            width: 250px; 
            height: 100vh;
            background-color: var(--bg-sidebar);
            border-right: 1px solid #d0d0d0;
            padding-top: 60px; 
            padding-left: 0;
            padding-right: 0;
            z-index: 1002;
            display: flex;
            flex-direction: column; 
            gap: 2px; 
            overflow-y: auto; 
            overflow-x: hidden;
            box-sizing: border-box;
            transition: width 0.3s ease; 
        }}

        .dataset-nav::-webkit-scrollbar {{ width: 5px; }}
        .dataset-nav::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 4px; }}
        .dataset-nav::-webkit-scrollbar-track {{ background: transparent; }}

        .nav-category {{
            font-size: 11px;
            text-transform: none; 
            color: #777; 
            font-weight: 700;
            margin-top: 25px;
            margin-bottom: 5px;
            padding-left: 15px;
            letter-spacing: 0.5px;
            white-space: nowrap;
            transition: opacity 0.2s ease;
        }}
        
        .nav-subcategory {{
            font-size: 12px;
            color: #444;
            font-weight: 700;
            margin-top: 10px;
            margin-bottom: 2px;
            padding-left: 12px;
            text-transform: none;
        }}

        /* Base Sidebar Button */
        .dataset-btn {{
            background-color: transparent;
            color: #444;
            border: none;
            border-left: 4px solid transparent;
            cursor: pointer;
            text-align: left;
            word-break: break-word; 
            white-space: normal;    
            line-height: 1.4;        
            transition: all 0.2s ease;
            font-family: var(--font-stack);
            width: 100%;
            display: block;
            box-sizing: border-box;
        }}

        .dataset-btn:hover {{
            background-color: #e0e0e0;
            color: #000;
        }}

        .dataset-btn.active {{
            background-color: var(--bg-level1);
            color: #000;
            border-left-color: var(--primary-color);
            font-weight: 600;
        }}

        /* Overview Button */
        .dataset-btn.overview-btn {{
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 10px;
            font-size: 14px;
            padding: 8px 15px;
        }}

        /* Level 2 Button (Sub-Category) */
        .dataset-btn.level-2 {{
            font-size: 13px;
            font-weight: 600;
            padding: 8px 15px 8px 15px; 
            margin-top: 2px;
            color: #333;
        }}

        /* Level 3 Button (Content) */
        .dataset-btn.level-3 {{
            font-size: 12px;
            font-weight: 400;
            padding: 6px 15px 6px 30px; /* Indented */
            color: #555;
        }}
        
        .dataset-btn.level-3.active {{
             background-color: #f0f8ff; 
             color: var(--primary-color);
        }}

        /* --- Toggle Button --- */
        #sidebar-toggle {{
            position: fixed;
            top: 10px;
            left: 5px; 
            z-index: 1003;
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
            font-size: 18px;
            line-height: 1;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: left 0.3s ease;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }}
        #sidebar-toggle:hover {{
            background-color: #f0f0f0;
        }}

        /* --- Main Content --- */
        .main-content {{
            margin-left: 250px;
            width: calc(100% - 250px); 
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: margin-left 0.3s ease, width 0.3s ease;
            box-sizing: border-box; 
        }}

        .paper-header {{
            width: 100%;
            background-color: #ffffff;
            padding: 50px 20px 30px 20px;
            text-align: center;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 40px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}

        .paper-title {{
            font-family: Georgia, 'Times New Roman', Times, serif;
            font-size: 2.2rem;
            font-weight: 400; 
            color: #444; 
            margin: 0 auto 20px auto;
            line-height: 1.3;
            max-width: 900px;
            letter-spacing: -0.2px; 
        }}

        .paper-authors, .paper-institutions {{
            font-size: 1.2rem;
            color: #222;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        .paper-authors .author-link {{
            color: inherit;
            text-decoration-line: underline;
            text-decoration-style: solid;
            text-decoration-color: rgba(0, 120, 212, 0.35);
            text-decoration-thickness: 2px;
            text-underline-offset: 3px;
            cursor: pointer;
            transition: color 0.2s ease, text-decoration-color 0.2s ease;
        }}
        .paper-authors .author-link:hover {{
            color: var(--primary-color);
            text-decoration-color: var(--primary-color);
        }}
        .paper-authors .author-link:focus-visible {{
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
            text-decoration-color: transparent;
        }}
        .paper-institutions {{ font-size: 1rem; color: #666; margin-bottom: 10px; font-weight: 400; }}
        .paper-venue {{ font-size: 1.15rem; color: #444; margin-bottom: 18px; font-weight: 600; letter-spacing: 0.4px; }}
        .author-span, .institution-span {{ margin: 0 10px; display: inline-block; }}
        sup {{ font-size: 0.7em; vertical-align: super; margin-left: 2px; color: var(--primary-color); }}

        .link-buttons {{ display: flex; justify-content: center; gap: 15px; margin-top: 15px; flex-wrap: wrap; }}
        .link-btn {{ background-color: #333; color: #fff; padding: 10px 24px; border-radius: 50px; text-decoration: none; font-weight: 600; font-size: 14px; transition: background-color 0.2s, transform 0.2s; display: inline-flex; align-items: center; gap: 8px; }}
        .link-btn:hover {{ background-color: #555; transform: translateY(-2px); }}
        .link-icon {{ width: 16px; height: 16px; fill: currentColor; }}

        .paper-footer {{ width: 100%; background-color: #fafafa; border-top: 1px solid var(--border-color); padding: 40px 20px; margin-top: 80px; text-align: center; }}
        .citation-block {{ background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 15px; text-align: left; font-family: 'Consolas', monospace; font-size: 13px; color: #555; max-width: 800px; margin: 20px auto; overflow-x: auto; white-space: pre; }}

        .back-btn {{
            position: fixed; bottom: 30px; right: 30px; z-index: 2000;
            background-color: #222; color: white; border: none; padding: 12px 24px;
            border-radius: 50px; font-size: 14px; font-family: var(--font-stack);
            font-weight: 600; cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.2s, background-color 0.2s; display: none; 
            align-items: center; gap: 8px; letter-spacing: 0.3px;
        }}
        .back-btn:hover {{ transform: translateY(-2px); background-color: #000; box-shadow: 0 8px 25px rgba(0,0,0,0.25); }}

        /* --- Page & Dataset Styles --- */
        .content-block {{ margin-bottom: 80px; width: 100%; display: flex; flex-direction: column; align-items: center; scroll-margin-top: 80px; gap: 40px; }}
        
        h2.dataset-title {{ font-family: var(--font-stack); font-size: 1.6rem; font-weight: 400; color: var(--text-title); margin-bottom: 15px; border-bottom: 3px solid var(--primary-color); padding-bottom: 8px; display: inline-block; }}
        h3.content-subtitle {{ font-size: 1.4rem; color: #444; margin-top: 0; margin-bottom: 10px; font-weight: 600; }}
        .dataset-description {{ font-size: 1.05rem; color: var(--text-secondary); max-width: 800px; text-align: left; line-height: 1.7; margin: 0 auto 30px auto; padding: 0 20px; }}
        .mlp-probing-figures {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 24px;
            margin-top: 30px;
        }}
        .mlp-probing-figures figure {{
            margin: 0;
            min-width: 0;
            text-align: center;
        }}
        .mlp-probing-figures img {{
            display: block;
            width: 100%;
            height: auto;
            background: #fff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
        }}
        .mlp-probing-figures figcaption {{
            margin-top: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.4;
        }}
        .dataset-description:has(.pca-analysis-gallery),
        .overview-desc:has(.pca-analysis-gallery),
        .dataset-description:has(.success-table-grid),
        .overview-desc:has(.success-table-grid),
        .dataset-description:has(.full-width-analysis),
        .overview-desc:has(.full-width-analysis) {{
            width: 100%;
            max-width: 1400px;
            box-sizing: border-box;
        }}
        .analysis2-subheading {{
            margin: 30px 0 8px;
            color: var(--text-title);
            font-size: 1.08rem;
        }}
        .analysis2-probe-grid {{ margin-bottom: 34px; }}
        .figure4-probe-grid {{
            width: 100%;
            max-width: 900px;
            margin: 30px auto 0;
        }}
        .pairwise-gallery {{ margin-top: 28px; }}
        .pca-analysis-gallery {{
            display: flex;
            flex-direction: column;
            gap: 28px;
        }}
        .pca-lead {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .pca-reading-guide {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 16px 20px;
            box-sizing: border-box;
            border: 1px solid #cfe3f4;
            border-left: 4px solid var(--primary-color);
            border-radius: 7px;
            background: #f7fbff;
            color: #3f5060;
            line-height: 1.6;
        }}
        .pca-case {{
            padding: 24px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background: #fff;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
        }}
        .pca-case-header {{
            display: flex;
            align-items: baseline;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }}
        .pca-case h5 {{
            margin: 0;
            color: var(--text-title);
            font-size: 1.05rem;
            line-height: 1.4;
        }}
        .pca-case-summary {{
            margin: 0 0 18px;
            color: var(--text-secondary);
            line-height: 1.6;
        }}
        .pca-media-pair {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 20px;
            align-items: start;
        }}
        .pca-media-panel {{
            min-width: 0;
            margin: 0;
        }}
        .pca-media-heading {{
            margin-bottom: 7px;
            color: #444;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .pca-media-link {{
            display: block;
            overflow: hidden;
            border: 1px solid var(--border-color);
            border-radius: 7px;
            background: #fff;
            transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
        }}
        .pca-media-link:hover {{
            border-color: var(--primary-color);
            box-shadow: 0 5px 16px rgba(0, 120, 212, 0.14);
            transform: translateY(-1px);
        }}
        .pca-media-link:focus-visible {{
            outline: 3px solid rgba(0, 120, 212, 0.35);
            outline-offset: 2px;
        }}
        .pca-media-link img {{
            display: block;
            width: 100%;
            height: auto;
        }}
        .pca-media-panel figcaption {{
            margin-top: 7px;
            color: #666;
            font-size: 0.83rem;
            line-height: 1.45;
        }}
        .pca-takeaway {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 17px 20px;
            box-sizing: border-box;
            border-radius: 7px;
            background: #f4f7f9;
            color: #38444e;
        }}
        .success-table-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 28px;
            margin-top: 26px;
        }}
        .comparison-table-pair {{
            align-items: start;
        }}
        .comparison-table-pair .table-wrap {{
            overflow-x: hidden;
        }}
        .comparison-success-table {{
            width: 100%;
            table-layout: fixed;
            font-size: clamp(8px, 0.65vw, 10px);
        }}
        .comparison-success-table th,
        .comparison-success-table td {{
            padding: 5px 2px;
        }}
        .comparison-success-table caption {{
            font-size: 0.9rem;
        }}
        .focus-ood-height,
        .focus-ood-count {{
            position: relative;
            font-weight: 700;
        }}
        .focus-ood-height {{
            box-shadow: inset 0 0 0 2px #c62828;
        }}
        .focus-ood-count {{
            box-shadow: inset 0 0 0 2px #0078d4;
        }}
        .table-focus-legend {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 16px 0 -8px;
            color: #4b5563;
            font-size: 0.9rem;
            line-height: 1.45;
        }}
        .table-focus-swatch {{
            width: 18px;
            height: 18px;
            flex: 0 0 18px;
            box-sizing: border-box;
            border-radius: 2px;
            background: #fff;
        }}
        .height-focus-swatch {{
            border: 2px solid #c62828;
        }}
        .count-focus-swatch {{
            border: 2px solid #0078d4;
        }}
        .success-table-card {{
            padding: 20px;
            border: 1px solid var(--border-color);
            border-radius: 9px;
            background: #fff;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.045);
        }}
        .success-table-card h5 {{
            margin: 0 0 14px;
            color: var(--text-title);
            font-size: 1rem;
        }}
        .success-heatmap td[data-value] {{
            transition: background-color 0.2s ease;
        }}
        .success-heatmap td.training-region {{
            box-shadow: inset 0 0 0 1.5px #d62728;
        }}
        .table-wrap {{ overflow-x: auto; }}
        .table-note {{ font-size: 12px; color: #666; margin-top: 6px; }}
        .full-width-analysis > p,
        .full-width-analysis > h5,
        .full-width-analysis > .pca-takeaway {{
            max-width: 1000px;
            margin-left: auto;
            margin-right: auto;
            box-sizing: border-box;
        }}
        .inline-carousel {{
            width: 100%;
            margin: 18px 0 30px;
        }}
        .latex-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            border-top: 1px solid #d6d6d6;
            border-bottom: 1px solid #d6d6d6;
            background: #ffffff;
        }}
        .latex-table th, .latex-table td {{
            padding: 8px 12px;
            vertical-align: middle;
            border-right: 1px solid #e2e2e2;
        }}
        .latex-table th {{
            font-weight: 600;
            color: #222;
            background: #f5f5f5;
        }}
        .latex-table td {{ color: #333; }}
        .latex-table td[data-value] {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .latex-table.heatmap td[data-value] {{ transition: background-color 0.2s ease; }}
        .latex-table tr td:last-child, .latex-table tr th:last-child {{ border-right: none; }}
        .latex-table .center {{ text-align: center; }}
        .latex-table .cmid {{ border-bottom: 1px solid #d6d6d6; }}
        .latex-table .headrule th {{ border-bottom: 1px solid #d6d6d6; }}
        .latex-table .midrule td, .latex-table .midrule th {{ border-top: 1px solid #d6d6d6; }}
        .latex-table .doublemid td, .latex-table .doublemid th {{ border-top: 1px solid #d6d6d6; }}
        .latex-table .sep-left {{ border-left: 1px solid #d6d6d6; }}
        .latex-table tbody tr:nth-child(odd) td {{ background: #ffffff; }}
        .latex-table tbody tr:hover td {{ background: #f7f7f7; }}
        .latex-table .u {{
            text-decoration: underline;
            text-decoration-thickness: 2px;
            text-underline-offset: 2px;
            text-decoration-color: #444;
        }}
        .latex-table .vlabel {{
            writing-mode: vertical-rl;
            transform: rotate(180deg);
            text-align: center;
            letter-spacing: 0.5px;
            color: #222;
        }}

        /* --- Overview Styling --- */
        .overview-container {{ width: 98%; max-width: 1600px; padding: 0 20px 100px 20px; display: none; box-sizing: border-box; margin: 0 auto; }}
        
        .abstract-section {{ max-width: 900px; margin: 0 auto 60px auto; text-align: justify; background-color: #ffffff; padding: 30px 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); border: 1px solid #f0f0f0; }}
        .abstract-title {{ text-align: center; font-weight: 700; font-size: 1.2rem; text-transform: uppercase; color: #444; margin-bottom: 15px; letter-spacing: 1px; }}
        .abstract-content {{ font-size: 1.05rem; line-height: 1.8; color: #333; }}

        /* === HIERARCHY STYLES (UPDATED) === */
        
        /* Base styles for Level 1 & 2 Headers */
        .hierarchy-bar {{
            width: 100%;
            box-sizing: border-box;
            text-align: center; 
            padding: 15px 0; 
            border-radius: 6px;
            font-family: var(--font-stack);
            margin-bottom: 30px;
            text-transform: none; 
            letter-spacing: 1px;
            font-weight: 600;
        }}

        /* LEVEL 1: Lighter Blue Shadow, Blue Border, Larger */
        .level-1-header {{
            font-size: 1.5rem;
            margin-top: 60px;
            background-color: var(--bg-level1); /* Solid Light Blue Color */
            color: var(--primary-color);
            box-shadow: none; 
            border-left: 5px solid var(--primary-color);
            border-top: none;
        }}

        /* LEVEL 2: Gray Shadow, Blue Border, Smaller */
        .level-2-header {{
            font-size: 1.25rem;
            margin-top: 30px;
            background-color: #f9f9f9;
            color: #444; 
            box-shadow: none; 
            border: 1px solid #eee;
            border-left: 5px solid var(--primary-color);
        }}

        /* LEVEL 3: Underscore Style (Content Title) */
        .level-3-header {{
            font-family: var(--font-stack);
            font-size: 1.3rem; 
            color: #222; 
            margin: 0;
            font-weight: 600;
            display: inline-block;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 6px;
        }}

        .overview-section {{ margin-bottom: 90px; width: 98%; max-width: 1600px; margin-left: auto; margin-right: auto; padding: 0 20px; box-sizing: border-box; scroll-margin-top: 80px; }}
        .overview-section-header {{ text-align: center; margin-bottom: 20px; }}
        .overview-desc {{ font-size: 1rem; color: var(--text-secondary); margin: 0 auto 30px auto; line-height: 1.6; max-width: 900px; text-align: left; }}
        .overview-action {{ text-align: center; margin-top: 30px; }}

        /* Carousel */
        .carousel-wrapper {{ position: relative; width: 100%; background: #000; border-radius: 8px; overflow: hidden; box-shadow: 0 6px 15px rgba(0,0,0,0.15); }}
        .carousel-wrapper video {{ width: 100%; display: block; height: auto; }}
        .carousel-btn {{ position: absolute; top: 50%; transform: translateY(-50%); background-color: rgba(0, 0, 0, 0.5); color: white; border: none; width: 50px; height: 50px; border-radius: 50%; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; font-size: 24px; transition: background-color 0.2s; opacity: 0; }}
        .carousel-wrapper:hover .carousel-btn {{ opacity: 1; }}
        .carousel-btn:hover {{ background-color: rgba(0, 0, 0, 0.8); }}
        .carousel-btn.left {{ left: 20px; }}
        .carousel-btn.right {{ right: 20px; }}
        .slide-counter {{ position: absolute; bottom: 20px; right: 20px; background-color: rgba(0,0,0,0.6); color: white; padding: 5px 10px; border-radius: 4px; font-size: 13px; pointer-events: none; font-weight: 600; }}
        .carousel-dots {{
            display: flex;
            justify-content: center;
            gap: 6px;
            margin-top: 12px;
            padding: 4px 6px;
            overflow-x: auto;
            overflow-y: hidden;
            scrollbar-width: thin;
            scrollbar-color: #8fbce6 transparent;
            white-space: nowrap;
        }}
        .carousel-dots::-webkit-scrollbar {{ height: 6px; }}
        .carousel-dots::-webkit-scrollbar-thumb {{ background: #8fbce6; border-radius: 999px; }}
        .carousel-dots::-webkit-scrollbar-track {{ background: transparent; }}
        .carousel-dot {{
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #d7ebfb;
            cursor: pointer;
            flex: 0 0 auto;
            padding: 0;
            border: none;
        }}
        .carousel-dot:hover {{ background: #b8daf5; }}
        .carousel-dot.active {{
            background: var(--primary-color);
            transform: scale(1.15);
        }}

        .btn-view-all {{ background-color: var(--primary-color); color: #fff; border: 2px solid var(--primary-color); padding: 10px 30px; border-radius: 50px; cursor: pointer; font-size: 13px; font-weight: 700; text-decoration: none; transition: all 0.2s; text-transform: uppercase; font-family: var(--font-stack); display: inline-block; letter-spacing: 0.5px; }}
        .btn-view-all:hover {{ background-color: var(--primary-hover); border-color: var(--primary-hover); color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }}

        /* Cards */
        .container {{ display: flex; flex-direction: column; align-items: center; gap: 50px; padding-bottom: 100px; width: 98%; max-width: 1600px; box-sizing: border-box; padding-top: 20px; }}
        .card {{ background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; border: 1px solid #e0e0e0; display: block; transition: transform 0.2s ease; }}
        
        /* --- FIX: Ensure videos inside cards do not exceed screen width --- */
        .card video {{ width: 100%; height: auto; display: block; }}
        
        .caption-box {{ padding: 25px; background-color: #fff; border-top: 1px solid #eee; font-family: 'Consolas', 'Monaco', monospace; font-size: 14px; line-height: 1.6; white-space: pre-wrap; color: #333; }}
        .caption-line {{ display: block; }}
        
        .page-view {{ display: none; width: 100%; flex-direction: column; align-items: center; }}
        .page-view.active {{ display: flex; }}

        /* Collapsed Sidebar */
        body.sidebar-collapsed .dataset-nav {{ width: 50px; padding-left: 5px; padding-right: 5px; }}
        body.sidebar-collapsed .main-content {{ margin-left: 50px; width: calc(100% - 50px); }}
        body.sidebar-collapsed .dataset-btn, body.sidebar-collapsed .nav-subcategory {{ opacity: 0; pointer-events: none; white-space: nowrap; }}
        body.sidebar-collapsed #sidebar-toggle {{ background-color: #e6e6e6; }}

        @media (max-width: 800px) {{
            .mlp-probing-figures {{ grid-template-columns: 1fr; }}
            .pca-media-pair {{ grid-template-columns: 1fr; }}
            .success-table-grid {{ grid-template-columns: 1fr; }}
            .pca-case {{ padding: 18px 14px; }}
        }}
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const toggleBtn = document.getElementById('sidebar-toggle');
            const body = document.body;
            
            const overviewVideosMap = {overview_videos_map_json};
            const datasetToPageMap = {dataset_to_page_map_json}; 
            const pageToFirstDatasetMap = {page_to_first_dataset_map_json};
            const pagesData = {pages_data_json};

            const carouselIndices = {{}};

            toggleBtn.addEventListener('click', () => {{
                body.classList.toggle('sidebar-collapsed');
                toggleBtn.innerHTML = body.classList.contains('sidebar-collapsed') ? "&#9776;" : "&laquo;";
            }});

            let activePage = "Overview"; 
            let activeDatasetName = null; 
            const overviewContainer = document.getElementById('overview-container');
            const cardsContainer = document.getElementById('cards-container'); 
            const backBtn = document.getElementById('back-to-overview');

            let observer = new IntersectionObserver((entries, observer) => {{
                entries.forEach(entry => {{
                    let video = entry.target;
                    
                    if (entry.isIntersecting) {{
                        if (video.dataset.src) {{
                            video.src = video.dataset.src;
                            video.load();
                            video.removeAttribute('data-src');
                        }}
                        var playPromise = video.play();
                        if (playPromise !== undefined) {{
                            playPromise.catch(error => {{ }});
                        }}
                    }} else {{
                        video.pause();
                    }}
                }});
            }}, {{ rootMargin: "200px" }});

            function handleScrollSpy() {{
                if (activePage === "Overview") return;
                const blocks = cardsContainer.querySelectorAll('.content-block');
                
                blocks.forEach(block => {{
                    const rect = block.getBoundingClientRect();
                    if (rect.top >= -50 && rect.top < 300) {{
                        const id = block.id.replace('dataset-block-', '');
                        if (id !== activeDatasetName) {{
                            activeDatasetName = id;
                            updateSidebarHighlight();
                        }}
                    }}
                }});
            }}

            window.addEventListener('scroll', handleScrollSpy);

            function updateCarouselDots(datasetName, activeIndex) {{
                const dotsWrap = document.getElementById('carousel-dots-' + datasetName);
                if (!dotsWrap) return;

                const dots = dotsWrap.querySelectorAll('.carousel-dot');
                dots.forEach((dot, idx) => {{
                    dot.classList.toggle('active', idx === activeIndex);
                }});

                if (dots[activeIndex]) {{
                    dots[activeIndex].scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});
                }}
            }}

            function applyHeatmap() {{
                const tables = document.querySelectorAll('table.heatmap-generalization');
                tables.forEach(table => {{
                    const applyGroup = (groupName, exponent) => {{
                        const cells = Array.from(
                            table.querySelectorAll(`td[data-group="${{groupName}}"][data-value]`)
                        );
                        const values = cells
                            .map(cell => parseFloat(cell.dataset.value))
                            .filter(value => !Number.isNaN(value));
                        if (!values.length) return;

                        const min = Math.min(...values);
                        const max = Math.max(...values);
                        const denom = max - min || 1;
                        const low = [236, 242, 234];
                        const high = [252, 228, 230];

                        cells.forEach(cell => {{
                            const value = parseFloat(cell.dataset.value);
                            if (Number.isNaN(value)) return;
                            const t = Math.pow((value - min) / denom, exponent);
                            const r = Math.round(low[0] + (high[0] - low[0]) * t);
                            const g = Math.round(low[1] + (high[1] - low[1]) * t);
                            const b = Math.round(low[2] + (high[2] - low[2]) * t);
                            cell.style.backgroundColor = `rgb(${{r}}, ${{g}}, ${{b}})`;
                        }});
                    }};

                    applyGroup('nar', 1.15);
                    applyGroup('ar', 1.4);
                }});

                document.querySelectorAll('table.success-heatmap td[data-value]').forEach(cell => {{
                    const value = Math.max(0, Math.min(100, parseFloat(cell.dataset.value)));
                    if (Number.isNaN(value)) return;
                    const t = value / 100;
                    const low = [248, 180, 180];
                    const high = [180, 230, 185];
                    const r = Math.round(low[0] + (high[0] - low[0]) * t);
                    const g = Math.round(low[1] + (high[1] - low[1]) * t);
                    const b = Math.round(low[2] + (high[2] - low[2]) * t);
                    cell.style.backgroundColor = `rgb(${{r}}, ${{g}}, ${{b}})`;
                }});
            }}

            window.setCarouselIndex = function(datasetName, newIndex) {{
                const videoList = overviewVideosMap[datasetName];
                if (!videoList || videoList.length === 0) return;

                if (carouselIndices[datasetName] === undefined) {{
                    carouselIndices[datasetName] = 0;
                }}

                if (newIndex >= videoList.length) newIndex = 0;
                if (newIndex < 0) newIndex = videoList.length - 1;

                carouselIndices[datasetName] = newIndex;

                const wrapper = document.getElementById('carousel-' + datasetName);
                const videoEl = wrapper.querySelector('video');
                const counterEl = wrapper.querySelector('.slide-counter');

                videoEl.src = videoList[newIndex];
                videoEl.play();

                if (counterEl) {{
                    counterEl.innerText = `${{newIndex + 1}} / ${{videoList.length}}`;
                }}

                updateCarouselDots(datasetName, newIndex);
            }};

            window.moveCarousel = function(datasetName, direction) {{
                const videoList = overviewVideosMap[datasetName];
                if (!videoList || videoList.length === 0) return;

                if (carouselIndices[datasetName] === undefined) {{
                    carouselIndices[datasetName] = 0;
                }}

                let newIndex = carouselIndices[datasetName] + direction;
                window.setCarouselIndex(datasetName, newIndex);
            }};

            window.setInlineCarousel = function(wrapper, newIndex) {{
                if (!wrapper) return;
                const videoList = JSON.parse(decodeURIComponent(wrapper.dataset.videos || "%5B%5D"));
                if (!videoList.length) return;

                if (newIndex >= videoList.length) newIndex = 0;
                if (newIndex < 0) newIndex = videoList.length - 1;
                wrapper.dataset.index = newIndex;

                const videoEl = wrapper.querySelector("video");
                const counterEl = wrapper.querySelector(".slide-counter");
                videoEl.dataset.src = videoList[newIndex];
                videoEl.src = videoList[newIndex];
                const playPromise = videoEl.play();
                if (playPromise !== undefined) playPromise.catch(() => {{}});

                if (counterEl) counterEl.innerText = `${{newIndex + 1}} / ${{videoList.length}}`;
                wrapper.querySelectorAll(".carousel-dot").forEach((dot, index) => {{
                    dot.classList.toggle("active", index === newIndex);
                }});
            }};

            window.moveInlineCarousel = function(button, direction) {{
                const wrapper = button.closest(".inline-carousel");
                if (!wrapper) return;
                const currentIndex = Number.parseInt(wrapper.dataset.index || "0", 10);
                window.setInlineCarousel(wrapper, currentIndex + direction);
            }};

            // --- NAVIGATION HELPERS ---
            function setRoute(pageId, datasetName) {{
                activePage = pageId;
                activeDatasetName = datasetName;
                
                const hashValue = datasetName ? datasetName : pageId;
                if (window.location.hash !== '#' + encodeURIComponent(hashValue)) {{
                    window.history.pushState(null, null, '#' + encodeURIComponent(hashValue));
                }}
                
                updateView();
                
                if (datasetName) {{
                    setTimeout(() => {{
                        const targetCard = document.getElementById('dataset-block-' + datasetName);
                        if (targetCard) {{
                            targetCard.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        }}
                    }}, 10);
                }} else {{
                    window.scrollTo(0, 0);
                }}
            }}

            window.navigateToDataset = function(datasetName) {{
                const targetPage = datasetToPageMap[datasetName];
                if (!targetPage) return;
                setRoute(targetPage, datasetName);
            }};

            window.navigateToGroup = function(pageId) {{
                setRoute(pageId, null);
            }};

            window.navigateToSection = function(sectionName) {{
                activePage = "Overview";
                activeDatasetName = sectionName;

                if (window.location.hash !== '#' + encodeURIComponent(sectionName)) {{
                    window.history.pushState(null, null, '#' + encodeURIComponent(sectionName));
                }}

                updateView();

                setTimeout(() => {{
                    const targetSection = document.getElementById('section-' + sectionName);
                    if (targetSection) {{
                        targetSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }}, 10);
            }};

            window.backToOverview = function() {{
                const sectionDataset = activeDatasetName || pageToFirstDatasetMap[activePage] || null;
                activePage = "Overview";
                activeDatasetName = sectionDataset;

                if (window.location.hash !== '#Overview') {{
                    window.history.pushState(null, null, '#Overview');
                }}

                updateView();

                if (sectionDataset) {{
                    setTimeout(() => {{
                        const targetSection = document.getElementById('section-' + sectionDataset);
                        if (targetSection) {{
                            targetSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        }} else {{
                            window.scrollTo(0, 0);
                        }}
                    }}, 10);
                }} else {{
                    window.scrollTo(0, 0);
                }}
            }};

            function updateSidebarHighlight() {{
                const datasetBtns = document.querySelectorAll('.dataset-btn');
                datasetBtns.forEach(btn => {{
                    const targetPage = btn.dataset.target;
                    const targetDataset = btn.dataset.dataset; 

                    btn.classList.remove('active');

                    if (activePage === "Overview") {{
                         if (targetPage === "Overview" || btn.dataset.section === activeDatasetName) {{
                             btn.classList.add('active');
                         }}
                    }} 
                    else if (btn.classList.contains('level-2')) {{
                        if (targetPage === activePage) {{
                            btn.classList.add('active');
                        }}
                    }} 
                    else if (btn.classList.contains('level-3')) {{
                        if (targetDataset === activeDatasetName) {{
                            btn.classList.add('active');
                        }}
                    }}
                }});
            }}

            function renderPage(pageId) {{
                cardsContainer.innerHTML = ""; // Clear memory!
                
                const data = pagesData[pageId];
                if (!data) return;

                const headerDiv = document.createElement('div');
                headerDiv.className = data.is_text_only ? "hierarchy-bar level-1-header" : "hierarchy-bar level-2-header";
                headerDiv.style.marginBottom = "40px";
                headerDiv.innerText = data.title;
                cardsContainer.appendChild(headerDiv);

                // --- Render Group Description (only if it exists) ---
                if (data.description) {{
                    const groupDescEl = document.createElement('div');
                    groupDescEl.className = "dataset-description";
                    groupDescEl.style.marginBottom = "30px";
                    groupDescEl.innerHTML = data.description;
                    cardsContainer.appendChild(groupDescEl);
                }}

                data.blocks.forEach(block => {{
                    const blockDiv = document.createElement('div');
                    blockDiv.className = "content-block";
                    blockDiv.id = "dataset-block-" + block.id;

                    if (data.is_group) {{
                         const titleEl = document.createElement('h3');
                         titleEl.className = "level-3-header";
                         titleEl.style.fontSize = "1.5rem";
                         titleEl.style.marginBottom = "20px";
                         titleEl.innerText = block.id;
                         blockDiv.appendChild(titleEl);
                    }}

                    if (block.description) {{
                        const descEl = document.createElement('div');
                        descEl.className = "dataset-description";
                        descEl.innerHTML = block.description;
                        blockDiv.appendChild(descEl);
                    }}

                    block.videos.forEach(vid => {{
                        const cardDiv = document.createElement('div');
                        cardDiv.className = "card";
                        
                        const videoTag = document.createElement('video');
                        videoTag.className = "lazy";
                        videoTag.setAttribute('data-src', vid.src);
                        videoTag.preload = "none";
                        videoTag.controls = true;
                        videoTag.autoplay = true;
                        videoTag.loop = true;
                        videoTag.muted = true;
                        videoTag.playsInline = true;
                        
                        cardDiv.appendChild(videoTag);

                        if (vid.caption) {{
                            const tempDiv = document.createElement('div');
                            tempDiv.innerHTML = vid.caption; 
                            while (tempDiv.firstChild) {{
                                cardDiv.appendChild(tempDiv.firstChild);
                            }}
                        }}

                        blockDiv.appendChild(cardDiv);
                    }});

                    cardsContainer.appendChild(blockDiv);
                }});

                const newVideos = cardsContainer.querySelectorAll('video.lazy');
                newVideos.forEach(v => observer.observe(v));
            }}

            function updateView() {{
                updateSidebarHighlight();

                if (activePage === "Overview") {{
                    cardsContainer.style.display = "none";
                    cardsContainer.innerHTML = ""; 
                    
                    overviewContainer.style.display = "block";
                    backBtn.style.display = "none"; 
                    
                    const overviewVideos = overviewContainer.querySelectorAll('video.lazy');
                    overviewVideos.forEach(v => observer.observe(v));

                }} else {{
                    overviewContainer.style.display = "none";
                    backBtn.style.display = "flex"; 
                    cardsContainer.style.display = "flex"; 

                    renderPage(activePage);
                }}

                applyHeatmap();
            }}

            // --- HANDLE INITIAL LOAD VIA URL ---
            function loadStateFromHash() {{
                const hash = window.location.hash.substring(1); 
                const decodedHash = decodeURIComponent(hash);
                
                if (!decodedHash || decodedHash === "Overview") {{
                    activePage = "Overview";
                    activeDatasetName = null;
                }} else {{
                    const overviewSection = document.getElementById('section-' + decodedHash);
                    if (overviewSection) {{
                        activePage = "Overview";
                        activeDatasetName = decodedHash;
                    }} else if (datasetToPageMap[decodedHash]) {{
                        activePage = datasetToPageMap[decodedHash];
                        activeDatasetName = decodedHash;
                    }} else if (pagesData[decodedHash]) {{
                        activePage = decodedHash;
                        activeDatasetName = null;
                    }} else {{
                        activePage = "Overview";
                        activeDatasetName = null;
                    }}
                }}
                
                updateView();

                if (activePage === "Overview" && activeDatasetName) {{
                    setTimeout(() => {{
                        const targetSection = document.getElementById('section-' + activeDatasetName);
                        if (targetSection) {{
                            targetSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        }}
                    }}, 100);
                }} else if (activeDatasetName && activePage !== "Overview") {{
                    setTimeout(() => {{
                        const targetCard = document.getElementById('dataset-block-' + activeDatasetName);
                        if (targetCard) {{
                            targetCard.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        }}
                    }}, 100);
                }}
            }}

            window.addEventListener('hashchange', loadStateFromHash);

            document.querySelectorAll('.dataset-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    if (window.innerWidth < 768) {{
                        body.classList.add('sidebar-collapsed');
                        toggleBtn.innerHTML = "&#9776;";
                    }}
                }});
            }});

            loadStateFromHash();
        }});
    </script>
</head>
<body>

    <button id="sidebar-toggle" title="Toggle Sidebar">&laquo;</button>

    <div class="dataset-nav">
        <button class="dataset-btn overview-btn" data-target="Overview" onclick="backToOverview()">Overview</button>
        {dataset_nav_buttons}
    </div>

    <div class="main-content">
        <header class="paper-header">
            <h1 class="paper-title">{paper_title}</h1>
            
            <div class="paper-meta">
                <div class="paper-authors">{authors_html}</div>
                <div class="paper-institutions">{institutions_html}</div>
                <div class="paper-venue">Anonymous 2026</div>
                <div class="link-buttons">{link_buttons_html}</div>
            </div>
        </header>

        <button id="back-to-overview" class="back-btn" onclick="backToOverview()">
            <span>&larr;</span> Back to Overview
        </button>

        <div id="overview-container" class="overview-container">
            <div class="abstract-section">
                <div class="abstract-title">Abstract</div>
                <div class="abstract-content">
                    {abstract_text}
                </div>
            </div>
            {overview_html}
        </div>

        <div id="cards-container" class="container"></div>

        <div class="paper-footer">
            <div style="font-weight: 600; margin-bottom: 10px;">Citation</div>
            <div class="citation-block">
@article{{CoGDiT,
  title={{{paper_title}}},
  author={{{authors_string}}},
  journal={{Conference Name}},
  year={{2026}}
}}
            </div>
        </div>
    </div>
    
    <div id="clustrmaps-widget-container">
        <script type="text/javascript" id="clustrmaps" src="//clustrmaps.com/map_v2.js?d=EakYmNC57ROvcmK4DT-NyOywRN9Y4G9Bh0BWI7qmXJ8&cl=ffffff&w=a"></script>
    </div>

</body>
</html>
"""

def sort_key(filepath):
    basename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(basename)[0]
    
    if name_without_ext.isdigit():
        return (0, int(name_without_ext))
    return (1, name_without_ext)


def generate_single_index(input_folder):
    if not os.path.exists(input_folder):
        print(f"Error: Input directory '{input_folder}' not found.")
        return

    # 1. Scan available datasets
    found_datasets = set([d for d in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, d))])
    
    if not found_datasets:
        print(f"No datasets found inside {input_folder}")
        return

    # --- PROCESS AUTHORS & INSTITUTIONS ---
    authors_html = ""
    for i, (name, indices, author_url) in enumerate(AUTHORS):
        sup_str = ",".join([str(idx + 1) for idx in indices])
        if author_url:
            author_label = f'<a class="author-link" href="{author_url}" target="_blank" rel="noopener">{name}</a>'
        else:
            author_label = name
        authors_html += f'<span class="author-span">{author_label}<sup>{sup_str}</sup></span>'
        if i < len(AUTHORS) - 1:
            authors_html += ", "
    
    authors_string = " and ".join([a[0] for a in AUTHORS])

    institutions_html = ""
    for i, inst in enumerate(INSTITUTIONS):
        institutions_html += f'<span class="institution-span"><sup>{i+1}</sup>{inst}</span>'
        if i < len(INSTITUTIONS) - 1:
            institutions_html += ", "

    # --- PROCESS LINKS ---
    link_buttons_html = ""
    if ARXIV_LINK:
        paper_icon = '<svg class="link-icon" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>'
        link_buttons_html += f'<a href="{ARXIV_LINK}" target="_blank" class="link-btn">{paper_icon} arXiv</a>'
    
    if CODE_LINK:
        code_icon = '<svg class="link-icon" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>'
        link_buttons_html += f'<a href="{CODE_LINK}" target="_blank" class="link-btn">{code_icon} GitHub</a>'

    # --- FLATTEN CONFIG FOR PAGES ---
    pages = []
    used_datasets = set()
    dataset_to_page_map = {} 
    page_to_first_dataset_map = {}
    
    overview_structure = [] 

    dataset_nav_html = ""

    # A. Process Configured Categories
    for category_name, items in SIDEBAR_CONFIG:
        # Every configured category is a clickable level-2 sidebar title.
        # Its children, when present, are level-3 titles.
        if not items and category_name not in DATASET_DESCRIPTIONS and category_name not in found_datasets:
            continue

        dataset_nav_html += f'<button class="dataset-btn level-2" data-target="{category_name}" data-section="{category_name}" onclick="navigateToSection(\'{category_name}\')">{category_name}</button>\n'
        cat_subitems = []

        if not items:
            category_video_files = sorted(
                glob.glob(os.path.join(input_folder, category_name, "*.mp4")),
                key=sort_key,
            )
            has_category_videos = bool(category_video_files)
            pages.append({
                "id": category_name,
                "title": category_name,
                "datasets": [category_name],
                "is_group": False,
                "is_text_only": not has_category_videos
            })
            page_to_first_dataset_map[category_name] = category_name
            used_datasets.add(category_name)
            dataset_to_page_map[category_name] = category_name
            category_subitems = []
            if has_category_videos:
                category_subitems.append((category_name, [category_name], False))
            overview_structure.append((category_name, category_subitems))
            continue

        # A category may have its own videos as well as child sections.
        # Put the category-level videos first in the overview.
        category_video_files = sorted(
            glob.glob(os.path.join(input_folder, category_name, "*.mp4")),
            key=sort_key,
        )
        if category_video_files and category_name not in used_datasets:
            pages.append({
                "id": category_name,
                "title": category_name,
                "datasets": [category_name],
                "is_group": False
            })
            page_to_first_dataset_map[category_name] = category_name
            dataset_to_page_map[category_name] = category_name
            used_datasets.add(category_name)
            cat_subitems.append((category_name, [category_name], False))

        for item in items:
            is_group = False
            sub_name = ""
            sub_datasets = []

            if isinstance(item, tuple):
                if len(item) == 2 and isinstance(item[1], list):
                    sub_name, sub_datasets = item
                    if not sub_datasets and sub_name in DATASET_DESCRIPTIONS:
                        is_group = False
                        sub_datasets = [sub_name]
                    else:
                        is_group = True
                elif len(item) == 1:
                    sub_name = item[0]
                    sub_datasets = [sub_name]
            elif isinstance(item, str):
                sub_name = item
                sub_datasets = [sub_name]

            valid_subs = [
                d for d in sub_datasets
                if d in found_datasets or d in DATASET_DESCRIPTIONS
            ]

            if not valid_subs:
                continue

            if is_group:
                dataset_nav_html += f'<button class="dataset-btn level-3" data-target="{sub_name}" data-section="{sub_name}" onclick="navigateToSection(\'{sub_name}\')">{sub_name}</button>\n'
                pages.append({
                    "id": sub_name,
                    "title": sub_name,
                    "datasets": valid_subs,
                    "is_group": True
                })
                page_to_first_dataset_map[sub_name] = valid_subs[0]
                dataset_to_page_map[sub_name] = sub_name

                for d_name in valid_subs:
                    dataset_nav_html += f'<button class="dataset-btn level-3" data-target="{sub_name}" data-dataset="{d_name}" data-section="{d_name}" onclick="navigateToSection(\'{d_name}\')">{d_name}</button>\n'
                    used_datasets.add(d_name)
                    dataset_to_page_map[d_name] = sub_name
            else:
                d_name = valid_subs[0]
                dataset_nav_html += f'<button class="dataset-btn level-3" data-target="{category_name}" data-dataset="{d_name}" data-section="{d_name}" onclick="navigateToSection(\'{d_name}\')">{d_name}</button>\n'
                pages.append({
                    "id": d_name,
                    "title": d_name,
                    "datasets": [d_name],
                    "is_group": False
                })
                page_to_first_dataset_map[d_name] = d_name
                used_datasets.add(d_name)
                dataset_to_page_map[d_name] = d_name

            cat_subitems.append((sub_name, valid_subs, is_group))

        if cat_subitems or category_name in DATASET_DESCRIPTIONS:
            overview_structure.append((category_name, cat_subitems))

    # B. Process "Others"
    remaining_datasets = sorted(list(found_datasets - used_datasets))
    if remaining_datasets:
        dataset_nav_html += '<button class="dataset-btn level-2" data-target="Others" data-section="Others" onclick="navigateToSection(\'Others\')">Others</button>\n'
        others_subitems = []
        for d_name in remaining_datasets:
            pages.append({
                "id": d_name,
                "title": d_name,
                "datasets": [d_name],
                "is_group": False
            })
            dataset_nav_html += f'<button class="dataset-btn level-3" data-target="Others" data-dataset="{d_name}" data-section="{d_name}" onclick="navigateToSection(\'{d_name}\')">{d_name}</button>\n'
            dataset_to_page_map[d_name] = d_name
            page_to_first_dataset_map[d_name] = d_name
            others_subitems.append((d_name, [d_name], False))

        overview_structure.append(("Others", others_subitems))

    # --- GENERATE OVERVIEW HTML ---
    overview_videos_map = {} 
    
    overview_html = ""
    for category_name, sub_items in overview_structure:
        overview_html += f'''
        <div class="hierarchy-bar level-1-header" id="section-{category_name}">
            {category_name}
        </div>
        '''

        category_desc = DATASET_DESCRIPTIONS.get(category_name, "")
        if category_desc:
            overview_html += (
                f'<div class="dataset-description" style="margin-bottom: 30px; text-align: left;">'
                f'{category_desc}'
                f'</div>'
            )
        
        for sub_name, d_list, is_group in sub_items:
            sub_header_id = f' id="section-{sub_name}"' if is_group else ""
            overview_html += f'''
            <div class="hierarchy-bar level-2-header"{sub_header_id}>
                {sub_name}
            </div>
            '''
            
            # Only render group description in overview if it IS a group
            if is_group:
                group_desc = DATASET_DESCRIPTIONS.get(sub_name, "")
                if group_desc:
                    overview_html += f'<div class="dataset-description" style="margin-bottom: 30px; text-align: left;">{group_desc}</div>'

            for d_name in d_list:
                d_path = os.path.join(input_folder, d_name)
                files = (
                    []
                    if d_name in MANUALLY_EMBEDDED_VIDEO_SECTIONS
                    else sorted(glob.glob(os.path.join(d_path, "*.mp4")), key=sort_key)
                )
                rel_files = [os.path.join(input_folder, d_name, os.path.basename(f)) for f in files]
                overview_videos_map[d_name] = rel_files

                desc = DATASET_DESCRIPTIONS.get(d_name, "")

                if not rel_files:
                    if not desc:
                        continue

                    header_html = ""
                    if is_group:
                        header_html = f'''
                        <div class="overview-section-header">
                            <h4 class="level-3-header">{d_name}</h4>
                        </div>
                        '''

                    section_html = f"""
                    <div class="overview-section" id="section-{d_name}">
                        {header_html}
                        <div class="overview-desc">{desc}</div>
                    </div>
                    """
                    overview_html += section_html
                    continue

                first_video = rel_files[0]
                total_count = len(rel_files)
                
                header_html = ""
                if is_group:
                    header_html = f'''
                    <div class="overview-section-header">
                        <h4 class="level-3-header">{d_name}</h4>
                    </div>
                    '''

                dots_html = "".join(
                    [
                        f"<button class=\"carousel-dot{' active' if i == 0 else ''}\" onclick=\"setCarouselIndex('{d_name}', {i})\" aria-label=\"Slide {i + 1}\"></button>"
                        for i in range(total_count)
                    ]
                )
                
                section_html = f"""
                <div class="overview-section" id="section-{d_name}">
                    {header_html}
                    <div class="overview-desc">{desc}</div>
                    
                    <div class="carousel-wrapper" id="carousel-{d_name}">
                        <button class="carousel-btn left" onclick="moveCarousel('{d_name}', -1)">&#10094;</button>
                        <video class="lazy" data-src="{first_video}" preload="none" muted autoplay loop playsinline></video>
                        <button class="carousel-btn right" onclick="moveCarousel('{d_name}', 1)">&#10095;</button>
                        <div class="slide-counter">1 / {total_count}</div>
                    </div>

                    <div class="carousel-dots" id="carousel-dots-{d_name}">
                        {dots_html}
                    </div>
                    
                    <div class="overview-action">
                        <button class="btn-view-all" onclick="navigateToDataset('{d_name}')">View Full Examples &rarr;</button>
                    </div>
                </div>
                """
                overview_html += section_html

    # --- GATHER CONTENT DATA ---
    pages_data = {}
    
    for page in pages:
        page_id = page["id"]
        
        # --- FIXED: Only set group description if it IS a group ---
        if page["is_group"]:
            group_description = DATASET_DESCRIPTIONS.get(page_id, "")
        else:
            group_description = ""
        
        current_page_data = {
            "title": page["title"],
            "description": group_description,
            "is_group": page["is_group"],
            "is_text_only": page.get("is_text_only", False),
            "blocks": []
        }
        
        for d_name in page["datasets"]:
            dataset_path = os.path.join(input_folder, d_name)
            mp4_files = (
                []
                if d_name in MANUALLY_EMBEDDED_VIDEO_SECTIONS
                else sorted(glob.glob(os.path.join(dataset_path, "*.mp4")), key=sort_key)
            )
            desc = DATASET_DESCRIPTIONS.get(d_name, "")

            block_data = {
                "id": d_name,
                "description": desc,
                "videos": []
            }
            
            for mp4_path in mp4_files:
                filename = os.path.basename(mp4_path)
                relative_video_path = os.path.join(input_folder, d_name, filename)
                
                json_filename = filename.replace(".mp4", ".json")
                json_path = os.path.join(dataset_path, json_filename)
                
                caption_html_str = ""
                if os.path.exists(json_path):
                    caption_html_str += '<div class="caption-box">'
                    try:
                        with open(json_path, 'r') as jf:
                            data = json.load(jf)
                            if isinstance(data, list):
                                for line in data:
                                    text = line.get('text', '')
                                    color = line.get('color', [0, 0, 0]) 
                                    hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                                    caption_html_str += f'<span class="caption-line" style="color: {hex_color};">{text}</span>'
                    except Exception:
                        pass
                    caption_html_str += '</div>'
                
                block_data["videos"].append({
                    "src": relative_video_path,
                    "caption": caption_html_str
                })
            
            current_page_data["blocks"].append(block_data)
        
        pages_data[page_id] = current_page_data

    # --- FINALIZE ---
    dataset_descriptions_json = json.dumps(DATASET_DESCRIPTIONS)
    overview_videos_map_json = json.dumps(overview_videos_map)
    dataset_to_page_map_json = json.dumps(dataset_to_page_map)
    page_to_first_dataset_map_json = json.dumps(page_to_first_dataset_map)
    pages_data_json = json.dumps(pages_data)

    final_html = HTML_TEMPLATE.format(
        paper_title=PAPER_TITLE,
        authors_html=authors_html,
        institutions_html=institutions_html,
        authors_string=authors_string,
        abstract_text=ABSTRACT_TEXT,
        link_buttons_html=link_buttons_html,
        dataset_nav_buttons=dataset_nav_html,
        overview_html=overview_html,
        dataset_descriptions_json=dataset_descriptions_json,
        overview_videos_map_json=overview_videos_map_json,
        dataset_to_page_map_json=dataset_to_page_map_json,
        page_to_first_dataset_map_json=page_to_first_dataset_map_json,
        pages_data_json=pages_data_json,
        dataset_category_map_json="{}" 
    )

    output_path = "./index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"\nSuccessfully generated dashboard at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile all datasets into a single HTML dashboard.")
    parser.add_argument("--input_folder", type=str, default="./video", help="Path to the folder containing dataset subdirectories.")
    
    args = parser.parse_args()
    
    generate_single_index(args.input_folder)
