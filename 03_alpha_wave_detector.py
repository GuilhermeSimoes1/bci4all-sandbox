import gpype as gp

ELECTRODES = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "POz", "PO8"]

if __name__ == "__main__":
    app = gp.MainApp()
    p = gp.Pipeline()

    # Sources
    amp = gp.BCICore()

    # Surgical filter: ONLY the Alpha band (8 to 13 Hz) + Notch 50 Hz
    alpha_band = gp.Bandpass(f_lo=8, f_hi=13)
    notch50 = gp.Bandstop(f_lo=48, f_hi=52)
    labeler = gp.ChannelLabeler(labels=ELECTRODES)

    # select the occipital channels to visualize the alpha waves
    selector = gp.ChannelSelector(labels=["PO7", "POz", "PO8"])

    # Visualization with high sensitivity (amplitude_limit=15, because my alpha waves are small but you can change it for your case)
    scope = gp.TimeSeriesScope(
        name="Alpha Rhythm Detector (8-13 Hz) - Occipital",
        amplitude_limit=15,  # Small scale to highlight weak waves
        time_window=6,
    )

    # Connecting the nodes
    p.connect(amp, alpha_band)
    p.connect(alpha_band, notch50)
    p.connect(notch50, labeler)
    p.connect(labeler, selector)
    p.connect(selector, scope)

    app.add_widget(scope)

    # Pipeline lifecycle
    p.start()
    app.run()
    p.stop()
    p.close()
