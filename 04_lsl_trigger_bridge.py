import threading
import gpype as gp
from pylsl import StreamInlet, resolve_byprop

ELECTRODES = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "POz", "PO8"]

# Function to receive the data from LSL and create a marker
def listen_lsl(marker_node):
    """Listens to LSL and injects it into gp.Marker."""
    inlet = StreamInlet(resolve_byprop("name", "BCI_Triggers")[0])
    while True:
        sample, _ = inlet.pull_sample()
        if sample:
            marker_node.emit(int(sample[0]))

if __name__ == "__main__":
    app = gp.MainApp()
    p = gp.Pipeline()

    # Sources
    amp = gp.BCICore()
    marker = gp.Marker()

    # Filters
    bandpass = gp.Bandpass(f_lo=1, f_hi=30)
    notch50 = gp.Bandstop(f_lo=48, f_hi=52)
    labeler = gp.ChannelLabeler(labels=ELECTRODES)
    router = gp.Router(input_channels=[gp.Router.ALL, gp.Router.ALL])

    # Markers that are used to show the stimulus on the scope
    mk = gp.TimeSeriesScope.Markers
    markers = [
        mk(color="g", label="Target (1)", channel=8, value=1),
        mk(color="r", label="Non-Target (2)", channel=8, value=2),
    ]

    # Visualization 
    scope = gp.TimeSeriesScope(
        name="BCI Core-8 + LSL Triggers",
        amplitude_limit=50,
        time_window=6,
        markers=markers,
        hidden_channels=[8],
    )

    # Connecting the nodes
    p.connect(amp, bandpass)
    p.connect(bandpass, notch50)
    p.connect(notch50, labeler)
    p.connect(labeler, router["in1"])
    p.connect(marker, router["in2"])
    p.connect(router, scope)

    # Adding the scope to the app
    app.add_widget(scope)

    # Starting the LSL listener and the pipeline
    threading.Thread(target=listen_lsl, args=(marker,), daemon=True).start()

    p.start()
    app.run()
    p.stop()
    p.close()
