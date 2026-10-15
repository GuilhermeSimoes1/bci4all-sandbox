import threading
import gpype as gp
from pylsl import StreamInlet, resolve_byprop

ELECTRODES = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "POz", "PO8"]

# Function that listens to LSL triggers that are sent by the stimulus generator 
# and emits them into gp.Marker.
def listen_lsl(marker_node, stream_name="P300_Markers"):
    print(f"[LSL Bridge] Searching for stream '{stream_name}'...")
    streams = resolve_byprop("name", stream_name, timeout=10)
    if not streams:
        print(f"[LSL Bridge] Stream '{stream_name}' not found.")
        return

    inlet = StreamInlet(streams[0])
    print(f"[LSL Bridge] Connected to '{stream_name}'. Listening for triggers...")
    while True:
        sample, _ = inlet.pull_sample()
        if sample:
            val = int(sample[0])
            marker_node.emit(val)


if __name__ == "__main__":
    app = gp.MainApp()
    p = gp.Pipeline()

    # Sources: Unicorn EEG + LSL Marker Inlet
    amp = gp.BCICore()
    marker = gp.Marker()

    # Filtering (1-30 Hz bandpass + 50 Hz notch)
    bandpass = gp.Bandpass(f_lo=1, f_hi=30)
    notch50 = gp.Bandstop(f_lo=48, f_hi=52)
    labeler = gp.ChannelLabeler(labels=ELECTRODES)

    # Focus on classic P300 midline channels (Cz, Pz)
    selector = gp.ChannelSelector(labels=["Cz", "Pz"])

    # Using trigger to get the epoch that p300 is supposed to happen (target)
    trig_target = gp.Trigger(time_pre=0.1, time_post=0.8, target=[1])
    base_target = gp.Baseline()
    scope_target = gp.TriggerScope(
        name="Target (1) - P300 ERP (Cz & Pz)",
        amplitude_limit=10,
    )

    # Using trigger to get the epoch that p300 is not supposed to happen (non-target)
    trig_nontarget = gp.Trigger(time_pre=0.1, time_post=0.8, target=[2])
    base_nontarget = gp.Baseline()
    scope_nontarget = gp.TriggerScope(
        name="Non-Target (2) - Baseline Noise (Cz & Pz)",
        amplitude_limit=10,
    )

    # connecting the nodes (filtering and labeling)
    p.connect(amp, bandpass)
    p.connect(bandpass, notch50)
    p.connect(notch50, labeler)
    p.connect(labeler, selector)

    # connecting the nodes (target branch)
    p.connect(selector, trig_target["in"])
    p.connect(marker, trig_target["trigger"])
    p.connect(trig_target, base_target)
    p.connect(base_target, scope_target)

    # connecting the nodes (non-target branch)
    p.connect(selector, trig_nontarget["in"])
    p.connect(marker, trig_nontarget["trigger"])
    p.connect(trig_nontarget, base_nontarget)
    p.connect(base_nontarget, scope_nontarget)

    # Adding the scopes to the app
    app.add_widget(scope_target)
    app.add_widget(scope_nontarget)

    # Starting the LSL listener thread
    threading.Thread(target=listen_lsl, args=(marker,), daemon=True).start()

    # Pipeline lifecycle
    p.start()
    app.run()
    p.stop()
    p.close()
