import sys
import random
from pylsl import StreamInfo, StreamOutlet
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

STREAM_NAME = "BCI_Triggers"
FLASH_DURATION_MS = 200   
ISI_MS = 1600             

# This class generates the visual stimuli (target and non-target flashes)
class OddballWindow(QWidget):
    def __init__(self, outlet):
        super().__init__()
        self.outlet = outlet
        self.setWindowTitle("Visual Oddball Paradigm - Count the TARGETS!")
        self.resize(500, 500)
        self.setStyleSheet("background-color: #121212;")

        layout = QVBoxLayout()
        self.box = QLabel("+")
        self.box.setAlignment(Qt.AlignCenter)
        self.box.setFont(QFont("Arial", 42, QFont.Bold))
        self.box.setStyleSheet(
            "background-color: #1a1a1a; color: #444444; border-radius: 20px;"
        )
        layout.addWidget(self.box)
        self.setLayout(layout)

        # Timers
        self.isi_timer = QTimer(self)
        self.isi_timer.timeout.connect(self.trigger_flash)
        self.isi_timer.start(ISI_MS)

        self.reset_timer = QTimer(self)
        self.reset_timer.setSingleShot(True)
        self.reset_timer.timeout.connect(self.reset_box)

    # Generates the visual stimuli (target and non-target flashes)
    def trigger_flash(self):
        # 20% probabilidade de Target (1), 80% Non-Target (2)
        is_target = random.random() < 0.20
        marker_id = 1 if is_target else 2

        self.outlet.push_sample([marker_id])

        if is_target:
            # TARGET: Super brilhante, saliente e inconfundível!
            self.box.setText("+")
            self.box.setStyleSheet(
                "background-color: #FFD600; color: #000000; border-radius: 20px;"
            )
            print("[STIMULUS] >>> ★ TARGET (1) ★ <<<")
        else:
            # NON-TARGET: Cinzento discreto e aborrecido (o cérebro ignora facilmente)
            self.box.setText("+")
            self.box.setStyleSheet(
                "background-color: #2a2a2a; color: #666666; border-radius: 20px;"
            )
            print("[STIMULUS] Non-Target (2)")

        self.reset_timer.start(FLASH_DURATION_MS)

    # Resets the box to its original state
    def reset_box(self):
        self.box.setText("+")
        self.box.setStyleSheet(
            "background-color: #1a1a1a; color: #444444; border-radius: 20px;"
        )


if __name__ == "__main__":
    print(f"[LSL] Creating marker stream: '{STREAM_NAME}'...")
    info = StreamInfo(
        name=STREAM_NAME,
        type="Markers",
        channel_count=1,
        nominal_srate=0.0,
        channel_format="int32",
    )
    outlet = StreamOutlet(info)

    app = QApplication(sys.argv)
    window = OddballWindow(outlet)
    window.show()
    sys.exit(app.exec())
