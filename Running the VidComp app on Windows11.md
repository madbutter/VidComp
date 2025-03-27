# Running the Video Comparison App on Windows 11 in Cursor

Here's a specific guide for setting up and running the application on Windows 11 using Cursor:

## Step-by-Step Setup for Windows 11

### 1. Create a Project Directory

Open Command Prompt or PowerShell and run:

```cmd
mkdir video_comparison_app
cd video_comparison_app
```

### 2. Create a Virtual Environment

In your project directory:

```cmd
python -m venv venv
```

### 3. Activate the Virtual Environment

In Windows 11, activate the virtual environment using:

```cmd
venv\Scripts\activate
```

You'll see `(venv)` appear at the beginning of your command prompt, indicating the virtual environment is active.

### 4. Install Required Dependencies

With the virtual environment activated:

```cmd
pip install PyQt5 opencv-python
```

### 5. Create the Application File in Cursor

1. Open Cursor
2. Navigate to File > Open Folder... and select your `video_comparison_app` folder
3. Create a new file called `video_comparison_app.py`
4. Paste the code I provided earlier into this file
5. Save the file (Ctrl+S)

### 6. Configure Cursor to Use Your Virtual Environment

1. Open the Command Palette in Cursor (Ctrl+Shift+P)
2. Type "Python: Select Interpreter" and select it
3. Choose the interpreter from your virtual environment (it should show up as `./venv/Scripts/python.exe`)

### 7. Running the App from Cursor

#### Method 1: Using the Terminal in Cursor
1. Open the Terminal in Cursor (View > Terminal or use the shortcut Ctrl+`)
2. Make sure you're in your project directory
3. If the virtual environment isn't already activated, activate it:
   ```cmd
   venv\Scripts\activate
   ```
4. Run the application:
   ```cmd
   python video_comparison_app.py
   ```

#### Method 2: Create a Convenient Run Script

Create a file named `run_app.bat` in your project directory with the following content:

```batch
@echo off
call venv\Scripts\activate
python video_comparison_app.py
```

You can then run this batch file by:
1. Double-clicking it in Windows Explorer
2. Or running it from the terminal in Cursor:
   ```cmd
   .\run_app.bat
   ```

### 8. Debugging in Cursor

To debug the application in Cursor:

1. Set breakpoints by clicking in the gutter (the space to the left of line numbers)
2. Make sure the correct interpreter is selected (the one from your virtual environment)
3. Press F5 or select the Run > Start Debugging menu option
4. Select "Python File" as the debug configuration
5. The application will start and will pause at your breakpoints

## Windows 11 Specific Tips

1. **File Explorer Integration**: You can right-click in the Windows 11 File Explorer and select "Open in Cursor" if you've set up the shell integration.

2. **Terminal Preference**: Windows 11 comes with both PowerShell and Command Prompt. Either will work, but PowerShell offers more advanced features if you need them.

3. **Performance Considerations**: For optimal video playback performance on Windows 11, ensure your graphics drivers are up to date.

4. **Windows Security**: If you get a Windows security alert about network access when first running the app, it's generally safe to allow access.

5. **High-DPI Displays**: If you're using a high-DPI display on Windows 11, you might need to adjust scaling. Add this line near the top of your `__main__` block:
   ```python
   if __name__ == "__main__":
       # Enable High DPI scaling
       QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
       QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
       
       app = QApplication(sys.argv)
       window = VideoComparisonApp()
       window.show()
       sys.exit(app.exec_())
   ```

6. **Folder Structure**: For a clean project structure on Windows, consider organizing your code like this:
   ```
   video_comparison_app/
   ├── venv/                     # Virtual environment
   ├── src/                      # Source code folder
   │   └── video_comparison_app.py  # Main application file
   ├── run_app.bat               # Run script
   └── requirements.txt          # Dependencies list
   ```

With these steps, you should be able to effectively develop, run, and debug your video comparison application on Windows 11 using Cursor, all while keeping it isolated from your other Python projects.