"""
plot_utils.py - Visualization utilities for ERP stability and P300 analysis.
Encapsulates all Matplotlib styling, subplots, and publication-ready reporting.
"""

import matplotlib.pyplot as plt

# show target and non-target mean +/- std
def plot_erp_stability_panels(
    time_axis, 
    m_tgt, s_tgt, n_tgt, 
    m_nontgt, s_nontgt, n_nontgt, 
    channel_name="Pz",
    save_path="p300_Pz_target_and_nontarget.png", 
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


# show only the standard deviation over time for target and non-target 
def plot_sigma_over_time(
    time_axis, 
    s_tgt, 
    s_nontgt, 
    channel_name="Pz", 
    save_path="p300_sigma_over_time.png", 
    show=True
):
    """Plots standard deviation (sigma) over time for Target and Non-Target."""
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Target sigma (red) and Non-Target sigma (cyan/blue)
    ax.plot(time_axis, s_tgt, color="#FF5252", linewidth=2.5, label=f"Target σ(t) - Variabilidade Alvo")
    ax.plot(time_axis, s_nontgt, color="#40C4FF", linewidth=2.0, linestyle="--", label=f"Non-Target σ(t) - Variabilidade Ruído")
    
    # Stimulus onset reference line
    ax.axvline(0.0, color="white", linestyle=":", linewidth=1.5, alpha=0.8, label="Início do Flash (0 ms)")
    ax.axvline(300.0, color="#FFD700", linestyle=":", linewidth=1.2, alpha=0.6, label="Janela P300 (~300 ms)")
    
    ax.set_title(f"Variabilidade Temporal σ(t) - Canal {channel_name}", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Tempo após estímulo (ms)", fontsize=11)
    ax.set_ylabel("Desvio Padrão σ (µV)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.3)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"[PLOT] Gráfico σ(t) guardado em '{save_path}'")
    if show:
        plt.show()
    plt.close(fig)

