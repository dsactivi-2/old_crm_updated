"""
AppleScript Bridge
Interfaces with macOS apps via AppleScript
"""

import subprocess
import json
from typing import List, Dict, Optional


class AppleScriptBridge:
    """Bridge to execute AppleScript commands for Mac apps"""

    @staticmethod
    def execute_script(script: str) -> str:
        """Execute an AppleScript and return the result"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Error: Script execution timeout"
        except Exception as e:
            return f"Error: {str(e)}"

    # ===== MAIL APP =====

    def get_unread_emails(self, limit: int = 10) -> List[Dict]:
        """Get unread emails from Mail.app"""
        script = f'''
        tell application "Mail"
            set unreadMessages to messages of inbox whose read status is false
            set emailList to {{}}
            repeat with msg in (items 1 thru (count of unreadMessages) of unreadMessages)
                set emailInfo to {{subject:subject of msg, sender:(sender of msg), dateReceived:(date received of msg)}}
                set end of emailList to emailInfo
                if (count of emailList) >= {limit} then exit repeat
            end repeat
            return emailList
        end tell
        '''
        result = self.execute_script(script)
        return result

    def send_email(self, to_address: str, subject: str, body: str) -> bool:
        """Send an email via Mail.app"""
        script = f'''
        tell application "Mail"
            set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
            tell newMessage
                make new to recipient with properties {{address:"{to_address}"}}
                send
            end tell
        end tell
        '''
        result = self.execute_script(script)
        return "Error" not in result

    def reply_to_latest_email(self, reply_text: str) -> bool:
        """Reply to the most recent email"""
        script = f'''
        tell application "Mail"
            set latestMessage to item 1 of (messages of inbox)
            set replyMessage to reply latestMessage with opening window yes
            set content of replyMessage to "{reply_text}"
            send replyMessage
        end tell
        '''
        result = self.execute_script(script)
        return "Error" not in result

    def get_recent_emails(self, hours: int = 24, limit: int = 20) -> str:
        """Get recent emails from the last N hours"""
        script = f'''
        tell application "Mail"
            set cutoffDate to (current date) - ({hours} * hours)
            set recentMessages to (messages of inbox whose date received > cutoffDate)
            set emailList to ""
            repeat with msg in (items 1 thru (count of recentMessages) of recentMessages)
                set emailList to emailList & "From: " & (sender of msg) & "\\n"
                set emailList to emailList & "Subject: " & (subject of msg) & "\\n"
                set emailList to emailList & "Date: " & (date received of msg) & "\\n---\\n"
            end repeat
            return emailList
        end tell
        '''
        return self.execute_script(script)

    # ===== MESSAGES (iMessage/WhatsApp via Messages) =====

    def send_message(self, contact: str, message: str) -> bool:
        """Send a message via Messages.app"""
        script = f'''
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "{contact}" of targetService
            send "{message}" to targetBuddy
        end tell
        '''
        result = self.execute_script(script)
        return "Error" not in result

    def get_recent_messages(self, limit: int = 10) -> str:
        """Get recent messages"""
        script = f'''
        tell application "Messages"
            set recentChats to chats
            set messageList to ""
            repeat with aChat in (items 1 thru (count of recentChats) of recentChats)
                try
                    set chatName to name of aChat
                    set lastMsg to last message of aChat
                    set msgText to text of lastMsg
                    set messageList to messageList & "Chat: " & chatName & "\\n"
                    set messageList to messageList & "Message: " & msgText & "\\n---\\n"
                end try
            end repeat
            return messageList
        end tell
        '''
        return self.execute_script(script)

    # ===== PHOTOS APP =====

    def search_photos(self, search_term: str, limit: int = 20) -> str:
        """Search for photos by name or date"""
        script = f'''
        tell application "Photos"
            activate
            set searchResults to search for "{search_term}"
            set photoList to ""
            repeat with aPhoto in (items 1 thru (count of searchResults) of searchResults)
                try
                    set photoName to name of aPhoto
                    set photoDate to date of aPhoto
                    set photoList to photoList & "Name: " & photoName & " | Date: " & photoDate & "\\n"
                end try
            end repeat
            return photoList
        end tell
        '''
        return self.execute_script(script)

    def delete_photos_by_name(self, photo_names: List[str]) -> bool:
        """Delete photos by their names"""
        names_str = '", "'.join(photo_names)
        script = f'''
        tell application "Photos"
            set photoNames to {{"{names_str}"}}
            repeat with photoName in photoNames
                set foundPhotos to search for photoName
                repeat with aPhoto in foundPhotos
                    if name of aPhoto is photoName then
                        delete aPhoto
                    end if
                end repeat
            end repeat
        end tell
        '''
        result = self.execute_script(script)
        return "Error" not in result

    def get_recent_photos(self, days: int = 7) -> str:
        """Get photos from the last N days"""
        script = f'''
        tell application "Photos"
            set cutoffDate to (current date) - ({days} * days)
            set allPhotos to every media item
            set recentPhotos to ""
            repeat with aPhoto in allPhotos
                if date of aPhoto > cutoffDate then
                    set photoName to name of aPhoto
                    set photoDate to date of aPhoto
                    set recentPhotos to recentPhotos & "Name: " & photoName & " | Date: " & photoDate & "\\n"
                end if
            end repeat
            return recentPhotos
        end tell
        '''
        return self.execute_script(script)

    # ===== CALENDAR =====

    def get_todays_events(self) -> str:
        """Get today's calendar events"""
        script = '''
        tell application "Calendar"
            set today to current date
            set beginning of today to time 0 of today
            set end of today to time 86400 of today
            set todayEvents to (every event of calendar 1 whose start date >= beginning of today and start date <= end of today)
            set eventList to ""
            repeat with anEvent in todayEvents
                set eventList to eventList & "Event: " & (summary of anEvent) & "\\n"
                set eventList to eventList & "Time: " & (start date of anEvent) & "\\n---\\n"
            end repeat
            return eventList
        end tell
        '''
        return self.execute_script(script)

    # ===== NOTES =====

    def search_notes(self, query: str) -> str:
        """Search Notes app"""
        script = f'''
        tell application "Notes"
            set foundNotes to (every note whose body contains "{query}")
            set noteList to ""
            repeat with aNote in foundNotes
                set noteList to noteList & "Note: " & (name of aNote) & "\\n"
                set noteList to noteList & "Content: " & (body of aNote) & "\\n---\\n"
            end repeat
            return noteList
        end tell
        '''
        return self.execute_script(script)

    def create_note(self, title: str, content: str) -> bool:
        """Create a new note"""
        script = f'''
        tell application "Notes"
            make new note at folder "Notes" with properties {{name:"{title}", body:"{content}"}}
        end tell
        '''
        result = self.execute_script(script)
        return "Error" not in result

    # ===== SYSTEM =====

    def get_active_app(self) -> str:
        """Get currently active application"""
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        return self.execute_script(script)

    def get_active_window_title(self) -> str:
        """Get title of active window"""
        script = '''
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            tell frontApp
                set windowTitle to name of front window
            end tell
            return windowTitle
        end tell
        '''
        return self.execute_script(script)
