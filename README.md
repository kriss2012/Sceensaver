# 🏴‍☠️ Luffy Live Wallpaper & Screensaver

Welcome to the **Luffy Live Wallpaper & Screensaver** project! This repository contains a complete Python-based solution to customize your Windows desktop with custom high-quality animations. It features two components:

1. **Interactive Screensaver (`.scr`)**: A full-screen video player built on Pygame and OpenCV that integrates into Windows screensaver controls (handling preview, run, and settings modes).
2. **Live Wallpaper Engine**: A background service that injects an MP4 video directly behind your desktop icons using Windows native API calls (`WorkerW` manipulation).

---

## 📋 Table of Contents
1. [🚀 Step-by-Step Laptop Setup Guide](#-step-by-step-laptop-setup-guide)
2. [🛠️ How to Compile/Make the Screensaver (.scr) File](#%EF%B8%8F-how-to-compilemake-the-screensaver-scr-file)
3. [⚙️ Installing & Activating the Screensaver](#%EF%B8%8F-installing--activating-the-screensaver)
4. [🖥️ Launching the Live Wallpaper](#%EF%B8%8F-launching-the-live-wallpaper)
5. [⚠️ Troubleshooting & Common Errors Explained](#%EF%B8%8F-troubleshooting--common-errors-explained)

---

## 🚀 Step-by-Step Laptop Setup Guide

Follow these steps to set up the runtime environment on your laptop:

### Step 1: Install Python
Ensure Python (version 3.8 or higher) is installed on your Windows laptop.
1. Download Python from the [official website](https://www.python.org/downloads/).
2. **CRITICAL:** During installation, check the box that says **"Add Python to PATH"**. If you skip this, scripts and commands will not run.

### Step 2: Open Terminal / Command Prompt
Open PowerShell or Command Prompt (CMD) in the project directory:
* Open the folder `Sceensaver` in File Explorer.
* Type `cmd` or `powershell` in the address bar and press **Enter**.

### Step 3: Install Required Dependencies
Run the following command to install the required Python packages:
```bash
pip install opencv-python pygame pywin32 pyinstaller
```

> [!NOTE]
> * **`opencv-python`** handles video decoding and frame reading.
> * **`pygame`** provides the graphics and windowing layer.
> * **`pywin32`** allows access to low-level Windows API functions (re-parenting windows, finding shell desktop processes).
> * **`pyinstaller`** compiles python scripts into standalone executables.

---

## 🛠️ How to Compile/Make the Screensaver (.scr) File
Windows screensavers are standard executable files (`.exe`) renamed to `.scr`. Since you want a standalone screensaver that doesn't require Python installed on every laptop, you can compile `screensaver.py` using PyInstaller.

We use the pre-configured `LuffyScreensaver.spec` file, which bundles the script and the video asset (`One-Piece-ScreenSaver.mp4`) into a single output executable.

### Method A: Compiling with the Spec File (Recommended)
Run the following command in your terminal:
```bash
pyinstaller --clean LuffyScreensaver.spec
```

### Method B: Compiling with Command Line Directly
If you prefer to compile manually without the spec file, run:
```bash
pyinstaller --onefile --noconsole --name LuffyScreensaver --add-data "One-Piece-ScreenSaver.mp4;." screensaver.py
```
> [!WARNING]
> In Windows, the `--add-data` separator is a **semicolon (`;`)**. If you copy-paste commands using a colon (`:`), PyInstaller will throw a compilation error.

### Step 4: Rename `.exe` to `.scr`
1. Once compilation finishes, navigate into the generated `dist` folder.
2. Locate `LuffyScreensaver.exe`.
3. Rename the file extension from `.exe` to `.scr` (e.g. `LuffyScreensaver.scr`).
4. Copy `LuffyScreensaver.scr` back to your main project directory.

---

## ⚙️ Installing & Activating the Screensaver

To make Windows recognize and trigger your screensaver, use one of the following methods:

### Method 1: Automatic Installer (PowerShell)
Right-click on `install.ps1` and select **Run with PowerShell**. 
* This script configures Windows registry settings to set `LuffyScreensaver.scr` as your active screensaver, sets a 1-minute timeout, and triggers system parameter refreshes.

> [!TIP]
> If Windows blocks execution, see [Troubleshooting Error 4](#error-4-powershell-script-execution-blocked-by-policy).

### Method 2: Manual Windows Installation
1. Right-click on `LuffyScreensaver.scr` in File Explorer.
2. Click **Install** from the context menu.
3. The native Windows Screensaver Settings panel will open. Select "LuffyScreensaver" from the list and configure your idle timeout (e.g., 5 minutes).

---

## 🖥️ Launching the Live Wallpaper

The Live Wallpaper component injects a video directly behind your desktop icons.

### To Start the Wallpaper:
Double-click `start_wallpaper.bat`.
* This launches `live_wallpaper.py` in the background (using `pythonw.exe` so no terminal window stays open).
* It registers itself in the **Windows Startup folder**, meaning it will launch automatically whenever you turn on your laptop.

### To Stop the Wallpaper:
Double-click `stop_wallpaper.bat`.
* This reads the running process identifier (`wallpaper.pid`) and terminates the background loop safely.

---

## ⚠️ Troubleshooting & Common Errors Explained

Below are explanations and solutions for errors you might encounter while building or running the screensaver and live wallpaper:

### Error 1: `pywintypes.error: (1400, 'SetParent', 'Invalid window handle.')`
* **Why it happens**: Windows screensaver preview mode operates by starting the screensaver with arguments like `/p <HWND_ID>`. The screensaver attempts to embed its Pygame window inside this parent window. If the user clicks off, clicks a settings tab, or closes the screensaver settings panel quickly, the parent window handle (`HWND`) is destroyed *before* or *during* Pygame's startup phase, causing the Windows API to fail.
* **Solution**: This error is completely harmless for full screensaver execution (which runs in full screen `/s` without a parent handle). If it happens, it will be caught by the script's try/catch boundaries, logged, and exit gracefully. No action is required.

### Error 2: Video file not found or failed to load
* **Why it happens**: OpenCV (`cv2.VideoCapture`) needs to open the video file. When compiling via PyInstaller, files are unpacked into a temporary folder (`C:\Users\<user>\AppData\Local\Temp\_MEIxxxx\`). If the script looks for the video file using a regular relative path instead of checking `sys._MEIPASS`, it won't find it.
* **Solution**: The code is designed to search three areas:
  1. The PyInstaller extraction path: `sys._MEIPASS` (for compiled versions).
  2. The folder where the `.scr`/`.exe` is running.
  3. The fallback path: `C:\Users\krishna\Downloads\Sceensaver`.
  
  Ensure that `One-Piece-ScreenSaver.mp4` is present in your root directory during compilation and next to the script during running.

### Error 3: Screensaver exits immediately after starting
* **Why it happens**: Pygame listens for mouse motion to terminate the screensaver. However, high-DPI screens or sensitive trackpads trigger minute mouse movements (1-2 pixels) right as the screensaver launches.
* **Solution**: The script has a built-in debounce filter:
  * Keypresses/clicks are ignored for the first **0.5 seconds**.
  * Mouse movement is ignored for the first **2.0 seconds** of startup.
  * Movement is ignored unless it exceeds a threshold of **20 pixels**.
  
  If the screensaver still exits immediately, avoid moving the mouse or touching the trackpad immediately after the screen goes idle.

### Error 4: PowerShell Script Execution blocked by policy
* **Why it happens**: By default, Windows blocks running downloaded PowerShell scripts for security reasons.
* **Solution**:
  1. Open PowerShell as Administrator.
  2. Run the command:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```
  3. Re-run `install.ps1`.

### Error 5: Antivirus / SmartScreen Blocking
* **Why it happens**: Since you are compiling a custom executable locally, it lacks a trusted digital signature. Windows Defender or other antiviruses might flag it as suspicious.
* **Solution**: If Windows SmartScreen prompts "Windows protected your PC", click **More Info** -> **Run anyway**. You can also add the project directory to your antivirus exclusions.

### Error 6: `ModuleNotFoundError: No module named 'win32gui'`
* **Why it happens**: You installed `pywin32` but the Windows binding libraries were not fully registered in your Python environment.
* **Solution**: Run the pywin32 post-installation script to register the DLLs:
  ```bash
  python [Python_Directory]/Scripts/pywin32_postinstall.py -install
  ```
  *(Or simply uninstall and reinstall the package: `pip uninstall pywin32` followed by `pip install pywin32`)*.
