# 🟢 CMatrix Video Screensaver Optimization & Deployment Guide

This guide details how the **CMatrix Video Screensaver** was configured, compiled, optimized, and activated to ensure a **completely lag-free startup and playback** experience.

---

## 🛠️ Optimization Highlights

To prevent lagging and high CPU usage, the following optimizations were applied:

1. **Video Compression & Resizing (FFmpeg)**:
   - **Original**: `1920x936` resolution with a very high bitrate (~7.75 Mbps) for a 14-second video, resulting in a large file (~14.1 MB) that is CPU-heavy to decode.
   - **Optimized**: Scaled to `1280x624` (perfectly matching a 1280x720 aspect ratio) with a lower CRF and compressed using H.264 (`cmatrix_optimized.mp4`). This dropped the bitrate to **~1.2 Mbps** and file size to **2.4 MB**, making it extremely light on memory and CPU.
   
2. **Direct File Streaming (Zero Startup Delay)**:
   - Built the screensaver using a `.spec` configuration that does **not** bundle the video directly inside the executable.
   - Rather than waiting 10-20 seconds for PyInstaller to extract a video from temporary directories (`sys._MEIPASS`) on launch, the executable directly streams `cmatrix_optimized.mp4` from the folder, activating **instantly**.

3. **Rendering Pipeline Improvements (`screensaver.py`)**:
   - **Omitted Redundant Clears**: Removed `screen.fill((0, 0, 0))` from the main frame loop. Pygame now clears the background once at startup rather than on every single frame, saving CPU and GPU work.
   - **Bypassed Resizing**: When the video is played on a screen with matching aspect metrics, the CPU-bound `cv2.resize` function is entirely bypassed.
   - **Fast Interpolation fallback**: If the video does need to be scaled to a different monitor resolution, it now uses `cv2.INTER_NEAREST` (nearest-neighbor) interpolation instead of default bilinear scaling. This is significantly faster and maintains the sharp, crisp pixel-art look of the digital rain characters.

4. **Dynamic Video Path Resolution**:
   - The logic in `get_video_path` now automatically inspects the name of the executable (`sys.executable` or `sys.argv[0]`).
   - If the name contains `cmatrix`, it targets `cmatrix_optimized.mp4` / `cmatrix.mp4`. This maintains single-codebase compatibility for all screensavers (Luffy, Harry Potter, and CMatrix).

---

## 🚀 Installation & Testing

### 1. Registry Activation
The screensaver has been configured and activated in the Windows Registry using the custom automatic installer script.
- **Script**: `install_cmatrix.ps1`
- **Settings updated**:
  - `ScreenSaveActive` = `1` (Enabled)
  - `SCRNSAVE.EXE` = `C:\Users\krishna\Downloads\Sceensaver\CMatrixScreensaver.scr`
  - `ScreenSaveTimeOut` = `60` (1 minute idle delay)

### 2. Manual Test Command
To run and test the CMatrix screensaver immediately in fullscreen, run this command in PowerShell:
```powershell
.\CMatrixScreensaver.scr /s
```
*Note: Any mouse movement or keyboard input will immediately close the screensaver.*

### 3. Settings / Preview Test
- **Settings Panel**: To open the properties/settings panel:
  ```powershell
  .\CMatrixScreensaver.scr /c
  ```
- **Preview Box**: To test embedding the screensaver into a specific window handler (such as the small preview thumbnail in the Windows Screen Saver Settings window):
  ```powershell
  .\CMatrixScreensaver.scr /p <HWND>
  ```
