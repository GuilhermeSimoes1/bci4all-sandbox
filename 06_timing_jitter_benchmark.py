import time
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Standard flash presentation rate in P300 spellers (~8 flashes/second)
TARGET_MS = 125.0

# Number of stimulus repetitions for statistical analysis
N_TRIALS = 100

# Initialize Qt GUI application (required for QTimer and PyQtGraph plotting)
app = QApplication([])


# Qtimer benchmark my colleague's approach
qtimer_times = []
last_t = 0.0

def on_tick():
    """Callback triggered by QTimer on every tick."""
    global last_t
    now = time.perf_counter()
    
    # Calculate actual elapsed time since the previous flash
    qtimer_times.append((now - last_t) * 1000.0)
    
    # Update reference timestamp for the next lap 
    last_t = now
    
    # Stop benchmark once all trials are collected
    if len(qtimer_times) >= N_TRIALS:
        timer.stop()
        app.quit()

timer = QTimer()
timer.timeout.connect(on_tick)

# Start the stopwatch and launch QTimer
last_t = time.perf_counter()
timer.start(int(TARGET_MS))

# Run Qt event loop until all trials are finished
app.exec()


# High-precision timing benchmark - PsychoPy / hardware clock model
precision_times = []
next_t = time.perf_counter() + (TARGET_MS / 1000.0)
prev_t = time.perf_counter()

for _ in range(N_TRIALS):
    # busy-wait
    while time.perf_counter() < next_t:
        pass
    
    now = time.perf_counter()
    precision_times.append((now - prev_t) * 1000.0)
    
    # Advance reference to the next ideal timestamp
    prev_t = now
    next_t += (TARGET_MS / 1000.0)


# Statistical analysis and console report
# Standard deviation represents timing jitter 
q_std = np.std(qtimer_times)
p_std = np.std(precision_times)  

print(f"\n[BENCHMARK] Target Interval: {TARGET_MS} ms ({N_TRIALS} trials)")
print(f"-> QTimer Jitter:    ±{q_std:.2f} ms")
print(f"-> Precision Jitter: ±{p_std:.3f} ms \n")


# Comparative visualization
win = pg.plot(title="Timing Jitter: QTimer (Red) vs Precision (Green)")
win.setLabel("left", "Measured Interval (ms)")
win.setLabel("bottom", "Flash Number (Trial)")
win.showGrid(x=True, y=True, alpha=0.3)
win.addLegend()

# Yellow dashed line: Ideal theoretical interval (125 ms)
win.plot([0, N_TRIALS], [TARGET_MS, TARGET_MS], 
         pen=pg.mkPen("y", width=2, style=pg.QtCore.Qt.DashLine), 
         name="Target (125 ms)")

# Red curve: QTimer timing instability
win.plot(qtimer_times, 
         pen=pg.mkPen("r", width=1.5), 
         name=f"QTimer (±{q_std:.2f} ms)")

# Green curve: High-precision timing stability
win.plot(precision_times, 
         pen=pg.mkPen("g", width=2), 
         name=f"Precision (±{p_std:.3f} ms)")

# Keep window open until we close it
pg.exec()
