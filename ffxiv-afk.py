import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QCheckBox, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from pynput import keyboard, mouse
import threading
import pygetwindow as gw
import pyautogui

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_input_time = time.time()
        self.afk_active = False
        self.initUI()

        # Start the input monitors in separate threads
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        mouse_listener = mouse.Listener(on_click=self.on_click)
        keyboard_listener.start()
        mouse_listener.start()

        self.update_label()

    def initUI(self):
        self.setWindowTitle('FFXIV Anti-AFK')
        self.setGeometry(300, 300, 400, 120)
        self.setStyleSheet("background-color: #333; color: #DDD; font-size: 16px;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.timer_label = QLabel('Time since last input: 00:00:00', self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.afk_label = QLabel('AFK mode: OFF', self)
        self.afk_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.timer_label)
        self.layout.addWidget(self.afk_label)

        self.always_on_top_checkbox = QCheckBox("Keep window on top", self)
        self.always_on_top_checkbox.stateChanged.connect(self.toggle_always_on_top)
        self.layout.addWidget(self.always_on_top_checkbox)

    def toggle_always_on_top(self, state):
        if state == Qt.Checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def on_press(self, key):
        self.last_input_time = time.time()
        self.afk_active = False

    def on_click(self, x, y, button, pressed):
        self.last_input_time = time.time()
        self.afk_active = False

    def update_label(self):
        elapsed = time.time() - self.last_input_time
        self.timer_label.setText(f"Time since last input: {int(elapsed)} seconds")
        if elapsed > 120:
            self.afk_label.setText("AFK mode: ON")
            self.afk_label.setStyleSheet("color: #FF6347;")
            self.afk_active = True
            self.afk_mode()
        else:
            self.afk_label.setText("AFK mode: OFF")
            self.afk_label.setStyleSheet("color: #90EE90;")
        
        QTimer.singleShot(1000, self.update_label)

    def afk_mode(self):
        if self.afk_active:
            threading.Timer(120, self.press_ctrl).start() 

    def press_ctrl(self):
        try:
            window = gw.getWindowsWithTitle('ffxiv_dx11.exe')[0]
            window.activate()
            time.sleep(2)
            pyautogui.press('ctrl')
        except IndexError:
            QMessageBox.critical(self, "Error", "Can't find 'ffxiv_dx11.exe'. Is it running?")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
