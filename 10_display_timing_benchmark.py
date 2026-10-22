"""
10_display_timing_benchmark.py
==============================
Realistic Display & V-Sync Benchmark using the exact 2-Box P300 Oddball 
paradigm elements from 07_psychopy_single_stimulus.py:
  - Dual cards (card_left, card_right)
  - Text stimuli (A, B, and hint text)
  - Real timing: 125 ms Flash / 800 ms ISI

Outputs:
  - Real-world rendering latency distribution.
  - V-Sync frame stability figure: 'benchmark_display_timing.png'.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from psychopy import visual, core, event

# ---------------------------------------------------------
# Configuration (Exact match with 07_psychopy_single_stimulus)
# ---------------------------------------------------------
FULLSCREEN = True        # Set to True for exclusive hardware V-Sync
WINDOW_SIZE = (900, 600)
N_TRIALS = 30             # 30 trials is enough (~30 seconds test)
FLASH_MS = 125.0
ISI_MS = 800.0

print("[INFO] Initializing PsychoPy display window (2-Box Paradigm)...")
win = visual.Window(
    size=WINDOW_SIZE,
    fullscr=FULLSCREEN,
    color=(-1, -1, -1),
    units="pix",
    waitBlanking=True
)

win.recordFrameIntervals = True

refresh_rate = win.getActualFrameRate() or 60.0
expected_frame_ms = 1000.0 / refresh_rate
flash_frames = max(1, int(round((FLASH_MS / 1000.0) * refresh_rate)))
isi_frames = max(1, int(round((ISI_MS / 1000.0) * refresh_rate)))

print(f"[INFO] Monitor Refresh: {refresh_rate:.2f} Hz ({expected_frame_ms:.2f} ms/frame)")
print(f"[INFO] Flash Frames: {flash_frames} (~{FLASH_MS:.1f} ms) | ISI Frames: {isi_frames} (~{ISI_MS:.1f} ms)")

# ---------------------------------------------------------
# Visual Stimuli (Matching 07)
# ---------------------------------------------------------
BOX_OFFSET_X = 300
BOX_SIZE = 180

IDLE_FILL = (-0.75, -0.75, -0.75)
IDLE_LINE = (-0.4, -0.4, -0.4)
IDLE_TEXT = (-0.1, -0.1, -0.1)

FLASH_FILL = (1.0, 0.84, 0.0)    # Gold
FLASH_LINE = (1.0, 1.0, 1.0)
FLASH_TEXT = (-1.0, -1.0, -1.0)

card_left = visual.Rect(win, width=BOX_SIZE, height=BOX_SIZE, pos=(-BOX_OFFSET_X, 0), lineWidth=4)
label_left = visual.TextStim(win, text="A", pos=(-BOX_OFFSET_X, 0), height=80, bold=True)

card_right = visual.Rect(win, width=BOX_SIZE, height=BOX_SIZE, pos=(BOX_OFFSET_X, 0), lineWidth=4)
label_right = visual.TextStim(win, text="B", pos=(BOX_OFFSET_X, 0), height=80, bold=True)

hint = visual.TextStim(
    win, 
    text="Fixa o teu olhar na Caixa A. Vais contar os flashes que vires do A.", 
    pos=(0, 210), 
    height=24, 
    color=(0.7, 0.7, 0.7)
)

# ---------------------------------------------------------
# GPU Warm-up (Compiles shaders before trial execution)
# ---------------------------------------------------------
print("[INFO] Warming up GPU shaders...")
hint.draw()
card_left.draw()
card_right.draw()
label_left.draw()
label_right.draw()
win.flip()
win.flip()

draw_durations_ms = []


print(f"[INFO] Running benchmark with {N_TRIALS} realistic 2-Box trials...")

win.frameIntervals = []
for trial in range(1, N_TRIALS + 1):
    if "escape" in event.getKeys():
        print("[WARN] Aborted by user.")
        break

    # Alternate target flash for testing
    is_target = (trial % 2 == 1)
    if is_target:
        card_left.fillColor, card_left.lineColor = FLASH_FILL, FLASH_LINE
        label_left.color = FLASH_TEXT
        card_right.fillColor, card_right.lineColor = IDLE_FILL, IDLE_LINE
        label_right.color = IDLE_TEXT
    else:
        card_left.fillColor, card_left.lineColor = IDLE_FILL, IDLE_LINE
        label_left.color = IDLE_TEXT
        card_right.fillColor, card_right.lineColor = FLASH_FILL, FLASH_LINE
        label_right.color = FLASH_TEXT

    # 1. FLASH ON
    for f in range(flash_frames):
        t0 = time.perf_counter()
        hint.draw()
        card_left.draw()
        card_right.draw()
        label_left.draw()
        label_right.draw()
        t1 = time.perf_counter()

        if f == 0:
            draw_durations_ms.append((t1 - t0) * 1000.0)

        win.flip()

    # 2. FLASH OFF (ISI)
    card_left.fillColor, card_left.lineColor = IDLE_FILL, IDLE_LINE
    label_left.color = IDLE_TEXT
    card_right.fillColor, card_right.lineColor = IDLE_FILL, IDLE_LINE
    label_right.color = IDLE_TEXT

    for _ in range(isi_frames):
        hint.draw()
        card_left.draw()
        card_right.draw()
        label_left.draw()
        label_right.draw()
        win.flip()

# ---------------------------------------------------------
# Metrics & Plotting
# ---------------------------------------------------------
raw_intervals_ms = np.array(win.frameIntervals) * 1000.0
n_dropped = win.nDroppedFrames
draw_durations_ms = np.array(draw_durations_ms)

win.close()

mean_interval = np.mean(raw_intervals_ms)
std_interval = np.std(raw_intervals_ms)
mean_draw = np.mean(draw_durations_ms)
max_draw = np.max(draw_durations_ms)

print("\n" + "=" * 55)
print("     2-BOX PARADIGM DISPLAY BENCHMARK RESULTS")
print("=" * 55)
print(f"Total Frames Analyzed   : {len(raw_intervals_ms)}")
print(f"Refresh Rate            : {refresh_rate:.2f} Hz (Period: {expected_frame_ms:.2f} ms)")
print(f"Mean Frame Interval     : {mean_interval:.3f} ms (± {std_interval:.3f} ms)")
print(f"Dropped Frames          : {n_dropped} ({ (n_dropped / max(1, len(raw_intervals_ms))) * 100:.2f} %)")
print(f"Full Scene Draw Time    : Mean = {mean_draw:.3f} ms | Max = {max_draw:.3f} ms")
print(f"Safety Margin to V-Sync : {(expected_frame_ms - max_draw):.2f} ms available")
print("=" * 55)

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=120)

ax1.plot(raw_intervals_ms, color="#1f77b4", lw=0.8, alpha=0.8, label="Frame Interval")
ax1.axhline(expected_frame_ms, color="red", linestyle="--", lw=1.2, label=f"Expected ({expected_frame_ms:.1f} ms)")
ax1.axhline(expected_frame_ms + 4.0, color="orange", linestyle=":", lw=1.0, label="Drop Threshold (+4 ms)")
ax1.set_title("V-Sync Stability (2-Box Real Paradigm)", fontsize=11, fontweight="bold")
ax1.set_xlabel("Frame Number")
ax1.set_ylabel("Duration (ms)")
ax1.set_ylim([max(0, expected_frame_ms - 10), expected_frame_ms + 15])
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.legend(loc="upper right", fontsize=8)

ax2.hist(draw_durations_ms, bins=15, color="#2ca02c", edgecolor="black", alpha=0.7)
ax2.axvline(mean_draw, color="darkgreen", linestyle="--", lw=1.5, label=f"Mean: {mean_draw:.3f} ms")
ax2.axvline(expected_frame_ms, color="red", linestyle="--", lw=1.2, label=f"Deadline: {expected_frame_ms:.1f} ms")
ax2.set_title("Full Scene Draw Duration (5 Elements)", fontsize=11, fontweight="bold")
ax2.set_xlabel("Draw Duration (ms)")
ax2.set_ylabel("Occurrences")
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.legend(loc="upper right", fontsize=8)

plt.tight_layout()
output_fig = "benchmark_display_timing.png"
plt.savefig(output_fig)
plt.close()
print(f"[INFO] Plot saved to: {output_fig}")
