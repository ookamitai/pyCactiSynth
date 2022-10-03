# Project Name: pyCactiSynth
# Project Desc.: A fully UTAU-compatible editor/synthesizer
# File name: ui.py
# Author: ookamitai, null
# Date: Oct. 3 2022

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget


class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("yay new window!")
        layout.addWidget(self.label)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        self.button = QPushButton("BEGIN SYNTH????????????")
        self.button.clicked.connect(self.show_new_window)
        self.setCentralWidget(self.button)

    def show_new_window(self):
        if self.w is None:
            self.w = AnotherWindow()
        self.w.show()


# Again, some driver code here
if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()
