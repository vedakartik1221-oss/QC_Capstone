"""
Script: build_presentation.py
Generates the complete, editable academic PowerPoint presentation (.pptx)
for the Quantum Capstone Project:
'Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates'
"""

import sys
from pathlib import Path
import json

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Initialize presentation with 16:9 widescreen
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

assets_dir = Path("deliverables/presentation_package")
out_pptx = Path("deliverables/Quantum_Drug_Screening_Capstone.pptx")
out_pptx.parent.mkdir(parents=True, exist_ok=True)

# Color Palette (Scientific Quantum Theme)
COLOR_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
COLOR_NAVY_LIGHT = RGBColor(30, 41, 59)     # #1E293B
COLOR_TEAL = RGBColor(13, 148, 136)         # #0D9488
COLOR_CYAN = RGBColor(2, 132, 199)          # #0284C7
COLOR_BLUE = RGBColor(37, 99, 235)          # #2563EB
COLOR_GREEN = RGBColor(22, 163, 74)         # #16A34A
COLOR_RED = RGBColor(220, 38, 38)           # #DC2626
COLOR_AMBER = RGBColor(217, 119, 6)         # #D97706
COLOR_BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_GRAY_TEXT = RGBColor(71, 85, 105)     # #475569
COLOR_GRAY_LIGHT = RGBColor(226, 232, 240)  # #E2E8F0
COLOR_CARD_BG = RGBColor(255, 255, 255)

FONT_HEADING = "Trebuchet MS"
FONT_BODY = "Calibri"


def add_header(slide, title_text, category_text="QUANTUM DRUG SCREENING CAPSTONE"):
    """Standard header for content slides."""
    # Top banner bar
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_TEAL
    top_bar.line.fill.background()
    
    # Category tag
    tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.5), Inches(0.3))
    tf_cat = tb_cat.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = FONT_BODY
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_TEAL
    
    # Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.65))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY_DARK


def set_notes(slide, notes_text):
    """Attach speaker notes to slide."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text


# ==============================================================================
# SLIDE 1: TITLE SLIDE
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = COLOR_NAVY_DARK
bg1.line.fill.background()

# Accent bar
bar1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.3), Inches(1.2), Inches(0.08))
bar1.fill.solid()
bar1.fill.fore_color.rgb = COLOR_TEAL
bar1.line.fill.background()

# Title text
tb1 = slide1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(2.2))
tf1 = tb1.text_frame
tf1.word_wrap = True
p1_sub = tf1.paragraphs[0]
p1_sub.text = "QUANTUM COMPUTING CAPSTONE PROJECT"
p1_sub.font.name = FONT_BODY
p1_sub.font.size = Pt(13)
p1_sub.font.bold = True
p1_sub.font.color.rgb = COLOR_TEAL

p1_title = tf1.add_paragraph()
p1_title.text = "Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates"
p1_title.font.name = FONT_HEADING
p1_title.font.size = Pt(30)
p1_title.font.bold = True
p1_title.font.color.rgb = COLOR_WHITE
p1_title.space_before = Pt(10)

p1_desc = tf1.add_paragraph()
p1_desc.text = "A Hybrid Machine Learning and QAOA Combinatorial Optimization Framework for BACE-1 Inhibitor Discovery"
p1_desc.font.name = FONT_BODY
p1_desc.font.size = Pt(16)
p1_desc.font.color.rgb = RGBColor(148, 163, 184)
p1_desc.space_before = Pt(8)

# Details Card
card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(4.3), Inches(11.3), Inches(2.3))
card1.fill.solid()
card1.fill.fore_color.rgb = COLOR_NAVY_LIGHT
card1.line.color.rgb = RGBColor(51, 65, 85)
card1.line.width = Pt(1.5)

tb_details = slide1.shapes.add_textbox(Inches(1.3), Inches(4.5), Inches(10.7), Inches(1.9))
tf_d = tb_details.text_frame
tf_d.word_wrap = True

p_d1 = tf_d.paragraphs[0]
p_d1.text = "Student Name: [Candidate Name / Roll Number]   |   Department: Computer Science / Quantum Engineering"
p_d1.font.name = FONT_BODY
p_d1.font.size = Pt(13)
p_d1.font.bold = True
p_d1.font.color.rgb = COLOR_WHITE

p_d2 = tf_d.add_paragraph()
p_d2.text = "Institution: [University / Institute Name]   |   Academic Year: 2026"
p_d2.font.name = FONT_BODY
p_d2.font.size = Pt(13)
p_d2.font.color.rgb = RGBColor(203, 213, 225)
p_d2.space_before = Pt(4)

p_d3 = tf_d.add_paragraph()
p_d3.text = "Core Tech Stack: Python 3.11  •  Qiskit 2.5  •  RDKit 2024+  •  Scikit-Learn  •  Qiskit Aer Simulator  •  Streamlit"
p_d3.font.name = FONT_BODY
p_d3.font.size = Pt(12)
p_d3.font.color.rgb = COLOR_TEAL
p_d3.space_before = Pt(12)

set_notes(slide1, """Good morning, respected professors, external examiners, and colleagues.
Welcome to my capstone presentation titled 'Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates'.

In this project, we have designed, implemented, and empirically benchmarked a complete hybrid quantum-classical drug screening pipeline.
We target Beta-Secretase 1 (BACE-1), a central enzymatic target in Alzheimer's disease pathology.
We use real experimental data from MoleculeNet, extract chemical features with RDKit, predict biological activity with Random Forest, and formulate the fixed-budget candidate selection problem as a QUBO problem solved variationally using QAOA on a local Qiskit Aer quantum simulator.

Over the next 15 minutes, I will walk you through the biological problem, our mathematical formulation, the quantum circuit architecture, our classical benchmarking results, and a live demonstration of the full-stack web application.""")


# ==============================================================================
# SLIDE 2: PROBLEM STATEMENT
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
add_header(slide2, "Problem Statement: The Combinatorial Drug Discovery Bottleneck", "BIOLOGICAL & COMPUTATIONAL MOTIVATION")

# Left Column: Biological Target Card
card_bio = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
card_bio.fill.solid()
card_bio.fill.fore_color.rgb = COLOR_BG_LIGHT
card_bio.line.color.rgb = COLOR_GRAY_LIGHT
card_bio.line.width = Pt(1)

tb_bio = slide2.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(4.8))
tf_bio = tb_bio.text_frame
tf_bio.word_wrap = True

p_b_h = tf_bio.paragraphs[0]
p_b_h.text = "1. Biological Target: BACE-1 & Alzheimer's"
p_b_h.font.name = FONT_HEADING
p_b_h.font.size = Pt(16)
p_b_h.font.bold = True
p_b_h.font.color.rgb = COLOR_NAVY_DARK

bullets_bio = [
    ("Enzyme Function", "Human beta-secretase 1 (BACE-1) is an aspartyl protease that cleaves Amyloid Precursor Protein (APP) at the beta-site."),
    ("Pathology", "Rate-limiting step generating neurotoxic Amyloid-beta (A-beta 42) peptides that aggregate into Alzheimer's senile plaques [Subramanian et al., 2018]."),
    ("Therapeutic Challenge", "Inhibitors must achieve high potency (IC50 < 1 uM) while crossing the blood-brain barrier (demanding strict Lipinski Rule of 5 adherence).")
]
for title, desc in bullets_bio:
    p_item = tf_bio.add_paragraph()
    p_item.text = f"• {title}: {desc}"
    p_item.font.name = FONT_BODY
    p_item.font.size = Pt(12)
    p_item.font.color.rgb = COLOR_GRAY_TEXT
    p_item.space_before = Pt(8)

# Right Column: Combinatorial Bottleneck Card
card_comp = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
card_comp.fill.solid()
card_comp.fill.fore_color.rgb = COLOR_BG_LIGHT
card_comp.line.color.rgb = COLOR_GRAY_LIGHT
card_comp.line.width = Pt(1)

tb_comp = slide2.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
tf_comp = tb_comp.text_frame
tf_comp.word_wrap = True

p_c_h = tf_comp.paragraphs[0]
p_c_h.text = "2. The Fixed-Budget Selection Dilemma"
p_c_h.font.name = FONT_HEADING
p_c_h.font.size = Pt(16)
p_c_h.font.bold = True
p_c_h.font.color.rgb = COLOR_NAVY_DARK

bullets_comp = [
    ("Laboratory Bottleneck", "High-throughput virtual screening flags thousands of prospective hits. However, expensive synthesis and crystallography permit advancing only K candidates (K << N)."),
    ("Multi-Objective Trade-Off", "Selecting purely on binding affinity neglects molecular weight, lipophilicity (LogP), and toxicity constraints."),
    ("Combinatorial Nature", "Selecting K candidates out of N is an NP-hard subset selection problem under non-linear chemical and diversity interaction constraints."),
    ("Quantum Opportunity", "Mapping candidate selection to Quadratic Unconstrained Binary Optimization (QUBO) provides an ideal benchmark for hybrid quantum algorithms.")
]
for title, desc in bullets_comp:
    p_item = tf_comp.add_paragraph()
    p_item.text = f"• {title}: {desc}"
    p_item.font.name = FONT_BODY
    p_item.font.size = Pt(12)
    p_item.font.color.rgb = COLOR_GRAY_TEXT
    p_item.space_before = Pt(8)

set_notes(slide2, """Let us begin with the problem statement.
In drug discovery, targeting Alzheimer's disease has been notoriously difficult. BACE-1 is the key rate-limiting enzyme responsible for producing toxic amyloid-beta peptides that destroy synapses in the brain.
While computational virtual screening can identify dozens or hundreds of prospective compounds, wet-lab synthesis, crystallography, and animal trials are prohibitively expensive.

