import random
import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet
from psychopy import visual, core, event

# Parameters of temporization (ms)
FLASH_MS = 125.0
ISI_MS = 800.0
N_TRIALS = 100
TARGET_PROBABILITY = 0.20  # 20% flashes no Alvo (A), 80% no Não-Alvo (B)

# LSL stream configuration (sender)
info = StreamInfo("P300_Markers", "Markers", 1, 0, "int32", "psychopy_stim_07")
outlet = StreamOutlet(info)

# PsychoPy window
win = visual.Window(size=(900, 600), color=(-1, -1, -1), units="pix", fullscr=False)
win.recordFrameIntervals = True

refresh_rate = win.getActualFrameRate() or 60.0
flash_frames = max(1, int(round((FLASH_MS / 1000.0) * refresh_rate)))
isi_frames = max(1, int(round((ISI_MS / 1000.0) * refresh_rate)))

# States colors (Idle vs Flash)
IDLE_FILL = (-0.75, -0.75, -0.75)
IDLE_LINE = (-0.4, -0.4, -0.4)
IDLE_TEXT = (-0.1, -0.1, -0.1)

FLASH_FILL = (1.0, 0.84, 0.0)    # Gold
FLASH_LINE = (1.0, 1.0, 1.0)    # White
FLASH_TEXT = (-1.0, -1.0, -1.0)  # Black

# Visual elements: Box A (Left / Target) and Box B (Right / Non-Target)
BOX_OFFSET_X = 220
BOX_SIZE = 180

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

flash_onset_times = []

def record_onset(marker_val):
    """Triggered by the exact sweep of the monitor's photon gun (V-Sync)."""
    flash_onset_times.append(time.perf_counter())
    outlet.push_sample([marker_val])

print(f"\n[BENCHMARK] Starting {N_TRIALS} trials in the 2-Box Paradigm...")
print("[INSTRUÇÃO] Mantém os olhos fixos na Caixa A (Esquerda).")

# Main loop
for trial in range(1, N_TRIALS + 1):
    is_target = random.random() < TARGET_PROBABILITY
    marker = 1 if is_target else 2

    # Setup Flash and Idle colors
    if is_target:
        # Box A flashes (Target)
        card_left.fillColor, card_left.lineColor = FLASH_FILL, FLASH_LINE
        label_left.color = FLASH_TEXT
        card_right.fillColor, card_right.lineColor = IDLE_FILL, IDLE_LINE
        label_right.color = IDLE_TEXT
    else:
        # Box B flashes (Non-Target)
        card_left.fillColor, card_left.lineColor = IDLE_FILL, IDLE_LINE
        label_left.color = IDLE_TEXT
        card_right.fillColor, card_right.lineColor = FLASH_FILL, FLASH_LINE
        label_right.color = FLASH_TEXT

    # V-SYNC LOCK: Trigger activate on monitor flip
    win.callOnFlip(record_onset, marker)

    # Flash duration
    for _ in range(flash_frames):
        # draw the scenario that stay behind of the actual card (stay on vram)
        hint.draw()
        card_left.draw()
        card_right.draw()
        label_left.draw()
        label_right.draw()
        # Synchronizes with monitor refresh (V-Sync) 
        # so execution resumes as photons hit the screen
        win.flip()

    # Return to idle state (both boxes turn off during ISI)
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

    if "escape" in event.getKeys():
        break

win.close()

# Analysis
intervals = np.diff(flash_onset_times) * 1000.0
target_period = (flash_frames + isi_frames) * (1000.0 / refresh_rate)
frame_intervals = np.array(win.frameIntervals) * 1000.0
expected_frame_ms = 1000.0 / refresh_rate
dropped_frames = np.sum(frame_intervals > (expected_frame_ms * 1.5))

print("\n" + "=" * 55)
print("       PSYCHOPY 2-BOX TIMING BENCHMARK REPORT")
print("=" * 55)
print(f"Monitor Refresh Rate:       {refresh_rate:.2f} Hz ({expected_frame_ms:.2f} ms / frame)")
print(f"Target Period (Flash+ISI):  {target_period:.2f} ms")
print(f"Measured Mean Period:       {np.mean(intervals):.2f} ms")
print(f"Timing Jitter (Std Dev):    ±{np.std(intervals):.3f} ms")
print(f"Total Frames Rendered:      {len(frame_intervals)}")
print(f"Dropped Frames:             {dropped_frames} ({dropped_frames / len(frame_intervals) * 100:.2f}%)")
print("=" * 55 + "\n")

core.quit()
