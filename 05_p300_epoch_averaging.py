import threading
import numpy as np
import gpype as gp
from pylsl import StreamInlet, resolve_byprop
from plot_utils import plot_erp_stability_panels, plot_sigma_over_time

# Electrodes
ELECTRODES = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "POz", "PO8"]


# Custom node to store epochs in RAM
# Rationale: gpype only shows graphs on screen. We need this node to save 
# the numeric data of each trial in memory so we can analyze it and train ML models.
class EpochCollector(gp.INode):
    """Node for epoch collection and P300 analysis."""
    def __init__(self, name="TargetCollector"):
        super().__init__(
            name=name,
            input_ports=[
                # ASYNC: Trials only arrive when there is a flash (irregular events),
                # unlike the continuous 250 Hz EEG signal.
                gp.IPort.Configuration(name="in", timing=gp.Constants.Timing.ASYNC)
            ],
            output_ports=[],
        )
        self.epochs = []

    def step(self, data):
        block = data.get("in")
        if block is not None and len(block) > 0:
            # Save a copy of the trial (225 samples) in the list
            self.epochs.append(np.asarray(block).copy())
        return {}

    def compute(self, data):
        return self.step(data)


# Thread to receive markers from PsychoPy via LSL
# Rationale: PsychoPy and gpype run in separate processes so visual flashes 
# never freeze or lag. This thread listens to the network and injects markers into gpype.
def listen_lsl(marker_node, stream_name="P300_Markers"):
    """LSL Stream Inlet to receive markers from PsychoPy."""
    print(f"[LSL Bridge] À procura da stream '{stream_name}'...")
    while True:
        streams = resolve_byprop("name", stream_name, timeout=1.0)
        if streams:
            break

    inlet = StreamInlet(streams[0])
    print(f"[LSL Bridge] CONECTADO a '{stream_name}'! À escuta de estímulos...")

    t_count = 0
    while True:
        try:
            sample, _ = inlet.pull_sample(timeout=1.0)
            if sample:
                val = int(sample[0])
                if val == 1:
                    t_count += 1
                    print(f"[LSL Bridge] -> Target (1) #{t_count} recebido!")
                marker_node.emit(val)
        except Exception:
            break


# Artifact rejection and statistical calculation
# Rationale: Eye blinks create huge spikes (>100 uV). Since the real P300 is small (~10 uV), 
# any trial with voltage > 70 uV is discarded to keep the data clean.
def process_epochs(epoch_list, label_name):
    """Filters artifacts (>70 uV) and calculates mean and standard deviation."""
    total = len(epoch_list)
    if total < 2:
        return None, None, None, 0
    
    # Discard trials with amplitude > 70 uV (blinks and muscle movements)
    clean = [e for e in epoch_list if np.max(np.abs(e)) < 70.0]
    used = clean if len(clean) >= 2 else epoch_list

    # Convert list to 2D matrix: (Number of Trials x 225 Samples)
    arr = np.squeeze(np.array(used))

    # Calculate Mean (ERP wave) and Standard Deviation (sigma) across trials
    m = np.mean(arr, axis=0)
    s = np.std(arr, axis=0, ddof=1)
    print(f"[{label_name}] Total: {total} | Clean: {len(clean)} | Rejected: {total - len(clean)}")
    return arr, m, s, len(arr)