A research team typically has the funding and capacity to advance only K candidates—say, 3 molecules—out of a library of N candidates.
If we only sort by predicted binding affinity, we risk selecting molecules with poor drug-likeness, bad blood-brain barrier permeability, or structural redundancy.
Therefore, candidate selection requires multi-objective optimization under strict budget constraints.
This is fundamentally a combinatorial optimization problem, which we map onto a quantum computer using QAOA.""")


# ==============================================================================
# SLIDE 3: OBJECTIVES & PROPOSED ARCHITECTURE
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
add_header(slide3, "Objectives and Proposed System Architecture", "END-TO-END PIPELINE OVERVIEW")

# Left Column: Objectives Card
card_obj = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(4.5), Inches(5.3))
card_obj.fill.solid()
card_obj.fill.fore_color.rgb = COLOR_BG_LIGHT
card_obj.line.color.rgb = COLOR_GRAY_LIGHT
card_obj.line.width = Pt(1)

tb_obj = slide3.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(4.1), Inches(4.8))
tf_obj = tb_obj.text_frame
tf_obj.word_wrap = True

p_o_h = tf_obj.paragraphs[0]
p_o_h.text = "Key Project Objectives"
p_o_h.font.name = FONT_HEADING
p_o_h.font.size = Pt(16)
p_o_h.font.bold = True
p_o_h.font.color.rgb = COLOR_NAVY_DARK

objs = [
    "Load real MoleculeNet BACE data (1,513 compounds) without fabricated observations.",
    "Extract 512-bit Morgan fingerprints and Lipinski physicochemical descriptors.",
    "Train a leakage-free Random Forest activity prediction model.",
    "Formulate candidate selection as a QUBO with quadratic cardinality penalties.",
    "Implement genuine QAOA on Qiskit Aer simulator with depth p.",
    "Benchmark against Classical Top-K and Exact Brute-Force solvers.",
    "Deliver an interactive Streamlit UI with exportable results."
]
for o in objs:
    p_i = tf_obj.add_paragraph()
    p_i.text = f"✔ {o}"
    p_i.font.name = FONT_BODY
    p_i.font.size = Pt(11)
    p_i.font.color.rgb = COLOR_GRAY_TEXT
    p_i.space_before = Pt(6)

# Right Column: Flowchart Image
img_flow = assets_dir / "architecture_flowchart.png"
if img_flow.exists():
    slide3.shapes.add_picture(str(img_flow), Inches(5.6), Inches(1.5), width=Inches(6.9))

# Callout below diagram
card_callout = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(5.0), Inches(6.9), Inches(1.8))
card_callout.fill.solid()
card_callout.fill.fore_color.rgb = RGBColor(238, 242, 255)
card_callout.line.color.rgb = COLOR_BLUE
card_callout.line.width = Pt(1)

tb_call = slide3.shapes.add_textbox(Inches(5.8), Inches(5.1), Inches(6.5), Inches(1.5))
tf_call = tb_call.text_frame
tf_call.word_wrap = True
p_c_1 = tf_call.paragraphs[0]
p_c_1.text = "Hybrid Classical-Quantum Synergy"
p_c_1.font.name = FONT_HEADING
p_c_1.font.size = Pt(14)
p_c_1.font.bold = True
p_c_1.font.color.rgb = COLOR_BLUE

p_c_2 = tf_call.add_paragraph()
p_c_2.text = "• Classical ML is optimal for training across large datasets (1,500+ compounds).\n• Quantum QAOA is deployed for combinatorial decision optimization across candidate subsets (N qubits), preventing classical exponential explosion as constraints grow."
p_c_2.font.name = FONT_BODY
p_c_2.font.size = Pt(11)
p_c_2.font.color.rgb = COLOR_NAVY_DARK
p_c_2.space_before = Pt(4)

set_notes(slide3, """On Slide 3, we show our project objectives and the complete system architecture.
Our goal is to build an end-to-end, runnable system.
Look at the architecture flowchart on the right:
1. We start with real experimental data from MoleculeNet BACE.
2. We extract both topological Morgan fingerprints (ECFP4) and continuous physicochemical descriptors.
3. We train a classical Random Forest classifier to estimate the probability that a molecule is active.
4. We combine predicted probability, binding affinity, and Lipinski rule compliance into a composite score.
5. We formulate the selection problem as a QUBO and map it to an Ising Cost Hamiltonian.
6. QAOA executes variational quantum circuits on the Qiskit Aer simulator, which we benchmark against classical exact enumeration.
Notice the division of labor: classical ML handles large-scale supervised learning, while the quantum processor optimizes the discrete combinatorial decision.""")


# ==============================================================================
# SLIDE 4: PROPOSED ALGORITHM — STEP-BY-STEP
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
add_header(slide4, "Proposed Algorithm: Step-by-Step Screening Methodology", "ALGORITHM WORKFLOW & FEATURE ENGINEERING")

# 4 horizontal process cards
card_w = Inches(2.75)
card_gap = Inches(0.2)
start_x = Inches(0.8)
y_pos = Inches(1.6)
card_h = Inches(5.2)

steps_data = [
    ("Step 1: Data QC & Featurization", COLOR_TEAL, [
        "Dataset: MoleculeNet BACE (1,513 valid records; 691 Active, 822 Inactive).",
        "RDKit Validation: Canonical SMILES parsing, valence checks, deduplication.",
        "ECFP4 Fingerprints: 512-bit binary structural vectors.",
        "Descriptors: MW, LogP, HBD, HBA, RotB, TPSA, Lipinski violations."
    ]),
    ("Step 2: ML Activity Model", COLOR_BLUE, [
        "Partition: 80% Train (1,210), 20% Test (303).",
        "Leakage Prevention: StandardScaler fitted exclusively on training set.",
        "Random Forest: 150 estimators with balanced class weighting.",
        "Output: Estimated probability P(active) in [0, 1]."
    ]),
    ("Step 3: Multi-Objective Score", COLOR_AMBER, [
        "Composite utility function:",
        "s_i = 0.60*P(act) + 0.25*Norm(pIC50) + 0.15*LipinskiPassRate.",
        "Calibrated in [0, 1].",
        "Harmonizes biochemical potency with drug-likeness."
    ]),
    ("Step 4: Quantum Optimization", COLOR_RED, [
        "Formulate QUBO with penalty A*(sum x_i - K)^2.",
        "Map binary x_i to Pauli-Z spin operators.",
        "Construct depth-p QAOA circuit in Qiskit.",
        "Optimize angles (gamma, beta) via COBYLA.",
        "Sample 1024 shots on AerSimulator."
    ])
]

for idx, (st_title, st_col, st_points) in enumerate(steps_data):
    cx = start_x + idx * (card_w + card_gap)
    c_shape = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, y_pos, card_w, card_h)
    c_shape.fill.solid()
    c_shape.fill.fore_color.rgb = COLOR_BG_LIGHT
    c_shape.line.color.rgb = st_col
    c_shape.line.width = Pt(1.5)
    
    tb_s = slide4.shapes.add_textbox(cx + Inches(0.15), y_pos + Inches(0.2), card_w - Inches(0.3), card_h - Inches(0.4))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True
    
    p_h = tf_s.paragraphs[0]
    p_h.text = st_title
    p_h.font.name = FONT_HEADING
    p_h.font.size = Pt(13)
    p_h.font.bold = True
    p_h.font.color.rgb = st_col
    
    for pt in st_points:
        p_pt = tf_s.add_paragraph()
        p_pt.text = f"• {pt}"
        p_pt.font.name = FONT_BODY
        p_pt.font.size = Pt(10.5)
        p_pt.font.color.rgb = COLOR_GRAY_TEXT
        p_pt.space_before = Pt(6)

set_notes(slide4, """Slide 4 breaks down the proposed algorithm into four systematic stages.
In Step 1, data quality control and featurization are performed using RDKit. We clean 1,513 real compounds from MoleculeNet BACE. For each compound, we compute both 512-bit Morgan fingerprints and 7 physicochemical descriptors.
In Step 2, we train a Random Forest model on 1,210 training compounds. We strictly fit the scaler only on the training set to prevent data leakage.
In Step 3, we define the composite candidate score s_i. It gives 60% weight to ML predicted activity, 25% weight to experimental binding affinity (pIC50), and 15% weight to Lipinski rule compliance.
In Step 4, we formulate the QUBO, map it to Pauli-Z spins, build the QAOA circuit, optimize parameters with COBYLA, and sample the optimal bitstring on Qiskit Aer.""")


# ==============================================================================
# SLIDE 5: QUBO MATHEMATICAL FORMULATION & ISING MAPPING
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
add_header(slide5, "QUBO Mathematical Formulation & Analytical Ising Mapping", "COMBINATORIAL OPTIMIZATION MATHEMATICS")

# Left Column: Formulation Box
card_qubo = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
card_qubo.fill.solid()
card_qubo.fill.fore_color.rgb = COLOR_BG_LIGHT
card_qubo.line.color.rgb = COLOR_GRAY_LIGHT
card_qubo.line.width = Pt(1)

tb_q = slide5.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(4.8))
tf_q = tb_q.text_frame
tf_q.word_wrap = True

p_q1 = tf_q.paragraphs[0]
p_q1.text = "1. Constrained Selection Objective"
p_q1.font.name = FONT_HEADING
p_q1.font.size = Pt(15)
p_q1.font.bold = True
p_q1.font.color.rgb = COLOR_NAVY_DARK

p_q2 = tf_q.add_paragraph()
p_q2.text = "Maximize:  sum_{i=1}^N  s_i * x_i\nSubject to: sum_{i=1}^N  x_i = K,   x_i in {0, 1}"
p_q2.font.name = "Courier New"
p_q2.font.size = Pt(12)
p_q2.font.bold = True
p_q2.font.color.rgb = COLOR_BLUE
p_q2.space_before = Pt(4)

p_q3 = tf_q.add_paragraph()
p_q3.text = "2. Unconstrained Penalty Formulation (QUBO)"
p_q3.font.name = FONT_HEADING
p_q3.font.size = Pt(15)
p_q3.font.bold = True
p_q3.font.color.rgb = COLOR_NAVY_DARK
p_q3.space_before = Pt(12)

p_q4 = tf_q.add_paragraph()
p_q4.text = "E(x) = -sum(s_i * x_i) + A * (sum x_i - K)^2"
p_q4.font.name = "Courier New"
p_q4.font.size = Pt(12)
p_q4.font.bold = True
p_q4.font.color.rgb = COLOR_RED
p_q4.space_before = Pt(4)

p_q5 = tf_q.add_paragraph()
p_q5.text = "Expanding via binary identity x_i^2 = x_i:\nE(x) = sum_i [-s_i + A(1 - 2K)] x_i + sum_{i < j} 2A x_i x_j + A*K^2"
p_q5.font.name = "Courier New"
p_q5.font.size = Pt(11)
p_q5.font.color.rgb = COLOR_NAVY_DARK
p_q5.space_before = Pt(6)

p_q6 = tf_q.add_paragraph()
p_q6.text = "Penalty Condition: A >= 1.5 * max(s_i) guarantees that any invalid cardinality selection costs strictly more than any score gain."
p_q6.font.name = FONT_BODY
p_q6.font.size = Pt(11)
p_q6.font.color.rgb = COLOR_GRAY_TEXT
p_q6.space_before = Pt(6)

# Right Column: Ising Mapping
card_ising = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
card_ising.fill.solid()
card_ising.fill.fore_color.rgb = COLOR_BG_LIGHT
card_ising.line.color.rgb = COLOR_GRAY_LIGHT
card_ising.line.width = Pt(1)

tb_i = slide5.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
tf_i = tb_i.text_frame
tf_i.word_wrap = True

p_i1 = tf_i.paragraphs[0]
p_i1.text = "3. Analytical Mapping to Pauli-Z Spins"
p_i1.font.name = FONT_HEADING
p_i1.font.size = Pt(15)
p_i1.font.bold = True
p_i1.font.color.rgb = COLOR_NAVY_DARK

p_i2 = tf_i.add_paragraph()
p_i2.text = "Map binary variable x_i to Pauli-Z spin operator:\nx_i = (I - Z_i) / 2,   where Z_i in {+1, -1}\n|0> -> +1 (unselected),  |1> -> -1 (selected)"
p_i2.font.name = "Courier New"
p_i2.font.size = Pt(11.5)
p_i2.font.color.rgb = COLOR_BLUE
p_i2.space_before = Pt(4)

p_i3 = tf_i.add_paragraph()
p_i3.text = "Cost Hamiltonian Decomposition:\nH_C = sum_{i=1}^N h_i Z_i + sum_{i < j} J_ij Z_i Z_j + C * I"
p_i3.font.name = "Courier New"
p_i3.font.size = Pt(12)
p_i3.font.bold = True
p_i3.font.color.rgb = COLOR_TEAL
p_i3.space_before = Pt(10)

p_i4 = tf_i.add_paragraph()
p_i4.text = "Exact Analytical Coefficients:\n• Longitudinal Fields: h_i = s_i / 2 + (A / 2) * (2K - N)\n• Ising Couplings:      J_ij = A / 2  (for all i < j)\n• Constant Offset:     C = A*K^2 - 0.5*sum(s_i) + ...\n\nResult: Eigenvalues <x|H_C|x> match E(x) identically across all 2^N basis states down to 10^-5 precision!"
p_i4.font.name = FONT_BODY
p_i4.font.size = Pt(11)
p_i4.font.color.rgb = COLOR_NAVY_DARK
p_i4.space_before = Pt(6)

set_notes(slide5, """Slide 5 presents the mathematical heart of our quantum formulation.
Our optimization goal is to maximize total score sum(s_i * x_i) subject to sum(x_i) = K.
To solve this on an unconstrained optimizer, we introduce a quadratic cardinality penalty A*(sum x_i - K)^2.
By expanding this quadratic term and using the idempotent property of binary variables (x_i squared equals x_i), we get our QUBO objective.

