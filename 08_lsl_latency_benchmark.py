"""
08_lsl_latency_benchmark.py - Side A Timing Benchmark (Ultra-MVP)
Measures the transmission delay and jitter from the PsychoPy monitor flip (V-Sync)
to the moment the marker arrives at the listening process via LSL.
"""

import numpy as np
import matplotlib.pyplot as plt
from pylsl import StreamInlet, resolve_byprop, local_clock

STREAM_NAME = "P300_Markers"

def main():
    print("=" * 60)
    print("       BENCHMARK DE SINCRONISMO LSL (SIDE A)")
    print("=" * 60)
    print(f"[LSL] À procura da stream '{STREAM_NAME}'...")

    streams = resolve_byprop("name", STREAM_NAME, timeout=10.0)
    if not streams:
        print(f"[ERRO] Stream '{STREAM_NAME}' não encontrada! Corre o 07 primeiro.")
        return

    inlet = StreamInlet(streams[0])
    print(f"[LSL] CONECTADO a '{STREAM_NAME}'!")
    print("[INFO] À escuta de marcadores... Fecha o 07 com ESC quando quiseres.\n")

    latencies_ms = []

    try:
        while True:
            sample, ts_flip = inlet.pull_sample(timeout=1.0)
            if sample and ts_flip:
                t_receive = local_clock()
                delay_ms = (t_receive - ts_flip) * 1000.0
                latencies_ms.append(delay_ms)
                print(f"-> Marcador {int(sample[0])} | Latência: {delay_ms:6.3f} ms (Trial #{len(latencies_ms)})")
    except KeyboardInterrupt:
        print("\n[INFO] Benchmark terminado.")

    if len(latencies_ms) >= 5:
        lat = np.array(latencies_ms)
        mean_lat = np.mean(lat)
        std_lat = np.std(lat, ddof=1)

        print("\n" + "=" * 60)
        print(f"Total Ensaios:                  {len(lat)}")
        print(f"Latência Média:                 {mean_lat:.3f} ms")
        print(f"Jitter Temporal (Desvio-Padrão): ±{std_lat:.3f} ms")
        print("=" * 60)

        plt.style.use("dark_background")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={'width_ratios': [2, 1]})

        # Latency plot
        ax1.plot(lat, color="#40C4FF", marker="o", markersize=2.5, linewidth=1, label="Latência por Ensaio")
        ax1.axhline(mean_lat, color="#FF5252", linestyle="--", linewidth=1.5, label=f"Média ({mean_lat:.3f} ms)")
        ax1.fill_between(range(len(lat)), mean_lat - std_lat, mean_lat + std_lat, color="#FF5252", alpha=0.15, label=f"Jitter (±{std_lat:.3f} ms)")
        ax1.axhline(1.0, color="#FFD700", linestyle=":", linewidth=1.2, label="Limite Sub-ms (1.0 ms)")
        ax1.set_ylim(0, 1.0)  # <- Fix scale
        ax1.set_title("Estabilidade de Transporte LSL (Zero Drift)", fontweight="bold")
        ax1.set_xlabel("Número do Ensaio")
        ax1.set_ylabel("Latência (ms)")
        ax1.grid(True, linestyle="--", alpha=0.3)
        ax1.legend(loc="upper right")

        # Histogram
        ax2.hist(lat, bins=15, color="#69F0AE", edgecolor="black", alpha=0.8)
        ax2.axvline(mean_lat, color="#FF5252", linestyle="--", linewidth=1.5)
        ax2.axvline(1.0, color="#FFD700", linestyle=":", linewidth=1.2)
        ax2.set_xlim(0, 1.0)  # <- Fix scale
        ax2.set_title("Distribuição do Atraso", fontweight="bold")
        ax2.set_xlabel("Latência (ms)")
        ax2.set_ylabel("Contagem")
        ax2.grid(True, linestyle="--", alpha=0.3)

        plt.tight_layout()
        plt.savefig("benchmark_lsl_latency.png", dpi=150)
        print("\n[SUCESSO] Gráfico guardado em 'benchmark_lsl_latency.png'!")
        plt.show()

if __name__ == "__main__":
    main()
