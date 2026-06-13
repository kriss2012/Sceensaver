import sys
import os
import ctypes
import cv2
import pygame
import win32gui
import win32con
import time
import traceback

def log_message(message):
    try:
        log_path = r"c:\Users\krishna\Downloads\Sceensaver\screensaver_log.txt"
        with open(log_path, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception:
        pass

# Set DPI Awareness to prevent scaling issues in Windows preview window and screensaver
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def get_video_path():
    video_names = [
        "One-Piece-ScreenSaver.mp4",
        "One Piece - Luffy Clips For Edits (4k) - Xeyrux Boi (1080p, h264).mp4",
        "One-Piece-Live-Wallpaer.mp4"
    ]
    
    # 1. Check if frozen (PyInstaller bundle)
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        for video_name in video_names:
            video_path = os.path.join(base_path, video_name)
            if os.path.exists(video_path):
                return video_path
            
    # 2. Check next to script/exe
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    for video_name in video_names:
        video_path = os.path.join(script_dir, video_name)
        if os.path.exists(video_path):
            return video_path
        
    # 3. Fallback to user's exact folder
    fallback_dir = r"c:\Users\krishna\Downloads\Sceensaver"
    for video_name in video_names:
        fallback_path = os.path.join(fallback_dir, video_name)
        if os.path.exists(fallback_path):
            return fallback_path
        
    return None

def show_settings():
    try:
        import win32api
        win32api.MessageBox(0, "Luffy Clips Screensaver by Antigravity.\n\nThis screensaver plays Luffy Clips from One Piece and does not require additional settings.", "Luffy Screensaver Settings", win32con.MB_OK | win32con.MB_ICONINFORMATION)
    except Exception:
        pass

def run_screensaver(video_path, mode, parent_hwnd):
    log_message(f"run_screensaver started. video_path={video_path}, mode={mode}, parent_hwnd={parent_hwnd}")
    # Initialize pygame
    pygame.init()
    log_message("Pygame initialized.")
    
    # Allow screensaver to run even if Pygame window is active
    try:
        pygame.display.set_allow_screensaver(True)
        log_message("Allowed screensaver in screensaver Pygame.")
    except Exception as e:
        log_message(f"Failed to set allow screensaver in screensaver: {e}")
        
    # Reset thread execution state to prevent keeping display awake
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000) # ES_CONTINUOUS
        log_message("Reset screensaver thread execution state to ES_CONTINUOUS.")
    except Exception as e:
        log_message(f"Failed to reset thread execution state in screensaver: {e}")

    # Get screen / target size
    info = pygame.display.Info()
    if mode == 'preview' and parent_hwnd:
        try:
            rect = win32gui.GetClientRect(parent_hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            log_message(f"Preview window client rect: {rect} -> width={width}, height={height}")
        except Exception as e:
            log_message(f"Failed to get client rect for preview HWND {parent_hwnd}: {e}")
            width, height = 150, 100
    else:
        width = info.current_w
        height = info.current_h
        log_message(f"Target display size from pygame info: width={width}, height={height}")

    # Create pygame screen
    if mode == 'preview':
        # Create a window matching parent size
        screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        
        # Reparent window
        hwnd = pygame.display.get_wm_info()['window']
        log_message(f"Created preview Pygame window HWND: {hwnd}")
        
        # Modify window style to be a child window without decoration
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = style | win32con.WS_CHILD
        style = style & ~win32con.WS_POPUP & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME & ~win32con.WS_MINIMIZEBOX & ~win32con.WS_MAXIMIZEBOX
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        
        # Embed the pygame window inside the parent HWND
        win32gui.SetParent(hwnd, parent_hwnd)
        log_message(f"Reparented Pygame window {hwnd} to parent HWND {parent_hwnd}")
        
        # Position the window inside parent client area
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, width, height, win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)
        log_message("Positioned and showed preview window.")
    else:
        # Fullscreen mode with fallback
        log_message("Entering full screen display mode initialization...")
        try:
            screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            log_message("Initialized FULLSCREEN with DOUBLEBUF.")
        except Exception as e:
            log_message(f"FULLSCREEN initialization failed ({e}). Trying NOFRAME...")
            try:
                screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
                log_message("Initialized NOFRAME.")
            except Exception as e2:
                log_message(f"NOFRAME initialization failed ({e2}). Trying default mode...")
                screen = pygame.display.set_mode((width, height))
                log_message("Initialized default windowed mode.")
        pygame.mouse.set_visible(False)

    # Load video
    log_message(f"Loading video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        log_message(f"ERROR: Failed to open VideoCapture for {video_path}")
        pygame.quit()
        try:
            import win32api
            win32api.MessageBox(0, f"Failed to load video file from:\n{video_path}", "Screensaver Error", win32con.MB_ICONERROR)
        except Exception:
            pass
        return

    video_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    log_message(f"Video file opened successfully. Dimensions: {video_w}x{video_h}, FPS: {fps}")
    if fps <= 0:
        fps = 30.0

    # Aspect ratio calculations for letterboxing/pillarboxing
    video_aspect = video_w / video_h
    screen_aspect = width / height

    if video_aspect > screen_aspect:
        new_w = width
        new_h = int(width / video_aspect)
    else:
        new_h = height
        new_w = int(height * video_aspect)

    x_offset = (width - new_w) // 2
    y_offset = (height - new_h) // 2
    log_message(f"Scaled frame size: {new_w}x{new_h}, Offset: ({x_offset}, {y_offset})")

    clock = pygame.time.Clock()
    running = True
    
    # Store start time and get initial mouse position to avoid immediate startup exits
    start_time = time.time()
    initial_mouse_pos = pygame.mouse.get_pos()
    log_message(f"Initial mouse position recorded: {initial_mouse_pos}")

    # Blank fill first
    screen.fill((0, 0, 0))
    pygame.display.flip()

    log_message("Entering main screensaver playback loop...")
    loop_count = 0
    while running:
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Check window/mouse events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_message("QUIT event received. Exiting loop.")
                running = False
                break
            
            # Key/mouse actions exit screensaver only when running in full screen mode
            if mode == 'run':
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    # Debounce: ignore keys/clicks in the first 0.5s of startup
                    if elapsed_time > 0.5:
                        log_message(f"Key/Click event received (type={event.type}, elapsed={elapsed_time:.2f}s). Exiting screensaver.")
                        running = False
                        break
                elif event.type == pygame.MOUSEMOTION:
                    # Debounce: ignore mouse motion for the first 2.0s of startup to handle OS warp events
                    if elapsed_time > 2.0:
                        if initial_mouse_pos is None:
                            initial_mouse_pos = event.pos
                            log_message(f"Set initial mouse position in loop to: {initial_mouse_pos}")
                        else:
                            dx = abs(event.pos[0] - initial_mouse_pos[0])
                            dy = abs(event.pos[1] - initial_mouse_pos[1])
                            # If mouse moves more than 20 pixels, exit
                            if dx > 20 or dy > 20:
                                log_message(f"Mouse motion threshold exceeded (dx={dx}, dy={dy}, pos={event.pos}, initial={initial_mouse_pos}, elapsed={elapsed_time:.2f}s). Exiting screensaver.")
                                running = False
                                break

        if not running:
            break

        # In preview mode, exit if the preview parent window is closed
        if mode == 'preview' and parent_hwnd:
            if not win32gui.IsWindow(parent_hwnd):
                log_message(f"Preview parent window {parent_hwnd} closed. Exiting screensaver.")
                break

        # Read video frame
        ret, frame = cap.read()
        if not ret:
            # Reopen capture to loop video safely (always works, even if seeking is not supported)
            log_message("End of video file reached. Re-opening capture stream to loop...")
            cap.release()
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if not ret:
                log_message("ERROR: Failed to read frame even after re-opening stream. Breaking loop.")
                break

        # Convert and resize
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (new_w, new_h))

        # Convert numpy array to pygame surface (efficient buffer conversion)
        frame_surface = pygame.image.frombuffer(frame.tobytes(), (new_w, new_h), 'RGB')

        # Render
        screen.fill((0, 0, 0))
        screen.blit(frame_surface, (x_offset, y_offset))
        pygame.display.flip()

        # Tick clock
        clock.tick(fps)
        loop_count += 1
        if loop_count % 300 == 0:
            log_message(f"Screensaver running. Frames rendered: {loop_count}")

    log_message(f"Exiting run_screensaver. Rendered {loop_count} frames total.")
    cap.release()
    pygame.quit()