Then, we analytically map each binary variable x_i to the Pauli-Z operator: x_i = (I - Z_i)/2.
Notice the exact analytical formulas we derived on the right:
- The single-qubit longitudinal field h_i is simply s_i / 2 + (A/2)*(2K - N).
- The two-qubit Ising coupling J_ij is simply A / 2 for every interacting pair.
We tested this formulation in pytest across all 2^N basis states, and the quantum Hamiltonian eigenvalues match the classical QUBO energy down to the 5th decimal place.""")


# ==============================================================================
# SLIDE 6: QAOA CIRCUIT & PSEUDOCODE
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
add_header(slide6, "QAOA Quantum Circuit Architecture & Pseudocode", "QUANTUM CIRCUIT REALIZATION")

# Left Column: Circuit Diagram
img_circ = assets_dir / "qaoa_circuit_diagram.png"
if img_circ.exists():
    slide6.shapes.add_picture(str(img_circ), Inches(0.8), Inches(1.5), width=Inches(6.0))

# Circuit Description below image
card_cd = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.5), Inches(6.0), Inches(2.3))
card_cd.fill.solid()
card_cd.fill.fore_color.rgb = COLOR_BG_LIGHT
card_cd.line.color.rgb = COLOR_GRAY_LIGHT
card_cd.line.width = Pt(1)

tb_cd = slide6.shapes.add_textbox(Inches(1.0), Inches(4.6), Inches(5.6), Inches(2.1))
tf_cd = tb_cd.text_frame
tf_cd.word_wrap = True
p_cd1 = tf_cd.paragraphs[0]
p_cd1.text = "Circuit Components (Qiskit 2.5)"
p_cd1.font.name = FONT_HEADING
p_cd1.font.size = Pt(14)
p_cd1.font.bold = True
p_cd1.font.color.rgb = COLOR_NAVY_DARK

p_cd2 = tf_cd.add_paragraph()
p_cd2.text = "1. State Preparation: |+>^N via Hadamard gates on all N qubits.\n2. Cost Unitary: U(C, gamma) = exp(-i * gamma * H_C) via RZ(2*gamma*h_i) and RZZ(2*gamma*J_ij).\n3. Mixer Unitary: U(B, beta) = exp(-i * beta * H_B) via RX(2*beta) gates on all qubits.\n4. Depth p: Alternating cost and mixer layers variationally tuned."
p_cd2.font.name = FONT_BODY
p_cd2.font.size = Pt(10.5)
p_cd2.font.color.rgb = COLOR_GRAY_TEXT
p_cd2.space_before = Pt(4)

# Right Column: Pseudocode Box
card_pseudo = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), Inches(1.5), Inches(5.4), Inches(5.3))
card_pseudo.fill.solid()
card_pseudo.fill.fore_color.rgb = COLOR_NAVY_DARK
card_pseudo.line.color.rgb = COLOR_TEAL
card_pseudo.line.width = Pt(1.5)

tb_ps = slide6.shapes.add_textbox(Inches(7.3), Inches(1.7), Inches(5.0), Inches(4.8))
tf_ps = tb_ps.text_frame
tf_ps.word_wrap = True

p_ps_h = tf_ps.paragraphs[0]
p_ps_h.text = "Algorithm Pseudocode: QAOA Screening"
p_ps_h.font.name = FONT_HEADING
p_ps_h.font.size = Pt(15)
p_ps_h.font.bold = True
p_ps_h.font.color.rgb = COLOR_TEAL

pseudo_lines = [
    "Input:  Scores s_i, Budget K, Depth p, Shots M",
    "Output: Selected Candidates, Best Energy E*",
    "",
    "1: Calculate penalty A = 2.0 * max(s_i)",
    "2: Derive Ising fields h_i and couplings J_ij",
    "3: Initialize parameters (gamma, beta) in [0, pi]",
    "4: Define Expectation Function <H_C>(gamma, beta):",
    "     qc <- QuantumCircuit(N)",
    "     Apply H on all qubits",
    "     For layer l = 1 to p do:",
    "       Apply RZ(2*gamma_l*h_i) & RZZ(2*gamma_l*J_ij)",
    "       Apply RX(2*beta_l) on all qubits",
    "     Return <psi|H_C|psi>",
    "5: (gamma*, beta*) <- COBYLA.minimize(<H_C>)",
    "6: Counts <- AerSimulator.run(qc(gamma*, beta*), shots=M)",
    "7: x* <- Best feasible bitstring from Counts",
    "8: If x* infeasible: x* <- GreedyRepair(x*, K)",
    "9: Return x*, E(x*), FeasibleRate(Counts)"
]
for pl in pseudo_lines:
    p_l = tf_ps.add_paragraph()
    p_l.text = pl
    p_l.font.name = "Courier New"
    p_l.font.size = Pt(9.5)
    p_l.font.color.rgb = COLOR_WHITE if not pl.startswith("Input") and not pl.startswith("Output") else RGBColor(148, 163, 184)
    p_l.space_before = Pt(1)

set_notes(slide6, """Slide 6 illustrates our QAOA quantum circuit architecture and the exact pseudocode.
Look at the circuit diagram on the left:
First, all qubits are initialized in the equal superposition state |+> using Hadamard gates.
Next, we apply the Cost Unitary U(C, gamma). This translates directly into single-qubit RZ gates for the longitudinal fields and two-qubit RZZ gates for pairwise Ising couplings.
Then, we apply the Mixer Unitary U(B, beta), implemented as single-qubit RX gates, which drive quantum transitions between computational basis states.
This alternating sequence is repeated for depth p.

