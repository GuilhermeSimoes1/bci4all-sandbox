"""Mock Stimulus Generator. (Simulating PsychoPy flashes)

Transmits numeric markers via LSL on the local network every 1 second.
"""

import time
from pylsl import StreamInfo, StreamOutlet

STREAM_NAME = "BCI_Triggers"

if __name__ == "__main__":
    print(f"[LSL] Creating a channel for markers: '{STREAM_NAME}'...")

    # Setting up the LSL channel (1 channel of integers for markers)
    # nominal_srate=0.0 means irregular events (only happen when there are flashes)
    info = StreamInfo(
        name=STREAM_NAME,
        type="Markers",
        channel_count=1,
        nominal_srate=0.0,
        channel_format="int32",
    )
    outlet = StreamOutlet(info)

    print("[LSL] Transmitter ready! Sending markers (Ctrl+C to stop)...")

    # Simulating flashes: alternates between 1 (Target) and 2 (Non-Target)
    marker_id = 1
    try:
        while True:
            time.sleep(1.0)  # Waiting 1 second between flashes
            outlet.push_sample([marker_id])
            print(f"[PsychoPy Fake] Firing marker: {marker_id}")

            # Alternating between 1 and 2
            marker_id = 2 if marker_id == 1 else 1
    except KeyboardInterrupt:
        print("\n[LSL] Transmitter off.")
