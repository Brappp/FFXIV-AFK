import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QCheckBox, QMessageBox, QHBoxLayout
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
        self.error_shown = False
        self.simulating_input = False
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

        self.bottom_layout = QHBoxLayout()

        self.always_on_top_checkbox = QCheckBox("Keep window on top", self)
        self.always_on_top_checkbox.stateChanged.connect(self.toggle_always_on_top)
        self.bottom_layout.addWidget(self.always_on_top_checkbox)
        
        self.bottom_layout.addStretch(1)

        self.github_label = QLabel('<a href="https://github.com/Brappp/FFXIV-AFK" style="color: #1E90FF; text-decoration: none;">GitHub</a>', self)
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setStyleSheet("font-size: 18px; text-align: right; font-weight: bold;")
        self.bottom_layout.addWidget(self.github_label)

        self.layout.addLayout(self.bottom_layout)

    def toggle_always_on_top(self, state):
        if state == Qt.Checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def on_press(self, key):
        if not self.simulating_input:
            self.last_input_time = time.time()
            self.afk_active = False
            self.error_shown = False

    def on_click(self, x, y, button, pressed):
        if not self.simulating_input:
            self.last_input_time = time.time()
            self.afk_active = False
            self.error_shown = False

    def update_label(self):
        elapsed = time.time() - self.last_input_time
        self.timer_label.setText(f"Time since last input: {int(elapsed)} seconds")
        if elapsed > 120:
            if not self.afk_active:
                self.afk_active = True
                self.afk_mode_initial()
            self.afk_label.setText("AFK mode: ON")
            self.afk_label.setStyleSheet("color: #FF6347;")
        else:
            self.afk_label.setText("AFK mode: OFF")
            self.afk_label.setStyleSheet("color: #90EE90;")
            self.afk_active = False
        
        QTimer.singleShot(1000, self.update_label)

    def afk_mode_initial(self):
        self.press_ctrl()
        self.start_afk_timer()

    def start_afk_timer(self):
        if self.afk_active:
            threading.Timer(120, self.press_ctrl).start()

    def press_ctrl(self):
        try:
            window = [win for win in gw.getWindowsWithTitle('FINAL FANTASY XIV') if 'FINAL FANTASY XIV' in win.title][0]
            window.minimize()
            time.sleep(1)
            window.restore()
            window.activate()
            time.sleep(2)
            self.simulating_input = True
            pyautogui.press('ctrl')
            time.sleep(1)
            self.simulating_input = False
        except IndexError:
            if not self.error_shown:
                self.error_shown = True
                self.show_error_message()

    def show_error_message(self):
        error_message = QMessageBox(self)
        error_message.setIcon(QMessageBox.Critical)
        error_message.setText("Can't find 'FINAL FANTASY XIV'. Is it running?")
        error_message.setWindowTitle("Error")
        error_message.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        error_message.buttonClicked.connect(self.error_button_clicked)
        error_message.exec_()  

    def error_button_clicked(self, button):
        if button.text() == "Close":
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