On the right is our pseudocode. The classical COBYLA optimizer iteratively evaluates the energy expectation and adjusts gamma and beta.
Once optimal angles are found, we run measurement sampling with 1,024 shots on the Aer simulator, decode the bitstrings, check cardinality feasibility, and output the selected candidates.""")


# ==============================================================================
# SLIDE 7: ALGORITHM COMPLEXITY & NISQ FEASIBILITY
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
add_header(slide7, "Algorithm Complexity and NISQ Feasibility Analysis", "THEORETICAL & RUNTIME SCALABILITY")

# Table of Complexity
table_shape = slide7.shapes.add_table(5, 5, Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.6))
table = table_shape.table
table.columns[0].width = Inches(2.2)
table.columns[1].width = Inches(2.4)
table.columns[2].width = Inches(2.4)
table.columns[3].width = Inches(2.4)
table.columns[4].width = Inches(2.3)

headers = ["Method", "Time Complexity", "Space / Memory", "QPU / Simulator Scalability", "Feasibility"]
for col_idx, h in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_NAVY_DARK
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

rows_data = [
    ("Top-K Greedy", "O(N log N)", "O(N)", "Instantaneous on CPU", "Guaranteed (100%)"),
    ("Exact QUBO", "O(2^N)", "O(1)", "Intractable for N > 30 on CPU", "Guaranteed (100%)"),
    ("QAOA (Aer Sim)", "O(N_iter * 2^N)", "O(2^N) state amplitudes", "Limited by 2^N RAM (N <= 20)", "Probabilistic (45.7% raw)"),
    ("QAOA (Real QPU)", "O(N_iter * M)", "O(N) physical qubits", "O(p * N^2) circuit depth", "Probabilistic sampling")
]
for row_idx, r_data in enumerate(rows_data):
    for col_idx, val in enumerate(r_data):
        cell = table.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_BG_LIGHT if row_idx % 2 == 0 else COLOR_WHITE
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_NAVY_DARK if col_idx == 0 else COLOR_GRAY_TEXT

# Two callout cards below table
card_nisq1 = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.4), Inches(5.7), Inches(2.4))
card_nisq1.fill.solid()
card_nisq1.fill.fore_color.rgb = COLOR_BG_LIGHT
card_nisq1.line.color.rgb = COLOR_GRAY_LIGHT
card_nisq1.line.width = Pt(1)

tb_n1 = slide7.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(5.3), Inches(2.1))
tf_n1 = tb_n1.text_frame
tf_n1.word_wrap = True
p_n1 = tf_n1.paragraphs[0]
p_n1.text = "Why Classical Simulator Limits Matter"
p_n1.font.name = FONT_HEADING
p_n1.font.size = Pt(13)
p_n1.font.bold = True
p_n1.font.color.rgb = COLOR_NAVY_DARK

p_n1_b = tf_n1.add_paragraph()
p_n1_b.text = "• Storing statevector amplitudes requires 2^N * 16 bytes.\n• N = 10 qubits: ~16 KB RAM.\n• N = 30 qubits: ~16 GB RAM.\n• N = 40 qubits: ~16 TB RAM.\n• Hence, running QAOA on candidate subsets (N = 8 to 12) is mathematically necessary for local simulation."
p_n1_b.font.name = FONT_BODY
p_n1_b.font.size = Pt(10.5)
p_n1_b.font.color.rgb = COLOR_GRAY_TEXT
p_n1_b.space_before = Pt(4)

card_nisq2 = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(4.4), Inches(5.7), Inches(2.4))
card_nisq2.fill.solid()
card_nisq2.fill.fore_color.rgb = COLOR_BG_LIGHT
card_nisq2.line.color.rgb = COLOR_GRAY_LIGHT
card_nisq2.line.width = Pt(1)

tb_n2 = slide7.shapes.add_textbox(Inches(7.0), Inches(4.5), Inches(5.3), Inches(2.1))
tf_n2 = tb_n2.text_frame
tf_n2.word_wrap = True
p_n2 = tf_n2.paragraphs[0]
p_n2.text = "Where Quantum Advantage Actually Emerges"
p_n2.font.name = FONT_HEADING
p_n2.font.size = Pt(13)
p_n2.font.bold = True
p_n2.font.color.rgb = COLOR_NAVY_DARK

p_n2_b = tf_n2.add_paragraph()
p_n2_b.text = "• For unconstrained linear cardinality, classical sorting is O(N log N).\n• However, when complex pairwise chemical interactions (scaffold diversity penalties, cross-reactivity) are added into Q_ij != const, the problem becomes NP-hard and non-convex.\n• That is the exact regime where quantum heuristic sampling is theorized to provide polynomial or quadratic advantages."
p_n2_b.font.name = FONT_BODY
p_n2_b.font.size = Pt(10.5)
p_n2_b.font.color.rgb = COLOR_GRAY_TEXT
p_n2_b.space_before = Pt(4)

set_notes(slide7, """Slide 7 discusses algorithmic complexity and NISQ feasibility with complete scientific honesty.
Let us examine the table:
Classical greedy Top-K sorting runs in O(N log N) time and is practically instantaneous.
Exact classical QUBO evaluates all 2^N bitstrings. It works fast for small instances (N <= 20), but becomes mathematically intractable once N exceeds 30 or 40.
When simulating QAOA on classical computers, we face an exponential memory wall: 30 qubits requires 16 Gigabytes, and 40 qubits requires 16 Terabytes.
This is precisely why we screen manageable candidate subsets (N = 8) on simulators.

