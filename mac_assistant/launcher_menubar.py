#!/usr/bin/env python3
"""
Mac Remote Assistant - Menu Bar Version
Runs in background with menu bar icon
"""

import os
import sys
from pathlib import Path
import threading
import rumps

# Add parent directory to path
if not getattr(sys, 'frozen', False):
    parent_dir = str(Path(__file__).parent.parent)
    current_dir = str(Path(__file__).parent)
    sys.path.insert(0, parent_dir)
    sys.path.insert(0, current_dir)
else:
    sys.path.insert(0, str(Path(__file__).parent))

# Import without mac_assistant prefix
from core_v2 import MacAssistantCore
from ui.dashboard import DashboardGUI


class MacAssistantMenuBar(rumps.App):
    """Menu Bar Application"""

    def __init__(self):
        super(MacAssistantMenuBar, self).__init__(
            "🤖",  # Menu bar icon
            title="Mac Assistant",
            quit_button=None  # Custom quit button
        )

        # Menu items
        self.menu = [
            rumps.MenuItem("Dashboard öffnen", callback=self.open_dashboard),
            rumps.separator,
            rumps.MenuItem("Neue E-Mails prüfen", callback=self.check_emails),
            rumps.MenuItem("Aktivitäten zeigen", callback=self.show_activities),
            rumps.separator,
            rumps.MenuItem("Einstellungen", callback=self.open_settings),
            rumps.separator,
            rumps.MenuItem("Beenden", callback=self.quit_app)
        ]

        # Initialize core
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.core = None
        self.dashboard = None
        self.dashboard_window = None

        # Initialize core in background
        threading.Thread(target=self._init_core, daemon=True).start()

    def _init_core(self):
        """Initialize core in background"""
        try:
            self.core = MacAssistantCore(api_key=self.api_key)
            self.title = "🤖 ●"  # Green dot = ready
        except Exception as e:
            print(f"Core init error: {e}")
            self.title = "🤖 ○"  # Empty dot = error

    @rumps.clicked("Dashboard öffnen")
    def open_dashboard(self, _):
        """Open dashboard window"""
        if self.dashboard is None:
            if self.core:
                # Create dashboard in background thread
                threading.Thread(target=self._create_dashboard, daemon=True).start()
            else:
                rumps.notification(
                    "Mac Assistant",
                    "Fehler",
                    "Core noch nicht initialisiert. Bitte warten..."
                )
        else:
            # Show existing dashboard
            self.dashboard.root.deiconify()
            self.dashboard.root.lift()

    def _create_dashboard(self):
        """Create dashboard GUI"""
        try:
            self.dashboard = DashboardGUI(self.core)

            # Override close behavior - hide instead of quit
            self.dashboard.root.protocol("WM_DELETE_WINDOW", self._hide_dashboard)

            # Start mainloop
            self.dashboard.root.mainloop()

        except Exception as e:
            print(f"Dashboard error: {e}")
            rumps.notification(
                "Mac Assistant",
                "Fehler",
                f"Dashboard konnte nicht geöffnet werden: {str(e)}"
            )

    def _hide_dashboard(self):
        """Hide dashboard instead of closing"""
        if self.dashboard:
            self.dashboard.root.withdraw()

    @rumps.clicked("Neue E-Mails prüfen")
    def check_emails(self, _):
        """Check for new emails"""
        if not self.core:
            rumps.notification("Mac Assistant", "Fehler", "Core nicht initialisiert")
            return

        try:
            # Get unread emails count
            result = self.core.process_user_query("Wie viele ungelesene E-Mails habe ich?")
            rumps.notification("Mac Assistant", "E-Mails", result[:100])
        except Exception as e:
            rumps.notification("Mac Assistant", "Fehler", str(e))

    @rumps.clicked("Aktivitäten zeigen")
    def show_activities(self, _):
        """Show today's activities"""
        if not self.core:
            rumps.notification("Mac Assistant", "Fehler", "Core nicht initialisiert")
            return

        try:
            result = self.core.process_user_query("Was habe ich heute gemacht?")
            rumps.notification("Mac Assistant", "Aktivitäten", result[:100])
        except Exception as e:
            rumps.notification("Mac Assistant", "Fehler", str(e))

    @rumps.clicked("Einstellungen")
    def open_settings(self, _):
        """Open settings"""
        # For now, open dashboard settings tab
        self.open_dashboard(None)
        rumps.notification(
            "Mac Assistant",
            "Einstellungen",
            "Öffne Dashboard → Einstellungen-Tab"
        )

    @rumps.clicked("Beenden")
    def quit_app(self, _):
        """Quit application"""
        # Clean shutdown
        if self.dashboard:
            try:
                self.dashboard.root.quit()
            except:
                pass
        rumps.quit_application()


def main():
    """Main entry point for menu bar app"""

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY not set")

    # Start menu bar app
    app = MacAssistantMenuBar()
    app.run()


if __name__ == "__main__":
    main()
