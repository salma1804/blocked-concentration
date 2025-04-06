# 🧠 Distraction Blocker

## 🚀 Overview

Distraction Blocker is a productivity tool designed to help users maintain focus during study or work sessions. Using computer vision technology, it monitors your attention through your webcam and alerts you when you become distracted, helping you develop better concentration habits.

## ✨ Features

- **Real-time Distraction Detection**:
  - Detects when you look away from the screen
  - Identifies when your hands move toward distractions (like your phone)
  - Provides immediate visual alerts to refocus your attention

- **Session Management**:
  - Track the duration of your focus sessions
  - Count the number of times you get distracted
  - Generate reports with concentration statistics

## 🔧 Requirements

- Python 3.6 or higher
- Webcam
- Required Python packages:
  - OpenCV (`cv2`)
  - MediaPipe
  - tkinter (usually included with Python)

## 📥 Installation

1. Clone this repository or download the project files
2. Install the required dependencies:

```bash
pip install opencv-python mediapipe
```

## 🎮 Usage

1. Run the application:

```bash
python concentration-project.py
```

2. The program will open two windows:
   - A webcam feed showing what's being monitored
   - A control panel with session management buttons

3. Click "Commencer" (Start) to begin your focus session.

4. The system will monitor your attention and show alerts if:
   - Your face is not detected (looking away)
   - Your hands are detected near the bottom of the frame (possibly using phone)

5. Click "Arrêter" (Stop) to end your session and generate a concentration report.

6. Press 'q' while the webcam window is active to quit the application.

## ⚙️ How It Works

The application uses:
- **MediaPipe Face Detection**: To determine if you're looking at the screen
- **MediaPipe Hands**: To track hand positions and detect potential distractions
- **Tkinter**: For the simple user interface and alert notifications

When a distraction is detected, the program increases the distraction counter and displays an alert message.

## 📊 Output

After ending a session, the program generates a report file called `rapport_concentration.txt` containing:
- Total session duration
- Number of times you were distracted

## 🔒 Privacy Notice

This application uses your webcam for distraction detection, but all processing is done locally on your device. No video data is transmitted or stored.

## 📄 License

This project is open source and available for personal and educational use.