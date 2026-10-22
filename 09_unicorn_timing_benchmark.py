"""
09_unicorn_timing_benchmark.py - Side B Timing Benchmark (Ultra-MVP)
Measures the Unicorn BCI Core-8 Bluetooth packet delivery cadence,
block sizes, sample loss, and reception jitter inside the gpype pipeline.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from pylsl import local_clock
from PySide6.QtCore import QCoreApplication
import gpype as gp

TARGET_SAMPLES = 2500  # Exactly 10 seconds of EEG at 250 Hz


class UnicornInspector(gp.INode):
    """Spy node to intercept and timestamp every Bluetooth block from the amplifier."""
    def __init__(self, target_samples=TARGET_SAMPLES):
        super().__init__(
            name="UnicornInspector",
            input_ports=[gp.IPort.Configuration(name="in", timing=gp.Constants.Timing.SYNC)],
            output_ports=[],
        )
        self.target_samples = target_samples
        self.intervals_ms = []
        self.block_sizes = []
        self.last_t = None
        self.start_t = None
        self.end_t = None
        self.total_samples = 0
        self.finished = False

    def step(self, data):
        now = local_clock()
        block = data.get("in")
        
        if block is not None and len(block) > 0:
            if self.start_t is None:
                self.start_t = now

            if self.last_t is not None:
                dt_ms = (now - self.last_t) * 1000.0
                self.intervals_ms.append(dt_ms)

            self.last_t = now
            
            n_samples = len(block)
            self.block_sizes.append(n_samples)
            self.total_samples += n_samples

            # Progress print
            if len(self.block_sizes) % 25 == 0:
                print(f"[BLE] Recebido bloco #{len(self.block_sizes)}: {n_samples} amostras | Total: {self.total_samples}/{self.target_samples}")

            # Mark as finished when target is reached
            if self.total_samples >= self.target_samples and not self.finished:
                self.end_t = now
                self.finished = True
                print("\n[INFO] Meta de 10 segundos atingida! A finalizar aquisição...")

        return {}

    def compute(self, data):
        return self.step(data)


def main():
    print("=" * 65)
    print("       BENCHMARK DE HARDWARE E BLUETOOTH (SIDE B - UNICORN)")
    print("=" * 65)
    print("[INFO] A ligar ao Unicorn BCI Core-8 via BLE...")
    
    app = gp.MainApp()
    p = gp.Pipeline()

    amp = gp.BCICore()
    inspector = UnicornInspector(target_samples=TARGET_SAMPLES)

    p.connect(amp, inspector)

    p.start()
    print("[INFO] Ligação estabelecida! A registar pacotes durante 10 segundos...\n")

    start_wait = time.time()
    try:
        # Loop não-bloqueante que processa os eventos do Qt e sai assim que terminar
        while not inspector.finished and (time.time() - start_wait < 15.0):
            QCoreApplication.processEvents()
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\n[INFO] Interrompido pelo utilizador.")
    finally:
        p.stop()
        p.close()

    # Relatório Estatístico e Gráficos
    if len(inspector.intervals_ms) >= 10:
        intervals = np.array(inspector.intervals_ms)
        sizes = np.array(inspector.block_sizes)
        
        total_time = (inspector.end_t - inspector.start_t) if inspector.end_t else 10.0
        effective_fs = inspector.total_samples / total_time
        
        mean_dt = np.mean(intervals)
        std_dt = np.std(intervals, ddof=1)
        mean_size = np.mean(sizes)

        print("\n" + "=" * 65)
        print("           RELATÓRIO DE SINCRONISMO E BLUETOOTH (LADO B)")
        print("=" * 65)
        print(f"Total de Amostras Recebidas:       {inspector.total_samples}")
        print(f"Tempo Real Decorrido:              {total_time:.3f} s")
        print(f"Taxa de Amostragem Efetiva (Fs):   {effective_fs:.2f} Hz (Nominal: 250.0 Hz)")
        print(f"Tamanho Médio de Bloco BLE:        {mean_size:.1f} amostras/bloco")
        print(f"Intervalo Médio Entre Pacotes:     {mean_dt:.2f} ms (Teórico: 16.0 ms)")
        print(f"Jitter de Chegada BLE (Std Dev):   ±{std_dt:.2f} ms")
        print("=" * 65)

        # Plot: Distribution and Timeline of Bluetooth deliveries
        plt.style.use("dark_background")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={'width_ratios': [2, 1]})

        # Panel 1: Delivery Intervals over time
        ax1.plot(intervals, color="#40C4FF", marker="o", markersize=2.5, linewidth=1, label="Intervalo entre Chegadas (ms)")
        ax1.axhline(16.0, color="#FFD700", linestyle=":", linewidth=1.5, label="Ritmo Teórico BLE (16.0 ms)")
        ax1.axhline(mean_dt, color="#FF5252", linestyle="--", linewidth=1.5, label=f"Média Real ({mean_dt:.1f} ms)")
        ax1.fill_between(range(len(intervals)), mean_dt - std_dt, mean_dt + std_dt, color="#FF5252", alpha=0.15, label=f"Jitter (±{std_dt:.2f} ms)")
        ax1.set_ylim(0, 35)
        ax1.set_title("Cadência de Chegada de Pacotes Bluetooth", fontweight="bold")
        ax1.set_xlabel("Número do Pacote BLE")
        ax1.set_ylabel("Intervalo (ms)")
        ax1.grid(True, linestyle="--", alpha=0.3)
        ax1.legend(loc="upper right")

        # Panel 2: Histogram
        ax2.hist(intervals, bins=15, color="#FFD54F", edgecolor="black", alpha=0.8)
        ax2.axvline(16.0, color="#FFD700", linestyle=":", linewidth=1.5)
        ax2.axvline(mean_dt, color="#FF5252", linestyle="--", linewidth=1.5)
        ax2.set_xlim(0, 35)
        ax2.set_title("Distribuição do Atraso BLE", fontweight="bold")
        ax2.set_xlabel("Intervalo (ms)")
        ax2.set_ylabel("Contagem")
        ax2.grid(True, linestyle="--", alpha=0.3)

        plt.tight_layout()
        plt.savefig("benchmark_unicorn_timing.png", dpi=150)
        print("\n[SUCESSO] Gráfico guardado em 'benchmark_unicorn_timing.png'!")
        plt.show()

    else:
        print("[AVISO] Amostras insuficientes para gerar estatísticas.")


if __name__ == "__main__":
    main()