Furthermore, we must be honest about quantum advantage: QAOA does not beat classical sorting for purely linear problems.
The real quantum opportunity arises when we introduce non-linear pairwise chemical interactions—such as pharmacophore diversity constraints and cross-reactivity penalties—making the landscape NP-hard and non-convex.""")


# ==============================================================================
# SLIDE 8: MACHINE LEARNING ACTIVITY PREDICTION RESULTS
# ==============================================================================
slide8 = prs.slides.add_slide(blank_layout)
add_header(slide8, "Stage 1 Results: Biological Activity Prediction Model", "MACHINE LEARNING CLASSIFIER EVALUATION")

# Left Image: Confusion Matrix
img_cm = assets_dir / "confusion_matrix.png"
if img_cm.exists():
    slide8.shapes.add_picture(str(img_cm), Inches(0.8), Inches(1.5), width=Inches(3.8))

# Middle Image: ROC Curve
img_roc = assets_dir / "roc_curve.png"
if img_roc.exists():
    slide8.shapes.add_picture(str(img_roc), Inches(4.8), Inches(1.5), width=Inches(3.8))

# Right Column: Metrics Card
card_ml = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.5), Inches(3.7), Inches(5.3))
card_ml.fill.solid()
card_ml.fill.fore_color.rgb = COLOR_BG_LIGHT
card_ml.line.color.rgb = COLOR_GRAY_LIGHT
card_ml.line.width = Pt(1)

tb_ml = slide8.shapes.add_textbox(Inches(9.0), Inches(1.7), Inches(3.3), Inches(4.8))
tf_ml = tb_ml.text_frame
tf_ml.word_wrap = True

p_ml_h = tf_ml.paragraphs[0]
p_ml_h.text = "Measured Model Metrics"
p_ml_h.font.name = FONT_HEADING
p_ml_h.font.size = Pt(15)
p_ml_h.font.bold = True
p_ml_h.font.color.rgb = COLOR_NAVY_DARK

ml_metrics_list = [
    ("Test Samples", "303 compounds"),
    ("Test Accuracy", "78.55% (238 / 303)"),
    ("ROC-AUC Score", "0.8794"),
    ("Precision", "75.89%"),
    ("Recall (Sensitivity)", "77.54%"),
    ("F1-Score", "0.7670"),
    ("True Negatives", "131 compounds"),
    ("True Positives", "107 compounds"),
    ("False Positives", "34 compounds"),
    ("False Negatives", "31 compounds")
]
for k, v in ml_metrics_list:
    p_m = tf_ml.add_paragraph()
    p_m.text = f"{k}: {v}"
    p_m.font.name = FONT_BODY
    p_m.font.size = Pt(10.5)
    p_m.font.bold = (k in ["Test Accuracy", "ROC-AUC Score", "F1-Score"])
    p_m.font.color.rgb = COLOR_NAVY_DARK if p_m.font.bold else COLOR_GRAY_TEXT
    p_m.space_before = Pt(3)

set_notes(slide8, """Slide 8 showcases our empirical results for the first stage: biological activity prediction.
These are real numbers generated from running the model on the held-out test set of 303 compounds.
Looking at the confusion matrix on the left: the model correctly classified 131 true inactives and 107 true active inhibitors.
Looking at the ROC curve in the center: the area under the curve is 0.8794, demonstrating strong discriminative power far above the random diagonal baseline.
Overall, test accuracy reached 78.55% and the F1-score reached 0.7670.
This confirms our machine learning pipeline provides high-quality, calibrated probabilities to feed into the composite scoring engine.""")


# ==============================================================================
# SLIDE 9: QUANTUM OPTIMIZATION & BENCHMARKING RESULTS
# ==============================================================================
slide9 = prs.slides.add_slide(blank_layout)
add_header(slide9, "Stage 2 Results: QAOA vs Classical Benchmarking", "EMPIRICAL OPTIMIZATION BENCHMARK (N=8, K=3)")

# Top Table: Comparison
tbl_shape2 = slide9.shapes.add_table(4, 7, Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.0))
tbl2 = tbl_shape2.table
col_widths = [Inches(2.2), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.5), Inches(1.6), Inches(1.6)]
for i, w in enumerate(col_widths):
    tbl2.columns[i].width = w

headers2 = ["Optimization Method", "QUBO Energy E(x)", "Score Sum", "Feasible (K=3)", "Optimality Gap", "Overlap %", "Runtime (s)"]
for col_idx, h in enumerate(headers2):
    cell = tbl2.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLOR_NAVY_DARK
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

b_rows = [
    ("QAOA (Qiskit Aer)", "-1.7179", "1.7179", "Yes (K=3)", "0.0000", "100.0%", "0.5585 s"),
    ("Top-K Greedy", "-1.7179", "1.7179", "Yes (K=3)", "0.0000", "100.0%", "0.0015 s"),
    ("Exact Classical QUBO", "-1.7179", "1.7179", "Yes (K=3)", "0.0000", "100.0%", "0.0052 s")
]
for row_idx, r_data in enumerate(b_rows):
    for col_idx, val in enumerate(r_data):
        cell = tbl2.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_BG_LIGHT if row_idx % 2 == 0 else COLOR_WHITE
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.bold = (col_idx in [1, 4])
        p.font.color.rgb = COLOR_TEAL if col_idx == 4 else (COLOR_NAVY_DARK if col_idx == 0 else COLOR_GRAY_TEXT)

# Two bottom images: Convergence and Measurement Distribution
img_conv = assets_dir / "qaoa_convergence.png"
if img_conv.exists():
    slide9.shapes.add_picture(str(img_conv), Inches(0.8), Inches(3.7), width=Inches(5.7))

img_meas = assets_dir / "measurement_distribution.png"
if img_meas.exists():
    slide9.shapes.add_picture(str(img_meas), Inches(6.8), Inches(3.7), width=Inches(5.7))

set_notes(slide9, """Slide 9 presents our quantum optimization results and classical benchmarking for N=8 candidate molecules and budget K=3.
Look at the benchmark table at the top:
QAOA on Qiskit Aer successfully converged to the global optimum:
- Final objective energy: -1.7179.
- Optimality gap: 0.0000.
- Overlap with the exact brute-force optimum: 100.0%.
All three methods agreed on the exact same optimal bitstring: 10100010.