if __name__ == "__main__":
    app = gp.MainApp()
    p = gp.Pipeline()

    # Sources
    amp = gp.BCICore()
    marker = gp.Marker()

    # Raw continuous recording branch (8 channels EEG + 1 channel Marker)
    router_raw = gp.Router(input_channels=[gp.Router.ALL, gp.Router.ALL])
    writer = gp.CsvWriter(file_name="session_p300_raw.csv")

    # Real-time filtering and visualization branch
    bandpass = gp.Bandpass(f_lo=0.5, f_hi=10.0)
    notch50 = gp.Bandstop(f_lo=48.0, f_hi=52.0)
    labeler = gp.ChannelLabeler(labels=ELECTRODES)
    selector = gp.ChannelSelector(labels=["Pz"])

    # Target Branch (Target = 1)
    trig_target = gp.Trigger(time_pre=0.1, time_post=0.8, target=[1])
    base_target = gp.Baseline()
    scope_target = gp.TriggerScope(name="Target (1) - Pz ERP", amplitude_limit=10)
    collector_target = EpochCollector(name="TargetCollector")

    # Non-Target Branch (Non-Target = 2)
    trig_nontarget = gp.Trigger(time_pre=0.1, time_post=0.8, target=[2])
    base_nontarget = gp.Baseline()
    scope_nontarget = gp.TriggerScope(name="Non-Target (2) - Pz Ruído", amplitude_limit=10)
    collector_nontarget = EpochCollector(name="NonTargetCollector")

    # Pipeline Connections - RAW Recording
    p.connect(amp, router_raw["in1"])
    p.connect(marker, router_raw["in2"])
    p.connect(router_raw, writer)

    # Pipeline Connections - Filtering & Pz Scopes
    p.connect(amp, bandpass)
    p.connect(bandpass, notch50)
    p.connect(notch50, labeler)
    p.connect(labeler, selector)

    # Target Branch
    p.connect(selector, trig_target["in"])
    p.connect(marker, trig_target["trigger"])
    p.connect(trig_target, base_target)
    p.connect(base_target, scope_target)
    p.connect(base_target, collector_target)

    # Non-Target Branch
    p.connect(selector, trig_nontarget["in"])
    p.connect(marker, trig_nontarget["trigger"])
    p.connect(trig_nontarget, base_nontarget)
    p.connect(base_nontarget, scope_nontarget)
    p.connect(base_nontarget, collector_nontarget)

    app.add_widget(scope_target)
    app.add_widget(scope_nontarget)

    # LSL Thread
    threading.Thread(target=listen_lsl, args=(marker,), daemon=True).start()

    print("\n[PIPELINE] Gravação iniciada (RAW CSV + Análise Pz).")
    print("[PIPELINE] Corre o 07_psychopy_single_stimulus.py. No fim, fecha a janela.")
    p.start()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[PIPELINE] Ctrl+C detetado!") 
    finally:
        try:
            p.stop()
            p.close()
        except Exception:
            pass

    # Statistical Analysis & Artifact Rejection
    arr_tgt, m_tgt, s_tgt, n_tgt = process_epochs(collector_target.epochs, "TARGET")
    arr_nontgt, m_nontgt, s_nontgt, n_nontgt = process_epochs(collector_nontarget.epochs, "NON-TARGET")

    if m_tgt is not None and m_nontgt is not None:
        n_samples = arr_tgt.shape[1]
        time_axis = np.linspace(-100.0, 800.0, n_samples)

        # save epochs in .npz (for the classifier)
        np.savez(
            "session_p300_epochs_Pz.npz",
            target_epochs=arr_tgt,
            nontarget_epochs=arr_nontgt,
            time_axis=time_axis,
            s_tgt=s_tgt,
            s_nontgt=s_nontgt,
            m_tgt=m_tgt,
            m_nontgt=m_nontgt,
            channel="Pz",
            fs=250,
        )
        print("[DATASET] Épocas guardadas com sucesso em 'session_p300_epochs_Pz.npz'!")

        # plot p300 stability (mean +/- std over time)
        plot_erp_stability_panels(
            time_axis, m_tgt, s_tgt, n_tgt, m_nontgt, s_nontgt, n_nontgt, 
            channel_name="Pz", save_path="p300_Pz_stability.png"
        )

        # plot sigma over time
        plot_sigma_over_time(
            time_axis, s_tgt, s_nontgt, 
            channel_name="Pz", save_path="p300_sigma_over_time.png"
        )
    else:
        print("[WARNING] Épocas insuficientes para cálculo estatístico.")
