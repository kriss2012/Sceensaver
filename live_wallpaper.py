import sys
import os
import ctypes
import cv2
import pygame
import win32gui
import win32con
import win32api
import win32com.client
import time
import traceback

# Config
LOG_PATH = r"c:\Users\krishna\Downloads\Sceensaver\wallpaper_log.txt"
PID_PATH = r"c:\Users\krishna\Downloads\Sceensaver\wallpaper.pid"
VIDEO_NAME = "HarryPotterScreenSaver.mp4"
FALLBACK_VIDEO_NAME = "One-Piece-Live-Wallpaer.mp4"
SCRIPT_DIR = r"c:\Users\krishna\Downloads\Sceensaver"

def log_message(message):
    try:
        with open(LOG_PATH, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception:
        pass

# Set DPI Awareness to prevent scaling/blurring issues on high-DPI screens
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def get_video_path():
    for name in [VIDEO_NAME, FALLBACK_VIDEO_NAME]:
        video_path = os.path.join(SCRIPT_DIR, name)
        if os.path.exists(video_path):
            return video_path
        if os.path.exists(name):
            return os.path.abspath(name)
    return None

def is_pid_running(pid):
    try:
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    except Exception:
        return False

def stop_wallpaper():
    log_message("Stop request received.")
    if os.path.exists(PID_PATH):
        try:
            with open(PID_PATH, 'r') as f:
                pid = int(f.read().strip())
            if is_pid_running(pid):
                PROCESS_TERMINATE = 0x0001
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
                if handle:
                    ctypes.windll.kernel32.TerminateProcess(handle, 0)
                    ctypes.windll.kernel32.CloseHandle(handle)
                    log_message(f"Terminated running process with PID {pid}.")
                    print(f"Stopped live wallpaper process (PID {pid}).")
                else:
                    print(f"Could not open process {pid} to terminate.")
            else:
                print("Live wallpaper is not currently running.")
        except Exception as e:
            log_message(f"Error terminating previous process: {e}")
            print(f"Error stopping process: {e}")
        
        try:
            os.remove(PID_PATH)
        except Exception:
            pass
    else:
        print("No active PID file found. Live wallpaper is likely stopped.")

def get_workerw_target():
    progman = win32gui.FindWindow("Progman", None)
    if not progman:
        log_message("Progman window not found.")
        return None
        
    # Send message 0x052C to Progman to spawn WorkerW
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
    
    hwnd_icons = None
    workerw_windows = []
    
    def enum_cb(hwnd, extra):
        nonlocal hwnd_icons
        class_name = win32gui.GetClassName(hwnd)
        if class_name == "WorkerW":
            workerw_windows.append(hwnd)
            shell = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
            if shell:
                hwnd_icons = hwnd
        return True
        
    win32gui.EnumWindows(enum_cb, None)
    
    if hwnd_icons:
        # The correct WorkerW is the sibling window directly after hwnd_icons in top-to-bottom order
        try:
            idx = workerw_windows.index(hwnd_icons)
            if idx + 1 < len(workerw_windows):
                return workerw_windows[idx + 1]
        except ValueError:
            pass
            
        sibling = win32gui.FindWindowEx(0, hwnd_icons, "WorkerW", None)
        if sibling:
            return sibling
            
    # Fallback to any WorkerW that is not the icon container
    for w in workerw_windows:
        if w != hwnd_icons:
            return w
            
    return None

def create_startup_shortcut():
    try:
        startup_dir = os.path.join(
            os.environ['APPDATA'],
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )
        # Remove old Luffy shortcut if it exists
        old_shortcut_path = os.path.join(startup_dir, "LuffyLiveWallpaper.lnk")
        if os.path.exists(old_shortcut_path):
            try:
                os.remove(old_shortcut_path)
                log_message(f"Removed old startup shortcut: {old_shortcut_path}")
            except Exception:
                pass

        shortcut_path = os.path.join(startup_dir, "HarryPotterLiveWallpaper.lnk")
        
        script_path = os.path.join(SCRIPT_DIR, "live_wallpaper.py")
        pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = pythonw_path
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = SCRIPT_DIR
        shortcut.Description = "Harry Potter Live Wallpaper Autostart"
        shortcut.IconLocation = pythonw_path
        shortcut.save()
        log_message(f"Created startup shortcut at: {shortcut_path}")
        print(f"Startup shortcut successfully created at: {shortcut_path}")
    except Exception as e:
        log_message(f"Failed to create startup shortcut: {e}")
        print(f"Failed to create startup shortcut: {e}")

def run_wallpaper():
    log_message("Starting live wallpaper run routine.")
    
    # 1. Stop any existing wallpaper instance first
    if os.path.exists(PID_PATH):
        try:
            with open(PID_PATH, 'r') as f:
                old_pid = int(f.read().strip())
            if old_pid != os.getpid() and is_pid_running(old_pid):
                log_message(f"Found active previous instance with PID {old_pid}. Terminating it.")
                PROCESS_TERMINATE = 0x0001
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, old_pid)
                if handle:
                    ctypes.windll.kernel32.TerminateProcess(handle, 0)
                    ctypes.windll.kernel32.CloseHandle(handle)
                    time.sleep(0.5)
        except Exception as e:
            log_message(f"Error checking/terminating previous PID: {e}")
            
    # 2. Save current PID
    try:
        with open(PID_PATH, 'w') as f:
            f.write(str(os.getpid()))
    except Exception as e:
        log_message(f"Failed to save current PID: {e}")

    # 3. Find video path
    video_path = get_video_path()
    if not video_path:
        log_message(f"ERROR: Video file '{VIDEO_NAME}' not found.")
        print(f"Error: Video file '{VIDEO_NAME}' not found in '{SCRIPT_DIR}'")
        return

    # 4. Get target WorkerW window
    workerw_target = get_workerw_target()
    if not workerw_target:
        log_message("ERROR: Could not find target WorkerW window.")
        print("Error: Could not find target Windows WorkerW window.")
        return
    log_message(f"Target WorkerW handle identified: {workerw_target}")

    # 5. Initialize pygame
    pygame.init()
    
    # Allow screensaver to run even when Pygame is rendering a window
    try:
        pygame.display.set_allow_screensaver(True)
        log_message("Allowed screensaver in Pygame.")
    except Exception as e:
        log_message(f"Failed to set allow screensaver: {e}")
        
    # Reset thread execution state to prevent keeping the display awake
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000) # ES_CONTINUOUS
        log_message("Reset thread execution state to ES_CONTINUOUS.")
    except Exception as e:
        log_message(f"Failed to reset thread execution state: {e}")
    
    # Get current resolution
    width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    log_message(f"Desktop resolution detected: {width}x{height}")

    # Create borderless window
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
    pygame_hwnd = pygame.display.get_wm_info()['window']
    
    # Reparent Pygame window to WorkerW
    style = win32gui.GetWindowLong(pygame_hwnd, win32con.GWL_STYLE)
    style = style | win32con.WS_CHILD
    style = style & ~win32con.WS_POPUP & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME
    win32gui.SetWindowLong(pygame_hwnd, win32con.GWL_STYLE, style)
    win32gui.SetParent(pygame_hwnd, workerw_target)
    win32gui.SetWindowPos(pygame_hwnd, win32con.HWND_TOP, 0, 0, width, height, win32con.SWP_SHOWWINDOW)
    
    # 6. Open Video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        log_message("ERROR: Failed to open video file.")
        pygame.quit()
        return
        
    video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
    log_message(f"Video dimensions: {video_w}x{video_h}, FPS: {fps}")

    # Aspect ratio calculations for "Fill" (zoom to cover)
    def calculate_scale_params(w, h, vw, vh):
        video_aspect = vw / vh
        screen_aspect = w / h
        if video_aspect > screen_aspect:
            nw = int(h * video_aspect)
            nh = h
            x_off = (w - nw) // 2
            y_off = 0
        else:
            nw = w
            nh = int(w / video_aspect)
            x_off = 0
            y_off = (h - nh) // 2
        return nw, nh, x_off, y_off

    new_w, new_h, x_offset, y_offset = calculate_scale_params(width, height, video_w, video_h)
    log_message(f"Scaling parameters calculated: scale={new_w}x{new_h}, offset=({x_offset}, {y_offset})")

    clock = pygame.time.Clock()
    running = True
    last_parent_check = time.time()
    
    # Make mouse cursor invisible on the window (just in case)
    pygame.mouse.set_visible(False)

    log_message("Starting main video loop...")
    while running:
        # Check window events (must poll to keep Pygame responsive and prevent hanging)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
                
        if not running:
            break

        current_time = time.time()
        
        # 1. Periodic self-healing checks (every 2 seconds)
        if current_time - last_parent_check > 2.0:
            last_parent_check = current_time
            
            # Reset thread execution state to prevent keeping the display awake
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000) # ES_CONTINUOUS
            except Exception:
                pass
            
            # Check screen resolution change
            cur_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            cur_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            if cur_w != width or cur_h != height:
                width, height = cur_w, cur_h
                log_message(f"Resolution change detected: {width}x{height}. Re-initializing window.")
                screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
                new_w, new_h, x_offset, y_offset = calculate_scale_params(width, height, video_w, video_h)
                win32gui.SetWindowPos(pygame_hwnd, win32con.HWND_TOP, 0, 0, width, height, win32con.SWP_SHOWWINDOW)
            
            # Check WorkerW validity & Parent integrity
            if not win32gui.IsWindow(workerw_target):
                log_message("Target WorkerW was destroyed. Attempting to locate new target...")
                workerw_target = get_workerw_target()
                if workerw_target:
                    win32gui.SetParent(pygame_hwnd, workerw_target)
                    win32gui.SetWindowPos(pygame_hwnd, win32con.HWND_TOP, 0, 0, width, height, win32con.SWP_SHOWWINDOW)
            elif win32gui.GetParent(pygame_hwnd) != workerw_target:
                log_message("Parent window mismatch detected. Re-parenting to WorkerW.")
                win32gui.SetParent(pygame_hwnd, workerw_target)
                win32gui.SetWindowPos(pygame_hwnd, win32con.HWND_TOP, 0, 0, width, height, win32con.SWP_SHOWWINDOW)

        # 2. Read Frame
        ret, frame = cap.read()
        if not ret:
            # Reopen capture to loop video
            cap.release()
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if not ret:
                log_message("ERROR: Failed to read frame even after looping.")
                break

        # 3. Process & Draw
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if (new_w, new_h) == (video_w, video_h):
            frame_surface = pygame.image.frombuffer(frame.tobytes(), (video_w, video_h), 'RGB')
        else:
            frame = cv2.resize(frame, (new_w, new_h))
            frame_surface = pygame.image.frombuffer(frame.tobytes(), (new_w, new_h), 'RGB')
        
        screen.fill((0, 0, 0))
        screen.blit(frame_surface, (x_offset, y_offset))
        pygame.display.flip()
        
        # Tick to match video frame rate and conserve CPU
        clock.tick(fps)

    cap.release()
    pygame.quit()
    log_message("Live wallpaper terminated clean.")
    try:
        os.remove(PID_PATH)
    except Exception:
        pass

def main():
    try:
        log_message(f"Wallpaper script initialized with args: {sys.argv}")
        action = '/start'
        if len(sys.argv) > 1:
            action = sys.argv[1].lower()
            
        if action == '/stop':
            stop_wallpaper()
        elif action == '/status':
            if os.path.exists(PID_PATH):
                with open(PID_PATH, 'r') as f:
                    pid = int(f.read().strip())
                if is_pid_running(pid):
                    print(f"Luffy Live Wallpaper is RUNNING (PID {pid}).")
                else:
                    print("Luffy Live Wallpaper is NOT running (orphaned PID file).")
            else:
                print("Luffy Live Wallpaper is NOT running.")
        elif action == '/shortcut':
            create_startup_shortcut()
        elif action == '/start' or action == '/run':
            # Create startup shortcut automatically so it auto-starts when windows opens
            create_startup_shortcut()
            run_wallpaper()
        else:
            print(f"Unknown option: {action}")
            print("Usage: python live_wallpaper.py [/start | /stop | /status | /shortcut]")
            
    except Exception as e:
        log_message(f"CRITICAL EXCEPTION in main: {str(e)}\n{traceback.format_exc()}")
        print(f"Critical error: {e}")

if __name__ == '__main__':
    main()