def main():
    try:
        log_message(f"Screensaver process started. Arguments: {sys.argv}")
        mode = 'run'
        parent_hwnd = None

        # Parse arguments. Windows screensavers can receive flags like /s, /c, /p.
        # Note that Windows can pass flags like /c:1234 or /c 1234. Let's make parsing robust.
        args = [arg.lower() for arg in sys.argv]
        
        # 1. Parse settings mode
        if any(arg.startswith('/c') for arg in args):
            mode = 'settings'
            for arg in args:
                if arg.startswith('/c:'):
                    try:
                        parent_hwnd = int(arg.split(':')[1])
                    except ValueError:
                        pass
        # 2. Parse preview mode
        elif any(arg.startswith('/p') for arg in args):
            mode = 'preview'
            for idx, arg in enumerate(args):
                if arg.startswith('/p:'):
                    try:
                        parent_hwnd = int(arg.split(':')[1])
                    except ValueError:
                        pass
                elif arg == '/p' and idx + 1 < len(args):
                    try:
                        parent_hwnd = int(args[idx + 1])
                    except ValueError:
                        pass
        # 3. Default or explicit run mode
        elif any(arg.startswith('/s') for arg in args):
            mode = 'run'

        log_message(f"Parsed mode: {mode}, parent_hwnd: {parent_hwnd}")

        if mode == 'settings':
            show_settings()
            log_message("Settings dialog shown. Exiting.")
            return

        video_path = get_video_path()
        log_message(f"Resolved video path: {video_path}")
        if not video_path:
            log_message("ERROR: Video path not found. Exiting.")
            try:
                import win32api
                win32api.MessageBox(0, "Luffy Clips video file was not found.\nPlease make sure the video is in the same folder as the screensaver or in downloads.", "Screensaver Error", win32con.MB_ICONERROR)
            except Exception:
                pass
            return

        run_screensaver(video_path, mode, parent_hwnd)
        log_message("Screensaver executed and finished successfully.")

    except Exception as e:
        log_message(f"CRITICAL EXCEPTION in main: {str(e)}\n{traceback.format_exc()}")

if __name__ == '__main__':
    main()
