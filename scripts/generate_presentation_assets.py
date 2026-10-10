"""
Script: generate_presentation_assets.py
Generates high-resolution publication-quality PNG charts, diagrams, and molecular renderings
for the academic PowerPoint presentation and stores them in deliverables/presentation_package/.
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.metrics import roc_curve, auc
from rdkit import Chem
from rdkit.Chem import Draw

# Set styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

out_dir = Path("deliverables/presentation_package")
out_dir.mkdir(parents=True, exist_ok=True)


def generate_roc_and_cm():
    # 1. Confusion Matrix
    eval_path = Path("results/model_evaluation.json")
    pred_path = Path("results/test_predictions.csv")
    if not eval_path.exists() or not pred_path.exists():
        print("Model evaluation or test predictions missing.")
        return
        
    with open(eval_path, "r") as f:
        metrics = json.load(f)
    cm = np.array(metrics["confusion_matrix"])
    
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=10)
    
    classes = ["Inactive (0)", "Active (1)"]
    tick_marks = np.arange(len(classes))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(classes, fontsize=11, fontweight="bold")
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(classes, fontsize=11, fontweight="bold")
    
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], "d"),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "#1e293b",
                    fontsize=16, fontweight="bold")
                    
    ax.set_ylabel("True Experimental Label", fontsize=12, fontweight="bold")
    ax.set_xlabel("Predicted Model Label", fontsize=12, fontweight="bold")
    ax.set_title("Random Forest Confusion Matrix\n(Test Set: 303 compounds)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    fig.savefig(out_dir / "confusion_matrix.png", dpi=300)
    plt.close(fig)
    print("Saved confusion_matrix.png")
    
    # 2. ROC Curve
    df_preds = pd.read_csv(pred_path)
    y_true = df_preds["Class"].to_numpy()
    y_prob = df_preds["predicted_prob_active"].to_numpy()
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    ax.plot(fpr, tpr, color="#0284c7", lw=3, label=f"Random Forest (AUC = {roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle="--", label="Random Guessing (AUC = 0.500)")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11, fontweight="bold")
    ax.set_ylabel("True Positive Rate (Sensitivity)", fontsize=11, fontweight="bold")
    ax.set_title("Receiver Operating Characteristic (ROC) Curve\n(BACE-1 Bioactivity)", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="lower right", fontsize=10, frameon=True)
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    fig.savefig(out_dir / "roc_curve.png", dpi=300)
    plt.close(fig)
    print("Saved roc_curve.png")


def generate_qaoa_plots():
    screen_path = Path("results/screening_results.json")
    if not screen_path.exists():
        print("Screening results missing.")
        return
        
    with open(screen_path, "r") as f:
        data = json.load(f)
        
    # 1. Convergence Curve
    history = data["qaoa"]["optimization_history"]
    if history:
        iters = [h["iteration"] for h in history]
        energies = [h["energy"] for h in history]
        
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
        ax.plot(iters, energies, marker="o", markersize=6, color="#0d9488", lw=2.5, label="Expected Energy <H_C>")
        ax.set_xlabel("COBYLA Optimizer Iteration", fontsize=11, fontweight="bold")
        ax.set_ylabel("Energy Expectation <H_C>", fontsize=11, fontweight="bold")
        ax.set_title("QAOA Variational Parameter Convergence\n(Depth p = 1)", fontsize=13, fontweight="bold", pad=12)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(fontsize=10, loc="upper right")
        plt.tight_layout()
        fig.savefig(out_dir / "qaoa_convergence.png", dpi=300)
        plt.close(fig)
        print("Saved qaoa_convergence.png")
        
    # 2. Measurement Distribution
    dist = data["qaoa"]["distribution"]
    top_items = sorted(dist.items(), key=lambda kv: kv[1]["probability"], reverse=True)[:10]
    bitstrings = [k for k, _ in top_items]
    probs = [v["probability"] * 100 for _, v in top_items]
    feasibles = [v["is_feasible"] for _, v in top_items]
    colors = ["#16a34a" if f else "#dc2626" for f in feasibles]
    
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    bars = ax.bar(bitstrings, probs, color=colors, width=0.65, edgecolor="#334155", lw=0.8)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.3, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        
    ax.set_ylabel("Measurement Probability (%)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Sampled Computational Basis State |x>", fontsize=11, fontweight="bold")
    ax.set_title("QAOA Aer Simulator Measurement Distribution (1024 Shots)\nGreen: Feasible (K=3), Red: Infeasible", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylim([0, max(probs) * 1.25])
    plt.xticks(rotation=35, ha="right", fontsize=9, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    fig.savefig(out_dir / "measurement_distribution.png", dpi=300)
    plt.close(fig)
    print("Saved measurement_distribution.png")
    
    # 3. Method Comparison Bar Chart
    comp = data["comparison"]["methods"]
    methods = ["QAOA", "Top-K", "Exact QUBO"]
    energies = [abs(comp[m]["energy"]) for m in ["QAOA", "Top-K", "Exact_QUBO"]]
    scores = [comp[m]["total_score"] for m in ["QAOA", "Top-K", "Exact_QUBO"]]
    
    x = np.arange(len(methods))
    width = 0.32
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    rects1 = ax.bar(x - width/2, scores, width, label="Total Candidate Score", color="#2563eb", edgecolor="#1e293b")
    rects2 = ax.bar(x + width/2, energies, width, label="|QUBO Objective Energy|", color="#10b981", edgecolor="#1e293b")
    
    for r in rects1:
        ax.text(r.get_x() + r.get_width()/2., r.get_height() + 0.03, f"{r.get_height():.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for r in rects2:
        ax.text(r.get_x() + r.get_width()/2., r.get_height() + 0.03, f"{r.get_height():.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        
    ax.set_ylabel("Value", fontsize=11, fontweight="bold")
    ax.set_title("Benchmarking: QAOA vs Classical Baselines\n(Identical Optimal Energy = -1.7179, Gap = 0.000)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=11, fontweight="bold")
    ax.set_ylim([0, 2.2])
    ax.legend(loc="upper right", fontsize=9.5)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    fig.savefig(out_dir / "method_comparison.png", dpi=300)
    plt.close(fig)
    print("Saved method_comparison.png")


def generate_chemical_depictions():
    pred_path = Path("results/test_predictions.csv")
    if not pred_path.exists():
        return
    df = pd.read_csv(pred_path)
    
    # Selected candidates in optimal bitstring 10100010: MOL_BACE_1111, MOL_BACE_558, MOL_BACE_1121
    target_cids = ["BACE_1111", "BACE_558", "BACE_1121"]
    mols = []
    legends = []
    
    for cid in target_cids:
        sub = df[df["CID"] == cid]
        if not sub.empty:
            smi = sub.iloc[0]["mol"]
            m = Chem.MolFromSmiles(smi)
            if m:
                mols.append(m)
                legends.append(f"CID: {cid}\nP(act): {sub.iloc[0]['predicted_prob_active']:.2f} | pIC50: {sub.iloc[0]['pIC50']:.1f}")
                
    if mols:
        img = Draw.MolsToGridImage(mols, molsPerRow=3, subImgSize=(350, 280), legends=legends, useSVG=False)
        img.save(str(out_dir / "selected_molecules.png"))
        print("Saved selected_molecules.png")


def generate_architecture_flowchart():
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=300)
    ax.axis("off")
    
    boxes = [
        {"text": "MoleculeNet\nBACE Data\n(1,513 Compounds)", "x": 0.05, "w": 0.15, "color": "#e0f2fe", "border": "#0284c7"},
        {"text": "RDKit Featurization\n(ECFP4 Fingerprints\n+ 7 Descriptors)", "x": 0.24, "w": 0.16, "color": "#f0fdf4", "border": "#16a34a"},
        {"text": "Random Forest\nClassifier\n(AUC = 0.8794)", "x": 0.44, "w": 0.15, "color": "#fef3c7", "border": "#d97706"},
        {"text": "QUBO & Ising\nHamiltonian Mapping\n(Cardinality Penalty)", "x": 0.63, "w": 0.16, "color": "#f3e8ff", "border": "#9333ea"},
        {"text": "QAOA Quantum Circuit\n(Aer Simulator,\nCOBYLA Optimizer)", "x": 0.83, "w": 0.15, "color": "#fee2e2", "border": "#dc2626"}
    ]
    
    y = 0.35
    h = 0.38
    
    for b in boxes:
        rect = patches.FancyBboxPatch((b["x"], y), b["w"], h,
                                      boxstyle="round,pad=0.03,rounding_size=0.04",
                                      facecolor=b["color"], edgecolor=b["border"], lw=2.2)
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2., y + h/2., b["text"],
                ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0f172a")
                
    # Draw arrows
    for i in range(len(boxes) - 1):
        x_start = boxes[i]["x"] + boxes[i]["w"] + 0.005
        x_end = boxes[i+1]["x"] - 0.005
        ax.annotate("", xy=(x_end, y + h/2.), xytext=(x_start, y + h/2.),
                    arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#334155", mutation_scale=16))
                    
    ax.set_xlim([0, 1.02])
    ax.set_ylim([0, 1.0])
    plt.tight_layout()
    fig.savefig(out_dir / "architecture_flowchart.png", dpi=300)
    plt.close(fig)
    print("Saved architecture_flowchart.png")


def generate_qaoa_circuit_diagram():
    fig, ax = plt.subplots(figsize=(9, 4.0), dpi=300)
    ax.axis("off")
    
    # Draw qubit wires
    qubits = [f"|0⟩ q_{i}" for i in range(4)]
    for i, q in enumerate(qubits):
        y_pos = 0.8 - i * 0.2
        ax.text(0.04, y_pos, q, fontsize=11, fontweight="bold", va="center")
        ax.plot([0.13, 0.96], [y_pos, y_pos], color="#64748b", lw=1.8, zorder=1)
        
    # Hadamard block
    rect_h = patches.FancyBboxPatch((0.16, 0.12), 0.10, 0.74, boxstyle="round,pad=0.02", facecolor="#dbeafe", edgecolor="#2563eb", lw=2, zorder=2)
    ax.add_patch(rect_h)
    ax.text(0.21, 0.49, "H^⊗N\n(State Prep)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1e3a8a")
    
    # Cost Unitary block
    rect_c = patches.FancyBboxPatch((0.33, 0.12), 0.24, 0.74, boxstyle="round,pad=0.02", facecolor="#ede9fe", edgecolor="#7c3aed", lw=2, zorder=2)
    ax.add_patch(rect_c)
    ax.text(0.45, 0.49, "Cost Unitary U(C, γ)\nR_Z(2γ h_i)\n+ R_ZZ(2γ J_ij)", ha="center", va="center", fontsize=10, fontweight="bold", color="#5b21b6")
    
    # Mixer Unitary block
    rect_m = patches.FancyBboxPatch((0.63, 0.12), 0.18, 0.74, boxstyle="round,pad=0.02", facecolor="#fef3c7", edgecolor="#d97706", lw=2, zorder=2)
    ax.add_patch(rect_m)
    ax.text(0.72, 0.49, "Mixer U(B, β)\n∏ R_X(2β)", ha="center", va="center", fontsize=10, fontweight="bold", color="#92400e")
    
    # Measurement block
    rect_meas = patches.FancyBboxPatch((0.87, 0.12), 0.08, 0.74, boxstyle="round,pad=0.02", facecolor="#fee2e2", edgecolor="#dc2626", lw=2, zorder=2)
    ax.add_patch(rect_meas)
    ax.text(0.91, 0.49, "Meas\n(Z-basis)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#991b1b")
    
    ax.set_xlim([0, 1.0])
    ax.set_ylim([0, 1.0])
    plt.tight_layout()
    fig.savefig(out_dir / "qaoa_circuit_diagram.png", dpi=300)
    plt.close(fig)
    print("Saved qaoa_circuit_diagram.png")


if __name__ == "__main__":
    generate_roc_and_cm()
    generate_qaoa_plots()
    generate_chemical_depictions()
    generate_architecture_flowchart()
    generate_qaoa_circuit_diagram()
    print("All presentation visual assets generated successfully.")