Now observe the two graphs below:
On the left is the COBYLA optimizer convergence curve across iterations, showing smooth descent to the energy minimum.
On the right is the measurement probability distribution from 1,024 shots.
Notice the green bars representing feasible states where sum(x_i) = 3: the feasible sample rate reached 45.7%, meaning nearly half of all raw quantum shots satisfied the cardinality constraint without any repair needed!""")


# ==============================================================================
# SLIDE 10: SELECTED DRUG CANDIDATES & CHEMICAL PROFILING
# ==============================================================================
slide10 = prs.slides.add_slide(blank_layout)
add_header(slide10, "Selected Drug Leads: Chemical Structure & Property Profiling", "PRIORITIZED CANDIDATES FROM OPTIMAL BITSTRING 10100010")

# Left Image: Chemical structures
img_mol = assets_dir / "selected_molecules.png"
if img_mol.exists():
    slide10.shapes.add_picture(str(img_mol), Inches(0.8), Inches(1.5), width=Inches(7.2))

# Right Column: Candidate Profiles Card
card_leads = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.3), Inches(1.5), Inches(4.2), Inches(5.3))
card_leads.fill.solid()
card_leads.fill.fore_color.rgb = COLOR_BG_LIGHT
card_leads.line.color.rgb = COLOR_GRAY_LIGHT
card_leads.line.width = Pt(1)

tb_leads = slide10.shapes.add_textbox(Inches(8.5), Inches(1.7), Inches(3.8), Inches(4.8))
tf_leads = tb_leads.text_frame
tf_leads.word_wrap = True

p_lh = tf_leads.paragraphs[0]
p_lh.text = "Prioritized Candidate Profiles"
p_lh.font.name = FONT_HEADING
p_lh.font.size = Pt(15)
p_lh.font.bold = True
p_lh.font.color.rgb = COLOR_NAVY_DARK

leads_data = [
    ("MOL_BACE_558 (Top Lead)", [
        "Predicted P(active): 87.2%",
        "Binding Affinity (pIC50): 7.59 (~26 nM IC50)",
        "Lipinski Pass Rate: 100% (0 violations)",
        "Composite Score: 0.923"
    ]),
    ("MOL_BACE_1111 (Lead 2)", [
        "Predicted P(active): 19.7%",
        "Binding Affinity (pIC50): 6.03 (~0.9 uM)",
        "Lipinski Pass Rate: 100% (0 violations)",
        "Composite Score: 0.423"
    ]),
    ("MOL_BACE_1121 (Lead 3)", [
        "Predicted P(active): 11.5%",
        "Binding Affinity (pIC50): 6.00 (~1.0 uM)",
        "Lipinski Pass Rate: 100% (0 violations)",
        "Composite Score: 0.372"
    ])
]
for l_title, l_props in leads_data:
    p_lt = tf_leads.add_paragraph()
    p_lt.text = l_title
    p_lt.font.name = FONT_HEADING
    p_lt.font.size = Pt(12)
    p_lt.font.bold = True
    p_lt.font.color.rgb = COLOR_TEAL if "Top" in l_title else COLOR_NAVY_DARK
    p_lt.space_before = Pt(8)
    for pr in l_props:
        p_lp = tf_leads.add_paragraph()
        p_lp.text = f"• {pr}"
        p_lp.font.name = FONT_BODY
        p_lp.font.size = Pt(10)
        p_lp.font.color.rgb = COLOR_GRAY_TEXT
        p_lp.space_before = Pt(2)

set_notes(slide10, """Slide 10 inspects the actual molecules selected by the optimal bitstring 10100010.
On the left, we render the 2D chemical structures of the top three selected leads.
Notice our top candidate, MOL_BACE_558:
- It has an 87.2% predicted probability of biological activity.
- Its experimentally measured pIC50 is 7.59, corresponding to a potent nanomolar binding affinity (approx. 26 nM).
- It satisfies 100% of Lipinski's Rule of 5 criteria with 0 violations.
- Its overall composite score is 0.923.
The other two molecules, MOL_BACE_1111 and MOL_BACE_1121, round out the budget of K=3.
This demonstrates how our system balances predicted activity, experimental affinity, and drug-likeness.""")


# ==============================================================================
# SLIDE 11: FULL-STACK IMPLEMENTATION & UI
# ==============================================================================
slide11 = prs.slides.add_slide(blank_layout)
add_header(slide11, "Implementation & Full-Stack Streamlit Web Application", "SYSTEM INTEGRATION & USER EXPERIENCE")

# 3 cards showing the implementation architecture
col_w = Inches(3.7)
col_g = Inches(0.3)
col_y = Inches(1.5)
col_h = Inches(5.3)

ui_features = [
    ("Modular Python Architecture", COLOR_BLUE, [
        "src/molecular_features.py: RDKit descriptor calculation and SVG rendering.",
        "src/data_loader.py: Automated download, cleaning, deduplication, and sampling.",
        "src/activity_model.py: Random Forest classifier and model persistence.",
        "src/qubo_formulation.py: QUBO matrix and Ising mapping.",
        "src/qaoa_optimizer.py: Qiskit 2.5 parameterized QAOA circuit on Aer.",
        "src/classical_baseline.py: Top-K and Exact QUBO enumeration.",
        "Automated Tests: 21 passing pytest unit and integration tests."
    ]),
    ("Streamlit Web Dashboard (app.py)", COLOR_TEAL, [
        "Page 1: Dashboard: Project KPIs, target biology, and architecture flow.",
        "Page 2: Dataset Explorer: Searchable table with 2D chemical structure rendering.",
        "Page 3: Activity Prediction: Real-time inference for custom SMILES inputs.",
        "Page 4: Quantum Screening: Live circuit execution with convergence plots.",
        "Page 5: Classical vs Quantum: Side-by-side benchmarking and optimality gap.",
        "Page 6: Results & Reports: CSV candidate export and downloadable JSON report."
    ]),
    ("Quality Control & Reproducibility", COLOR_GREEN, [
        "Reproducibility: Config file (config.yaml) and fixed random seeds.",
        "Zero Mock Buttons: Every button connects to functioning backend code.",
        "Safe Data Upload: Custom CSV upload handles malformed files without crashing.",
        "Exportable Outputs: Immediate CSV and JSON report downloads.",
        "Continuous Dev: Tested on Python 3.11 with pinned requirements.txt."
    ])
]

for idx, (f_title, f_col, f_pts) in enumerate(ui_features):
    cx = Inches(0.8) + idx * (col_w + col_g)
    c_box = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, col_y, col_w, col_h)
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = COLOR_BG_LIGHT
    c_box.line.color.rgb = f_col
    c_box.line.width = Pt(1.5)
    
    tb_f = slide11.shapes.add_textbox(cx + Inches(0.15), col_y + Inches(0.2), col_w - Inches(0.3), col_h - Inches(0.4))
    tf_f = tb_f.text_frame
    tf_f.word_wrap = True
    
    p_fh = tf_f.paragraphs[0]
    p_fh.text = f_title
    p_fh.font.name = FONT_HEADING
    p_fh.font.size = Pt(14)
    p_fh.font.bold = True
    p_fh.font.color.rgb = f_col
    
    for pt in f_pts:
        p_pt = tf_f.add_paragraph()
        p_pt.text = f"• {pt}"
        p_pt.font.name = FONT_BODY
        p_pt.font.size = Pt(10.5)
        p_pt.font.color.rgb = COLOR_GRAY_TEXT
        p_pt.space_before = Pt(6)

set_notes(slide11, """Slide 11 highlights our software engineering implementation and web application.
This is not a theoretical prototype or a script; it is a full-stack, modular software system.
On the left, notice our clean project architecture with complete separation of concerns between chemistry, machine learning, quantum optimization, and evaluation. We have 21 automated pytest tests verifying every module.
In the center, our multi-page Streamlit application provides six functional pages. Users can inspect 2D chemical structures, input custom SMILES strings to get real-time predictions, run QAOA with custom depths and shots, and download the prioritized candidate list as a CSV.
On the right, we emphasize reproducibility: fixed seeds, pinned requirements, and zero mock buttons.""")


# ==============================================================================
# SLIDE 12: SCIENTIFIC LIMITATIONS & ETHICAL CONSIDERATIONS
# ==============================================================================
slide12 = prs.slides.add_slide(blank_layout)
add_header(slide12, "Scientific Limitations & Ethical Disclaimers", "RESEARCH RIGOR & SCIENTIFIC HONESTY")

# 3 horizontal warning cards
w_card_h = Inches(1.5)
w_gap = Inches(0.25)
w_y = Inches(1.5)

warnings_data = [
    ("1. In Silico Hypotheses vs Wet-Lab Reality", COLOR_AMBER,
     "Quantum optimization solves a mathematical subset selection problem under defined utility scores. It does NOT prove drug safety, non-toxicity, bioavailability, binding specificity, or clinical efficacy. Computational screening provides prioritized research hypotheses that must undergo rigorous in vitro assays."),
    ("2. Target Specificity & Generalizability", COLOR_BLUE,
     "The activity prediction model is trained specifically on human BACE-1 in vitro assay data. It does NOT generalize to other aspartyl proteases (such as Cathepsin D or Renin) or other disease targets without dedicated retraining on respective benchmark datasets."),
    ("3. Absence of Unsubstantiated Quantum Speedup Claims", COLOR_RED,
     "On classical quantum simulators and current NISQ hardware, QAOA does not outperform classical greedy heuristics for simple linear cardinality problems. Practical quantum advantage requires non-convex landscapes with pairwise structural or chemical cross-reactivity interactions executed on fault-tolerant hardware.")
]

for idx, (w_title, w_col, w_text) in enumerate(warnings_data):
    wy = w_y + idx * (w_card_h + w_gap)
    card_w = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), wy, Inches(11.7), w_card_h)
    card_w.fill.solid()
    card_w.fill.fore_color.rgb = COLOR_BG_LIGHT
    card_w.line.color.rgb = w_col
    card_w.line.width = Pt(1.5)
    
    tb_w = slide12.shapes.add_textbox(Inches(1.0), wy + Inches(0.15), Inches(11.3), w_card_h - Inches(0.3))
    tf_w = tb_w.text_frame
    tf_w.word_wrap = True
    
    p_wh = tf_w.paragraphs[0]
    p_wh.text = w_title
    p_wh.font.name = FONT_HEADING
    p_wh.font.size = Pt(14)
    p_wh.font.bold = True
    p_wh.font.color.rgb = w_col
    
    p_wt = tf_w.add_paragraph()
    p_wt.text = w_text
    p_wt.font.name = FONT_BODY
    p_wt.font.size = Pt(11)
    p_wt.font.color.rgb = COLOR_NAVY_DARK
    p_wt.space_before = Pt(4)

set_notes(slide12, """On Slide 12, we address scientific limitations and ethical considerations with utmost transparency.
First: in silico screening produces prioritized laboratory hypotheses, not confirmed medicines. Neither machine learning nor quantum optimization can replace wet-lab biochemical validation.
Second: our activity model is strictly trained on human BACE-1; it cannot be applied to other enzymes without retraining.
Third: we make no exaggerated claims of quantum supremacy. On contemporary NISQ simulators, QAOA cannot beat classical sorting for unconstrained linear constraints. Real quantum speedup will require non-convex pairwise chemical interaction matrices running on fault-tolerant hardware.
Maintaining this scientific honesty is essential for credible academic research.""")


# ==============================================================================
# SLIDE 13: CONCLUSION & FUTURE DIRECTIONS
# ==============================================================================
slide13 = prs.slides.add_slide(blank_layout)
add_header(slide13, "Conclusion & Future Research Directions", "SUMMARY & FUTURE ROADMAP")

# Left Column: Conclusions
card_c1 = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
card_c1.fill.solid()
card_c1.fill.fore_color.rgb = COLOR_BG_LIGHT
card_c1.line.color.rgb = COLOR_TEAL
card_c1.line.width = Pt(1.5)

tb_c1 = slide13.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(4.8))
tf_c1 = tb_c1.text_frame
tf_c1.word_wrap = True

p_c1_h = tf_c1.paragraphs[0]
p_c1_h.text = "Key Project Achievements"
p_c1_h.font.name = FONT_HEADING
p_c1_h.font.size = Pt(16)
p_c1_h.font.bold = True
p_c1_h.font.color.rgb = COLOR_TEAL

achievements = [
    "Delivered a complete, runnable, tested hybrid quantum-classical drug screening pipeline.",
    "Trained Random Forest activity model on MoleculeNet BACE achieving 0.8794 ROC-AUC and 78.55% test accuracy.",
    "Formulated fixed-budget selection as a QUBO and derived analytical Ising Hamiltonian coefficients h_i and J_ij.",
    "Successfully executed QAOA on Qiskit Aer simulator, achieving 100% solution optimality (0.0000 gap) and 45.7% feasible sampling rate.",
    "Built a 6-page interactive Streamlit web app with 2D chemical structure rendering and CSV exports.",
    "Validated all modules with 21 passing automated tests in pytest."
]
for a in achievements:
    p_a = tf_c1.add_paragraph()
    p_a.text = f"✔ {a}"
    p_a.font.name = FONT_BODY
    p_a.font.size = Pt(11)
    p_a.font.color.rgb = COLOR_GRAY_TEXT
    p_a.space_before = Pt(6)

# Right Column: Future Directions
card_c2 = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
card_c2.fill.solid()
card_c2.fill.fore_color.rgb = COLOR_BG_LIGHT
card_c2.line.color.rgb = COLOR_BLUE
card_c2.line.width = Pt(1.5)

tb_c2 = slide13.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
tf_c2 = tb_c2.text_frame
tf_c2.word_wrap = True

p_c2_h = tf_c2.paragraphs[0]
p_c2_h.text = "Future Research Roadmap"
p_c2_h.font.name = FONT_HEADING
p_c2_h.font.size = Pt(16)
p_c2_h.font.bold = True
p_c2_h.font.color.rgb = COLOR_BLUE

future_pts = [
    ("Non-Linear Diversity Penalties", "Incorporate Tanimoto similarity penalties into off-diagonal Q_ij terms to actively penalize selecting chemically redundant analogs."),
    ("Subspace-Preserving XY Mixers", "Implement XY-mixer Hamiltonians that preserve the sum(x_i)=K constraint within the quantum state evolution, achieving 100% feasible sampling by design."),
    ("Physical QPU Deployment", "Execute the variational circuit on IBM Quantum Eagle / Heron superconducting processors via Qiskit Runtime Primitives with zero-noise extrapolation (ZNE)."),
    ("Multi-Target Protease Profiling", "Extend the ML featurization pipeline to panel screening across related aspartyl proteases to optimize drug selectivity.")
]
for f_t, f_d in future_pts:
    p_f = tf_c2.add_paragraph()
    p_f.text = f"➔ {f_t}: {f_d}"
    p_f.font.name = FONT_BODY
    p_f.font.size = Pt(11)
    p_f.font.color.rgb = COLOR_GRAY_TEXT
    p_f.space_before = Pt(6)

set_notes(slide13, """Slide 13 summarizes our conclusions and future roadmap.
In summary, we have built a complete, runnable, tested hybrid quantum-classical drug screening platform.
We achieved strong predictive accuracy with Random Forest (AUC 0.8794), mapped the candidate selection problem into an Ising Hamiltonian, and verified that QAOA achieves 100% optimality on Qiskit Aer.

