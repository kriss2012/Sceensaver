# Luffy Video Screensaver Automatic Installer
# Run this script in PowerShell to automatically set up the screensaver.

# Get the absolute path to LuffyScreensaver.scr in this directory
$scrPath = Join-Path -Path $PSScriptRoot -ChildPath "LuffyScreensaver.scr"

# Ensure the screensaver file exists
if (Test-Path $scrPath) {
    Write-Host "Configuring Windows Screensaver registry settings..."
    
    # 1. Enable screensaver
    Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'ScreenSaveActive' -Value '1' -Force
    
    # 2. Set screensaver path directly to our compiled file
    Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'SCRNSAVE.EXE' -Value $scrPath -Force
    
    # 3. Set the idle timeout (60 seconds = 1 minute)
    # You can change '60' to '300' for 5 minutes, etc.
    Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'ScreenSaveTimeOut' -Value '60' -Force
    
    # 4. Turn off screen saver password requirement (optional, set to '1' if you want password lock)
    Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'ScreenSaverIsSecure' -Value '0' -Force
    
    # Force Windows to reload registry changes immediately without logoff/reboot
    Write-Host "Updating system parameters..."
    rundll32.exe user32.dll,UpdatePerUserSystemParameters 1 True
    
    Write-Host ""
    Write-Host "SUCCESS! Luffy Video Screensaver has been configured and activated."
    Write-Host "Path: $scrPath"
    Write-Host "Idle Timeout: 1 minute (60 seconds)"
    Write-Host "Note: You can test the screensaver immediately by running: .\LuffyScreensaver.scr /s"
} else {
    Write-Error "Error: LuffyScreensaver.scr was not found in: $PSScriptRoot. Please run compilation first."
}
