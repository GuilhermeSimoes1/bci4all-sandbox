import gpype as gp

ELECTRODES = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "POz", "PO8"]

if __name__ == "__main__":
    app = gp.MainApp()
    p = gp.Pipeline()

    # Sources definition
    amp = gp.BCICore()
    keyboard = gp.Keyboard()

    # Recording branch, creating a router to synchronize the signals with the keyboard inputs and a writer to save the data
    router_raw = gp.Router(input_channels=[gp.Router.ALL, gp.Router.ALL])
    writer = gp.CsvWriter(file_name="session_01.csv")

    # Applying filters to the signal and labeling the channels
    bandpass = gp.Bandpass(f_lo=1, f_hi=30)
    notch50 = gp.Bandstop(f_lo=48, f_hi=52)
    labeler = gp.ChannelLabeler(labels=ELECTRODES)

    # Visualization branch, creating a router to synchronize the signals with the keyboard inputs and a scope to show the data
    router_scope = gp.Router(input_channels=[gp.Router.ALL, gp.Router.ALL])
    mk = gp.TimeSeriesScope.Markers
    markers = [
        mk(color="r", label="Espaço (Flash)", channel=8, value=32),
        mk(color="g", label="Tecla M (Alvo)", channel=8, value=77),
    ]
    scope = gp.TimeSeriesScope(
        name="BCI Core-8 - Monitorização com Triggers",
        amplitude_limit=50,
        time_window=6,
        markers=markers,
        hidden_channels=[8],
    )

    # Connecting the nodes, signal without filters and writing on a csv file
    p.connect(amp, router_raw["in1"])
    p.connect(keyboard, router_raw["in2"])
    p.connect(router_raw, writer)

    # Connecting the nodes, applying filters to the signal and labeling the channels
    p.connect(amp, bandpass)
    p.connect(bandpass, notch50)
    p.connect(notch50, labeler)
    # Connecting the nodes, signal with filters and labeling the channels and visualizing the data
    p.connect(labeler, router_scope["in1"])
    p.connect(keyboard, router_scope["in2"])
    p.connect(router_scope, scope)

    # Scope to visualize the data
    app.add_widget(scope)

    # Pipeline lifecycle
    p.start()
    app.run()
    p.stop()
    p.close()
