import random
import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet
from psychopy import visual, core, event

# Experiment timing parameters
FLASH_MS = 125.0
ISI_MS = 800.0
N_TRIALS = 100
TARGET_PROBABILITY = 0.20

# Setup LSL Marker Outlet
info = StreamInfo("P300_Markers", "Markers", 1, 0, "int32", "psychopy_stim_07")
outlet = StreamOutlet(info)

# Setup PsychoPy Window
win = visual.Window(size=(800, 600), color=(-1, -1, -1), units="pix", fullscr=False)

# Activate hardware frame interval recording (tracks GPU V-Sync stability)
win.recordFrameIntervals = True

refresh_rate = win.getActualFrameRate() or 60.0
flash_frames = max(1, int(round((FLASH_MS / 1000.0) * refresh_rate)))
isi_frames = max(1, int(round((ISI_MS / 1000.0) * refresh_rate)))

# Visual stimuli
card = visual.Rect(win, width=180, height=180, lineWidth=4)
label = visual.TextStim(win, text="+", height=80)

# Arrays to record real hardware timestamps
flash_onset_times = []

def record_onset(marker_val):
    """Callback fired by PsychoPy on the exact GPU flip raster sweep."""
    flash_onset_times.append(time.perf_counter())
    outlet.push_sample([marker_val])

print(f"\n[BENCHMARK] Running {N_TRIALS} trials with GPU V-Sync profiling...")

# Main Presentation Loop
for trial in range(1, N_TRIALS + 1):
    is_target = random.random() < TARGET_PROBABILITY
    marker = 1 if is_target else 2
    

    card.fillColor = (1.0, 0.84, 0.0)      
    card.lineColor = (1.0, 1.0, 1.0)        
    label.color = (-1.0, -1.0, -1.0)

    label.text = "G" if is_target else "Z"

    # V-SYNC ONSET: Trigger fires on the exact monitor refresh
    win.callOnFlip(record_onset, marker)
    
    for f in range(flash_frames):
        card.draw()
        label.draw()
        win.flip()
    
    card.fillColor = (-0.7, -0.7, -0.7)      
    card.lineColor = (-0.4, -0.4, -0.4)      
    label.color = (-0.2, -0.2, -0.2)         
    label.text = "+"

    for f in range(isi_frames):
        card.draw()
        label.draw()
        win.flip()
        
    if "escape" in event.getKeys():
        break

win.close()

# Statistical Analysis of Real Timing Performance
# Calculate flash-to-flash intervals (Period = Flash + ISI)
intervals = np.diff(flash_onset_times) * 1000.0
target_period = (flash_frames + isi_frames) * (1000.0 / refresh_rate)

# Calculate frame intervals recorded by GPU
frame_intervals = np.array(win.frameIntervals) * 1000.0
expected_frame_ms = 1000.0 / refresh_rate
dropped_frames = np.sum(frame_intervals > (expected_frame_ms * 1.5))

print("\n" + "=" * 55)
print("             PSYCHOPY TIMING BENCHMARK REPORT")
print("=" * 55)
print(f"Monitor Refresh Rate:       {refresh_rate:.2f} Hz ({expected_frame_ms:.2f} ms / frame)")
print(f"Target Period (Flash+ISI):  {target_period:.2f} ms")
print(f"Measured Mean Period:       {np.mean(intervals):.2f} ms")
print(f"Timing Jitter (Std Dev):    ±{np.std(intervals):.3f} ms")
print(f"Total Frames Rendered:      {len(frame_intervals)}")
print(f"Dropped Frames:             {dropped_frames} ({dropped_frames / len(frame_intervals) * 100:.2f}%)")
print("=" * 55 + "\n")

core.quit()
