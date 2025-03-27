# Video Comparator

A PyQt-based application for comparing two videos side by side or in overlay mode.

## Features
- Side-by-side video comparison
- Synchronized playback
- Timeline scrubbing
- Equal-size video panels
- Overlay mode with draggable divider (coming soon)

## Requirements
- Python 3.x
- PyQt5
- OpenCV (opencv-python)

## Setup
1. Create a virtual environment:
   ```
   python -m venv venv
   ```
2. Activate the virtual environment:
   - Windows (Command Prompt): `venv\Scripts\activate`
   - Windows (PowerShell): `venv\Scripts\Activate.ps1`
3. Install dependencies:
   ```
   pip install PyQt5 opencv-python
   ```

## Usage
Run the application:
```
python video_comparison_app.py
```
1. Click "Load Videos" to select two video files
2. Use the slider to scrub through the videos
3. Use the Play/Pause button to control playback 