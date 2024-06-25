import sys
import time
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QCheckBox, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from pynput import keyboard, mouse
import pygetwindow as gw

if ctypes.sizeof(ctypes.c_void_p) == 8:  # 64-bit
    ULONG_PTR = ctypes.c_ulonglong
else:  # 32-bit
    ULONG_PTR = wintypes.ULONG

# Load user32
user32 = ctypes.WinDLL('user32', use_last_error=True)

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        class _KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", wintypes.WORD),
                        ("wScan", wintypes.WORD),
                        ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ULONG_PTR)]

        _anonymous_ = ("ki",)
        _fields_ = [("ki", _KEYBDINPUT),]

    _anonymous_ = ("i",)
    _fields_ = [("type", wintypes.DWORD),
                ("i", _INPUT)]

def send_input(hwnd, vk, scan, flags):
    inp = INPUT(type=1,  # INPUT_KEYBOARD
                i=INPUT._INPUT(ki=INPUT._INPUT._KEYBDINPUT(wVk=vk,
                                                           wScan=scan,
                                                           dwFlags=flags,
                                                           time=0,
                                                           dwExtraInfo=user32.GetMessageExtraInfo())))
    user32.PostMessageA(hwnd, 0x100, vk, 0) # WM_KEYDOWN
    user32.PostMessageA(hwnd, 0x101, vk, 0) # WM_KEYUP

def get_ffxiv_hwnd():
    windows = gw.getWindowsWithTitle('FINAL FANTASY XIV')
    if windows:
        return windows[0]._hWnd
    return None

class InputMonitor:
    """ Monitor system-wide keyboard and mouse events, check if they occur with FFXIV active """
    def __init__(self, callback):
        self.last_active_time = time.time()
        self.callback = callback
        self.keyboard_listener = keyboard.Listener(on_press=self.on_input_detected)
        self.mouse_listener = mouse.Listener(on_click=self.on_input_detected)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def on_input_detected(self, *args):
        """ Update the last active time if FFXIV is the active window when input is detected """
        if is_ffxiv_active():
            self.last_active_time = time.time()
            self.callback()

def is_ffxiv_active():
    """ Check if 'FINAL FANTASY XIV' is the active window """
    try:
        ffxiv_window = gw.getWindowsWithTitle('FINAL FANTASY XIV')[0]
        return ffxiv_window.isActive
    except IndexError:
        return False

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.input_monitor = InputMonitor(self.reset_afk_mode)
        self.error_shown = False

        self.countdown_time = 120
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.timeout.connect(self.check_inactivity)
        self.inactivity_timer.start(1000)  

    def initUI(self):
        self.setWindowTitle('FFXIV Anti-AFK')
        self.setGeometry(300, 300, 400, 150)
        self.setStyleSheet("background-color: #333; color: #DDD; font-size: 16px;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.timer_label = QLabel('Sending Ctrl in: 120 seconds', self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.timer_label)

        self.afk_label = QLabel('AFK mode: OFF', self)
        self.afk_label.setAlignment(Qt.AlignCenter)
        self.afk_label.setStyleSheet("color: green;")
        layout.addWidget(self.afk_label)

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

    def reset_afk_mode(self):
        """ Reset the inactivity timer and update the UI """
        self.input_monitor.last_active_time = time.time()
        self.afk_label.setText('AFK mode: OFF')
        self.afk_label.setStyleSheet("color: green;")
        self.countdown_time = 120

    def check_inactivity(self):
        """ Check if the user has been inactive and update UI """
        elapsed = time.time() - self.input_monitor.last_active_time

        if elapsed > 0 and self.afk_label.text() == 'AFK mode: OFF':  
            self.afk_label.setText('AFK mode: ON')
            self.afk_label.setStyleSheet("color: red;")

        if elapsed >= 1:
            self.countdown_time -= 1
            self.timer_label.setText(f'Sending Ctrl in: {self.countdown_time} seconds')

        if self.countdown_time <= 0:
            self.press_ctrl()
            self.reset_afk_mode()

    def press_ctrl(self):
        hwnd_ffxiv = get_ffxiv_hwnd()
        if hwnd_ffxiv:
            send_input(hwnd_ffxiv, 0x11, 0, 0) 
        else:
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
        self.error_shown = False 
        if button.text() == "Close":
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