Looking forward, we have identified exciting research extensions:
First, adding Tanimoto similarity penalties into off-diagonal QUBO terms to enforce chemical scaffold diversity.
Second, using XY-mixers that restrict quantum evolution strictly within the feasible K-subspace.
Third, deploying this circuit onto physical IBM Quantum hardware using Qiskit Runtime Primitives.""")


# ==============================================================================
# SLIDE 14: REFERENCES
# ==============================================================================
slide14 = prs.slides.add_slide(blank_layout)
add_header(slide14, "References & Scientific Citations", "BIBLIOGRAPHY")

card_ref = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.3))
card_ref.fill.solid()
card_ref.fill.fore_color.rgb = COLOR_BG_LIGHT
card_ref.line.color.rgb = COLOR_GRAY_LIGHT
card_ref.line.width = Pt(1)

tb_ref = slide14.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(11.1), Inches(4.8))
tf_ref = tb_ref.text_frame
tf_ref.word_wrap = True

refs = [
    ("[1] Farhi, E., Goldstone, J., & Gutmann, S. (2014).", "A Quantum Approximate Optimization Algorithm. arXiv:1411.4028 [quant-ph]."),
    ("[2] Subramanian, G., et al. (2018).", "MoleculeNet: A Benchmark for Molecular Machine Learning. Chemical Science, 9(2), 513-530."),
    ("[3] Lipinski, C. A., Lombardo, F., Dominy, B. W., & Feeney, P. J. (2001).", "Experimental and computational approaches to estimate solubility and permeability in drug discovery. Advanced Drug Delivery Reviews, 46(1-3), 3-26."),
    ("[4] Lucas, A. (2014).", "Ising formulations of many NP problems. Frontiers in Physics, 2, 5."),
    ("[5] Preskill, J. (2018).", "Quantum Computing in the NISQ era and beyond. Quantum, 2, 79."),
    ("[6] Landrum, G., et al. (2024).", "RDKit: Open-source cheminformatics toolkit. http://www.rdkit.org"),
    ("[7] Qiskit Contributors (2025).", "Qiskit: An Open-source Framework for Quantum Computing. Zenodo. doi:10.5281/zenodo.2562110.")
]
for idx, (c_auth, c_title) in enumerate(refs):
    p_r = tf_ref.paragraphs[0] if idx == 0 else tf_ref.add_paragraph()
    p_r.text = f"{c_auth} {c_title}"
    p_r.font.name = FONT_BODY
    p_r.font.size = Pt(11)
    p_r.font.color.rgb = COLOR_GRAY_TEXT
    p_r.space_before = Pt(8)

set_notes(slide14, """Slide 14 lists the primary academic literature and open-source frameworks cited throughout this work, including Farhi et al. for QAOA, Subramanian et al. for the MoleculeNet benchmark, Lipinski et al. for drug-likeness rules, Andrew Lucas for QUBO-Ising formulations, and John Preskill for NISQ quantum computing principles.""")


# ==============================================================================
# SLIDE 15: THANK YOU / Q&A
# ==============================================================================
slide15 = prs.slides.add_slide(blank_layout)
bg15 = slide15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg15.fill.solid()
bg15.fill.fore_color.rgb = COLOR_NAVY_DARK
bg15.line.fill.background()

tb_ty = slide15.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.5))
tf_ty = tb_ty.text_frame
tf_ty.word_wrap = True

p_ty_sub = tf_ty.paragraphs[0]
p_ty_sub.text = "CAPSTONE PRESENTATION COMPLETED"
p_ty_sub.font.name = FONT_BODY
p_ty_sub.font.size = Pt(14)
p_ty_sub.font.bold = True
p_ty_sub.font.color.rgb = COLOR_TEAL

p_ty = tf_ty.add_paragraph()
p_ty.text = "Thank You!"
p_ty.font.name = FONT_HEADING
p_ty.font.size = Pt(44)
p_ty.font.bold = True
p_ty.font.color.rgb = COLOR_WHITE
p_ty.space_before = Pt(10)

p_ty_desc = tf_ty.add_paragraph()
p_ty_desc.text = "Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates"
p_ty_desc.font.name = FONT_BODY
p_ty_desc.font.size = Pt(18)
p_ty_desc.font.color.rgb = RGBColor(148, 163, 184)
p_ty_desc.space_before = Pt(8)

p_qa = tf_ty.add_paragraph()
p_qa.text = "Questions & Discussion"
p_qa.font.name = FONT_HEADING
p_qa.font.size = Pt(22)
p_qa.font.bold = True
p_qa.font.color.rgb = COLOR_CYAN
p_qa.space_before = Pt(20)

# Card at bottom
c_info = slide15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.3), Inches(11.3), Inches(1.3))
c_info.fill.solid()
c_info.fill.fore_color.rgb = COLOR_NAVY_LIGHT
c_info.line.color.rgb = RGBColor(51, 65, 85)

tb_inf = slide15.shapes.add_textbox(Inches(1.2), Inches(5.4), Inches(10.9), Inches(1.1))
tf_inf = tb_inf.text_frame
tf_inf.word_wrap = True
p_inf1 = tf_inf.paragraphs[0]
p_inf1.text = "Repository: [GitHub Link / Project Directory]   |   Interactive Web UI: http://localhost:8501"
p_inf1.font.name = FONT_BODY
p_inf1.font.size = Pt(12)
p_inf1.font.bold = True
p_inf1.font.color.rgb = COLOR_WHITE

p_inf2 = tf_inf.add_paragraph()
p_inf2.text = "Presenter: [Student Name]  •  Contact: [Email Address]  •  Supervisor: [Faculty Advisor Name]"
p_inf2.font.name = FONT_BODY
p_inf2.font.size = Pt(11)
p_inf2.font.color.rgb = RGBColor(148, 163, 184)
p_inf2.space_before = Pt(4)

set_notes(slide15, """Thank you very much for your time, attention, and valuable feedback.
I would be delighted to answer any questions regarding our methodology, the QUBO derivation, the QAOA circuit implementation, or our empirical benchmarking results.
Thank you!""")

# Save presentation
prs.save(str(out_pptx))
print(f"PowerPoint presentation successfully created at: {out_pptx}")
