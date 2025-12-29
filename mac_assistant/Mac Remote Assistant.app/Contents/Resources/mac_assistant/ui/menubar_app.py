"""
macOS Menu Bar App
Runs in background with menu bar icon
"""

import tkinter as tk
import subprocess
import threading
from pathlib import Path


class MenuBarApp:
    """Menu Bar Application Controller"""

    def __init__(self, dashboard_gui):
        self.dashboard = dashboard_gui
        self.root = dashboard_gui.root

        # Hide window initially
        self.root.withdraw()

        # Create menu bar icon using native macOS
        self.setup_menubar_icon()

        # Window state
        self.window_visible = False

        # Setup window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def setup_menubar_icon(self):
        """Create menu bar icon using native macOS tools"""
        # We'll use a simple AppleScript-based approach
        # For production, consider using rumps or pystray

        # For now, create a dock icon that can be hidden
        self.root.createcommand('tk::mac::ShowPreferences', self.show_window)

    def show_window(self):
        """Show the dashboard window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.window_visible = True

    def hide_window(self):
        """Hide the dashboard window"""
        self.root.withdraw()
        self.window_visible = False

    def toggle_window(self):
        """Toggle window visibility"""
        if self.window_visible:
            self.hide_window()
        else:
            self.show_window()

    def quit_app(self):
        """Quit the application"""
        self.root.quit()


class MenuBarIcon:
    """
    Creates a persistent menu bar icon
    Uses AppleScript + Swift for native macOS integration
    """

    def __init__(self, callback_show, callback_quit):
        self.callback_show = callback_show
        self.callback_quit = callback_quit

        # Create menu bar runner in background
        threading.Thread(target=self._run_menubar, daemon=True).start()

    def _run_menubar(self):
        """Run menu bar icon (using Swift helper if available)"""
        # This would require a Swift helper app
        # For now, we'll use the Dock icon with LSUIElement
        pass

    def create_applescript_menubar(self):
        """Alternative: Use AppleScript to create menu bar presence"""
        script = '''
        tell application "System Events"
            tell application process "Mac Remote Assistant"
                set visible to true
            end tell
        end tell
        '''
        try:
            subprocess.run(['osascript', '-e', script], check=False)
        except:
            pass
