"""
Photos.app Plugin
"""

from typing import Dict, List
from .base_plugin import MediaPlugin
import subprocess


class PhotosPlugin(MediaPlugin):
    """Plugin for macOS Photos.app"""

    def __init__(self):
        super().__init__('Photos')

    def is_available(self) -> bool:
        """Photos is always available on macOS"""
        return True

    def _execute_applescript(self, script: str) -> str:
        """Execute AppleScript"""
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search photos"""
        limit = kwargs.get('limit', 20)
        script = f'''
        tell application "Photos"
            activate
            set searchResults to search for "{query}"
            set photoList to {{}}
            repeat with aPhoto in (items 1 thru (count of searchResults) of searchResults)
                try
                    set photoInfo to {{name:(name of aPhoto), photoDate:(date of aPhoto)}}
                    set end of photoList to photoInfo
                end try
            end repeat
            return photoList
        end tell
        '''
        result = self._execute_applescript(script)
        return [{'query': query, 'results': result}]

    def get_recent_media(self, days: int = 7) -> List[Dict]:
        """Get recent photos"""
        script = f'''
        tell application "Photos"
            set cutoffDate to (current date) - ({days} * days)
            set allPhotos to every media item
            set recentPhotos to {{}}
            repeat with aPhoto in allPhotos
                if date of aPhoto > cutoffDate then
                    set photoInfo to {{name:(name of aPhoto), photoDate:(date of aPhoto)}}
                    set end of recentPhotos to photoInfo
                end if
            end repeat
            return recentPhotos
        end tell
        '''
        result = self._execute_applescript(script)
        return [{'days': days, 'photos': result}]

    def delete_media(self, media_ids: List[str]) -> bool:
        """Delete photos by name"""
        names_str = '", "'.join(media_ids)
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
        result = self._execute_applescript(script)
        return "Error" not in result

    def execute_action(self, action: str, **params) -> Dict:
        """Execute Photos-specific actions"""
        if action == 'create_album':
            album_name = params.get('album_name', '')
            return self._create_album(album_name)

        elif action == 'add_to_favorites':
            photo_names = params.get('photo_names', [])
            return self._add_to_favorites(photo_names)

        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def _create_album(self, album_name: str) -> Dict:
        """Create a new album"""
        script = f'''
        tell application "Photos"
            make new album named "{album_name}"
        end tell
        '''
        result = self._execute_applescript(script)
        return {'status': 'success' if 'Error' not in result else 'error', 'message': result}

    def _add_to_favorites(self, photo_names: List[str]) -> Dict:
        """Add photos to favorites"""
        names_str = '", "'.join(photo_names)
        script = f'''
        tell application "Photos"
            set photoNames to {{"{names_str}"}}
            repeat with photoName in photoNames
                set foundPhotos to search for photoName
                repeat with aPhoto in foundPhotos
                    set favorite of aPhoto to true
                end repeat
            end repeat
        end tell
        '''
        result = self._execute_applescript(script)
        return {'status': 'success' if 'Error' not in result else 'error'}
