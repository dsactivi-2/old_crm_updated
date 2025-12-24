#!/usr/bin/env python3
"""
Mac Remote Assistant Launcher
Native App Entry Point
"""

import os
import sys
from pathlib import Path

# Add parent directory to path (only if not in py2app bundle)
if not getattr(sys, 'frozen', False):
    parent_dir = str(Path(__file__).parent.parent)
    current_dir = str(Path(__file__).parent)
    sys.path.insert(0, parent_dir)
    sys.path.insert(0, current_dir)
else:
    # In py2app bundle, add current directory
    sys.path.insert(0, str(Path(__file__).parent))

# Import without mac_assistant prefix
from core_v2 import MacAssistantCore
from ui.dashboard import DashboardGUI


def main():
    """Main entry point for native app"""

    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')

    # Initialize core
    try:
        core = MacAssistantCore(api_key=api_key)
    except Exception as e:
        print(f"Error initializing: {e}")
        # Even if error, continue to show GUI with settings option
        core = None

    # Launch Dashboard GUI
    try:
        if core:
            gui = DashboardGUI(core)
            gui.run()
        else:
            # Show error in GUI
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Fehler",
                "Konnte App nicht initialisieren.\nBitte prüfe deine Einstellungen."
            )
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
