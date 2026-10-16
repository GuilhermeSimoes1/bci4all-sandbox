"""
plot_utils.py - Visualization utilities for ERP stability and P300 analysis.
Encapsulates all Matplotlib styling, subplots, and publication-ready reporting.
"""

import matplotlib.pyplot as plt


def plot_erp_stability_panels(
    time_axis, 
    m_tgt, s_tgt, n_tgt, 
    m_nontgt, s_nontgt, n_nontgt, 
    channel_name="PO7",
    save_path="p300_po7_target_and_nontarget.png", 
    show=True
):
    """
    Renders and saves a 2-panel publication-ready report:
    - Top Subplot: Target ERP with Mean ± 1 Standard Deviation.
    - Bottom Subplot: Non-Target ERP with Mean ± 1 Standard Deviation.
    """
    plt.style.use("dark_background")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True, sharey=True)
    fig.suptitle(f"P300 ERP Stability Analysis: Channel {channel_name} (Mean ± 1σ)", fontsize=14, fontweight="bold")

    # --- Top Subplot: TARGET ---
    ax1.plot(time_axis, m_tgt + s_tgt, color="red", linestyle="--", linewidth=1.5, label="Mean + 1σ")
    ax1.plot(time_axis, m_tgt, color="cyan", linewidth=2.5, label="Target Mean (μ)")
    ax1.plot(time_axis, m_tgt - s_tgt, color="#FFD600", linestyle="--", linewidth=1.5, label="Mean - 1σ")
    ax1.fill_between(time_axis, m_tgt - s_tgt, m_tgt + s_tgt, color="cyan", alpha=0.15, label="Variance Envelope (±1σ)")
    ax1.axvline(0, color="white", linestyle=":", alpha=0.7, label="Stimulus Onset (0 ms)")
    ax1.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax1.set_title(f"Target Events (N = {n_tgt}) — Characteristic P300 Peak at 300 ms", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Amplitude (µV)", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.legend(loc="upper right", fontsize=9)

    # --- Bottom Subplot: NON-TARGET ---
    ax2.plot(time_axis, m_nontgt + s_nontgt, color="coral", linestyle="--", linewidth=1.5, label="Mean + 1σ")
    ax2.plot(time_axis, m_nontgt, color="deepskyblue", linewidth=2.5, label="Non-Target Mean (μ)")
    ax2.plot(time_axis, m_nontgt - s_nontgt, color="khaki", linestyle="--", linewidth=1.5, label="Mean - 1σ")
    ax2.fill_between(time_axis, m_nontgt - s_nontgt, m_nontgt + s_nontgt, color="deepskyblue", alpha=0.15, label="Variance Envelope (±1σ)")
    ax2.axvline(0, color="white", linestyle=":", alpha=0.7, label="Stimulus Onset (0 ms)")
    ax2.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax2.set_title(f"Non-Target Events (N = {n_nontgt}) — Flat Baseline Response", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Time after stimulus (ms)", fontsize=11)
    ax2.set_ylabel("Amplitude (µV)", fontsize=11)
    ax2.set_ylim(-35, 45)
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"\n[SUCCESS] Report saved to '{save_path}' (300 DPI)!")
    
    if show:
        plt.show()
