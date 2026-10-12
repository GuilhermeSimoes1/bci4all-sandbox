import gpype as gp

ELECTRODES = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "POz", "PO8"]


if __name__ == "__main__":
    app = gp.MainApp()
    p = gp.Pipeline()

    # Source: Unicorn BCI Core-8
    amp = gp.BCICore()

    # Essential cleaning of the signal
    bandpass = gp.Bandpass(f_lo=1, f_hi=30)     # Filter to only pass the frequencies between 1 and 30 hz
    notch50 = gp.Bandstop(f_lo=48, f_hi=52)     # Filter to remove 50 hz noise (Portugal use 50 hz on electrical grid)

    # Change channel names to more understandable names - Electrodes locations according to 10-20 International System
    labeler = gp.ChannelLabeler(labels=ELECTRODES)

    # Scope that shows the signal in real time
    scope = gp.TimeSeriesScope(name="BCI Core-8 - Clean EEG", amplitude_limit=50, time_window=6)

    # Pipeline
    p.connect(amp, bandpass)
    p.connect(bandpass, notch50)
    p.connect(notch50, labeler)
    p.connect(labeler, scope)

    app.add_widget(scope)

    # Life cycle
    p.start()
    app.run()
    p.stop()
    p.close()
