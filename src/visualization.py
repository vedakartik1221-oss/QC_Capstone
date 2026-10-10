"""
Visualization Module
Generates interactive Plotly figures for molecular properties,
model evaluation, QAOA optimization convergence, bitstring distributions,
and classical vs quantum benchmarking.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics import roc_curve, auc


def plot_confusion_matrix(cm: List[List[int]]) -> go.Figure:
    """Plot interactive confusion matrix heatmap."""
    z = np.array(cm)
    x = ["Predicted Inactive (0)", "Predicted Active (1)"]
    y = ["Actual Inactive (0)", "Actual Active (1)"]
    
    # Annotations
    annotations = []
    for i in range(len(y)):
        for j in range(len(x)):
            annotations.append(
                dict(
                    x=x[j],
                    y=y[i],
                    text=str(z[i, j]),
                    font=dict(color="white" if z[i, j] > np.max(z) / 2 else "black", size=18),
                    showarrow=False
                )
            )
            
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale="Blues",
            showscale=True
        )
    )
    fig.update_layout(
        title="<b>Confusion Matrix (Biological Activity Prediction)</b>",
        annotations=annotations,
        xaxis_title="Predicted Label",
        yaxis_title="True Experimental Label",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def plot_roc_curve(y_true: np.ndarray, y_prob: np.ndarray) -> go.Figure:
    """Plot interactive ROC curve with AUC score."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=f"Random Forest (AUC = {roc_auc:.3f})",
            line=dict(color="#1f77b4", width=3)
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Random Guessing (AUC = 0.500)",
            line=dict(color="gray", dash="dash", width=1.5)
        )
    )
    fig.update_layout(
        title="<b>Receiver Operating Characteristic (ROC) Curve</b>",
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Sensitivity)",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(x=0.55, y=0.1)
    )
    return fig


def plot_qaoa_convergence(history: List[Dict[str, Any]]) -> Optional[go.Figure]:
    """Plot QAOA expected energy convergence across optimizer iterations."""
    if not history:
        return None
        
    df_hist = pd.DataFrame(history)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_hist["iteration"],
            y=df_hist["energy"],
            mode="lines+markers",
            marker=dict(size=6, color="#00bcd4"),
            line=dict(color="#00838f", width=2.5),
            name="Expected Energy <H_C>"
        )
    )
    fig.update_layout(
        title="<b>QAOA Classical Parameter Optimization Convergence</b>",
        xaxis_title="Optimizer Iteration (COBYLA)",
        yaxis_title="Cost Expectation <H_C>",
        template="plotly_white",
        height=380,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def plot_measurement_distribution(distribution: Dict[str, Dict[str, Any]], k_target: int, top_n: int = 15) -> go.Figure:
    """Plot distribution of sampled bitstrings highlighting feasibility."""
    # Sort by probability descending
    items = sorted(distribution.items(), key=lambda kv: kv[1]["probability"], reverse=True)[:top_n]
    
    bitstrings = [k for k, _ in items]
    probs = [v["probability"] for _, v in items]
    energies = [v["energy"] for _, v in items]
    feasibles = [v["is_feasible"] for _, v in items]
    colors = ["#2ca02c" if f else "#d62728" for f in feasibles]
    hover_texts = [
        f"Bitstring: {b}<br>Probability: {p:.4f}<br>Energy: {e:.3f}<br>Feasible (sum={b.count('1')} == K={k_target}): {'YES' if f else 'NO'}"
        for b, p, e, f in zip(bitstrings, probs, energies, feasibles)
    ]
    
    fig = go.Figure(
        data=go.Bar(
            x=bitstrings,
            y=probs,
            marker_color=colors,
            text=[f"{p*100:.1f}%" for p in probs],
            textposition="auto",
            hovertext=hover_texts,
            hoverinfo="text"
        )
    )
    fig.update_layout(
        title="<b>QAOA Measurement Probability Distribution</b> (Green: Feasible sum(x)=K, Red: Infeasible)",
        xaxis_title="Sampled Bitstring",
        yaxis_title="Measurement Probability",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=40, t=60, b=50)
    )
    return fig


def plot_method_comparison(comparison: Dict[str, Any]) -> go.Figure:
    """Grouped bar chart comparing QAOA, Top-K, and Exact QUBO."""
    methods = ["QAOA", "Top-K", "Exact_QUBO"]
    energies = [comparison["methods"][m]["energy"] for m in methods]
    scores = [comparison["methods"][m]["total_score"] for m in methods]
    gaps = [comparison["methods"][m]["optimality_gap"] for m in methods]
    
    fig = go.Figure(
        data=[
            go.Bar(name="Total Score (Higher is Better)", x=methods, y=scores, marker_color="#2ca02c"),
            go.Bar(name="QUBO Energy (Lower is Better)", x=methods, y=energies, marker_color="#1f77b4"),
            go.Bar(name="Optimality Gap (0 is Optimal)", x=methods, y=gaps, marker_color="#ff7f0e")
        ]
    )
    fig.update_layout(
        barmode="group",
        title="<b>Optimization Method Comparison (QAOA vs Baselines)</b>",
        yaxis_title="Value",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_property_distributions(df: pd.DataFrame, property_name: str = "MW") -> go.Figure:
    """Plot physicochemical property distribution stratified by activity class."""
    calc_col = f"calc_{property_name}" if f"calc_{property_name}" in df.columns else property_name
    if calc_col not in df.columns:
        return go.Figure()
        
    fig = px.histogram(
        df,
        x=calc_col,
        color="Class",
        barmode="overlay",
        color_discrete_map={1: "#2ca02c", 0: "#d62728"},
        labels={"Class": "Activity Label", calc_col: property_name},
        title=f"<b>Distribution of {property_name} by Biological Activity</b> (1=Active, 0=Inactive)",
        template="plotly_white"
    )
    fig.update_layout(height=380, margin=dict(l=40, r=40, t=60, b=40))
    return fig
