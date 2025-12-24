"""
Telegram Plugin
"""

from typing import Dict, List
from .base_plugin import MessagingPlugin
import subprocess
import os


class TelegramPlugin(MessagingPlugin):
    """Plugin for Telegram"""

    def __init__(self):
        super().__init__('Telegram')

    def is_available(self) -> bool:
        """Check if Telegram is installed"""
        return os.path.exists('/Applications/Telegram.app')

    def _execute_applescript(self, script: str) -> str:
        """Execute AppleScript"""
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def read_messages(self, limit: int = 10) -> List[Dict]:
        """Read recent Telegram messages"""
        return [{'note': 'Use Telegram Bot API for programmatic access'}]

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        """Send a Telegram message"""
        script = f'''
        tell application "Telegram"
            activate
        end tell

        delay 0.5

        tell application "System Events"
            tell process "Telegram"
                -- Search for contact/chat
                keystroke "f" using command down
                delay 0.3

                keystroke "{recipient}"
                delay 0.5

                keystroke return
                delay 0.3

                -- Type and send message
                keystroke "{message}"
                delay 0.2
                keystroke return
            end tell
        end tell
        '''
        result = self._execute_applescript(script)
        return "Error" not in result

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search Telegram"""
        script = f'''
        tell application "Telegram"
            activate
        end tell

        tell application "System Events"
            tell process "Telegram"
                keystroke "f" using command down
                delay 0.3
                keystroke "{query}"
            end tell
        end tell
        '''
        self._execute_applescript(script)
        return [{'status': 'Search initiated'}]
