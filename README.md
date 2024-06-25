# FFXIV Anti-AFK

This project is designed to prevent being marked as AFK (Away From Keyboard) in the game Final Fantasy XIV. The application monitors user input and simulates key presses to ensure the game remains active.

[Download FFXIV-AFK](https://github.com/Brappp/FFXIV-AFK/releases/tag/v1)

## Features

- Monitors keyboard and mouse input to reset AFK timers.
- Simulates `Ctrl` key presses at regular intervals when no input is detected.
- Option to keep the application window always on top.
- Error handling to alert the user if the game window cannot be found.

## Usage

- The window will display the time since the last input, AFK mode status, and the time until the next `Ctrl` key press.
- Use the "Keep window on top" checkbox to keep the application window above other windows.

## Setup

```
pip install PyQt5 pynput pygetwindow pyautogui
```

## Compiling to an Executable

To compile the application to a standalone executable, you will need to install `pyinstaller` and then use it to create the executable.

1. Install `pyinstaller`:
    ```bash
    pip install pyinstaller
    ```

2. Compile the application:
    ```bash
    pyinstaller --onefile --windowed ffxiv-afk.py
    ```

   This will generate a standalone executable in the `dist` directory.

## UML Sequence Diagram

The following UML sequence diagram illustrates the main flow of the application:

![UML Sequence Diagram](https://github.com/Brappp/FFXIV-AFK/blob/main/uml.jpeg)

