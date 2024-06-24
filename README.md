# FFXIV Anti-AFK

This project is designed to prevent being marked as AFK (Away From Keyboard) in the game Final Fantasy XIV. The application monitors user input and simulates key presses to ensure the game remains active.

## Features

- Monitors keyboard and mouse input to reset AFK timers.
- Simulates `Ctrl` key presses at regular intervals when no input is detected.
- Option to keep the application window always on top.
- Error handling to alert the user if the game window cannot be found.

## Usage

- Start the application.
- The window will display the time since the last input, AFK mode status, and the time until the next `Ctrl` key press.
- Use the "Keep window on top" checkbox to keep the application window above other windows.

## UML Sequence Diagram

The following UML sequence diagram illustrates the main flow of the application:

![UML Sequence Diagram](https://github.com/Brappp/FFXIV-AFK/blob/main/uml.jpeg)

