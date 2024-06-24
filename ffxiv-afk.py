import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QCheckBox, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from pynput import keyboard, mouse
import pygetwindow as gw
import pyautogui

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_input_time = time.time()
        self.afk_active = False
        self.error_shown = False
        self.simulating_input = False
        self.ctrl_press_interval = 120  
        self.initUI()

        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        mouse_listener = mouse.Listener(on_click=self.on_click)
        keyboard_listener.start()
        mouse_listener.start()

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.timeout.connect(self.update_label)
        self.inactivity_timer.start(1000)

        self.ctrl_timer = QTimer(self)
        self.ctrl_timer.timeout.connect(self.simulate_ctrl_press)

    def initUI(self):
        self.setWindowTitle('FFXIV Anti-AFK')
        self.setGeometry(300, 300, 400, 120)
        self.setStyleSheet("background-color: #333; color: #DDD; font-size: 16px;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.timer_label = QLabel('Time since last input: 00:00:00', self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)

        self.afk_label = QLabel('AFK mode: OFF', self)
        self.afk_label.setAlignment(Qt.AlignCenter)
        self.afk_label.setStyleSheet("color: green;")
        layout.addWidget(self.afk_label)

        self.ctrl_timer_label = QLabel('Next ctrl press in: --', self)
        self.ctrl_timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ctrl_timer_label)

        bottom_layout = QHBoxLayout()
        self.always_on_top_checkbox = QCheckBox("Keep window on top", self)
        self.always_on_top_checkbox.stateChanged.connect(self.toggle_always_on_top)  
        bottom_layout.addWidget(self.always_on_top_checkbox)

        bottom_layout.addStretch(1)  

        self.github_label = QLabel('<a href="https://github.com/Brappp/FFXIV-AFK" style="color: #1E90FF; text-decoration: none;">GitHub</a>', self)
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setStyleSheet("font-size: 18px; text-align: right; font-weight: bold;")
        bottom_layout.addWidget(self.github_label, alignment=Qt.AlignRight)

        layout.addLayout(bottom_layout)

    def toggle_always_on_top(self, state):
        if state == Qt.Checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def on_press(self, key):
        self.last_input_time = time.time()
        if self.afk_active:
            QTimer.singleShot(0, self.deactivate_afk_mode)

    def on_click(self, x, y, button, pressed):
        self.last_input_time = time.time()
        if self.afk_active:
            QTimer.singleShot(0, self.deactivate_afk_mode)

    def deactivate_afk_mode(self):
        self.afk_active = False
        self.afk_label.setText('AFK mode: OFF')
        self.afk_label.setStyleSheet("color: green;")
        self.ctrl_timer.stop()
        self.ctrl_timer_label.setText('Next ctrl press in: --')

    def update_label(self):
        elapsed = time.time() - self.last_input_time
        self.timer_label.setText(f'Time since last input: {int(elapsed)} seconds')
        if elapsed > 120:
            if not self.afk_active:
                self.activate_afk_mode()

    def activate_afk_mode(self):
        self.afk_active = True
        self.afk_label.setText('AFK mode: ON')
        self.afk_label.setStyleSheet("color: red;")
        self.ctrl_press_interval = 120
        self.ctrl_timer.start(1000)
        self.error_shown = False  

    def simulate_ctrl_press(self):
        self.ctrl_press_interval -= 1
        self.ctrl_timer_label.setText(f'Next ctrl press in: {self.ctrl_press_interval} seconds')
        if self.ctrl_press_interval <= 0:
            self.press_ctrl()
            self.ctrl_press_interval = 120  

    def press_ctrl(self):
        try:
            window = [win for win in gw.getWindowsWithTitle('FINAL FANTASY XIV') if 'FINAL FANTASY XIV' in win.title][0]
            window.minimize()
            time.sleep(1)
            window.restore()
            window.activate()
            time.sleep(2)
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
