# How to Add New Plugins

Diese Anleitung zeigt, wie du neue App-Integrationen zur Mac Assistant App hinzufügst.

## Schritt 1: Plugin-Datei erstellen

1. Kopiere `plugins/PLUGIN_TEMPLATE.py`
2. Benenne sie um (z.B. `whatsapp_plugin.py`, `discord_plugin.py`, etc.)

```bash
cd mac_assistant/plugins
cp PLUGIN_TEMPLATE.py whatsapp_plugin.py
```

## Schritt 2: Plugin anpassen

Öffne deine neue Plugin-Datei und passe sie an:

### 2.1 Wähle die richtige Basis-Klasse

```python
from .base_plugin import MessagingPlugin, EmailPlugin, MediaPlugin, ProductivityPlugin

# Für Chat-Apps:
class WhatsAppPlugin(MessagingPlugin):
    def __init__(self):
        super().__init__('WhatsApp')

# Für E-Mail-Apps:
class OutlookPlugin(EmailPlugin):
    def __init__(self):
        super().__init__('Outlook')

# Für Foto/Video-Apps:
class LightroomPlugin(MediaPlugin):
    def __init__(self):
        super().__init__('Lightroom')

# Für Produktivitäts-Apps:
class NotionPlugin(ProductivityPlugin):
    def __init__(self):
        super().__init__('Notion')
```

### 2.2 Implementiere `is_available()`

```python
def is_available(self) -> bool:
    """Check if app is installed"""
    return os.path.exists('/Applications/WhatsApp.app')
```

### 2.3 Implementiere die Hauptfunktionen

Je nach Basis-Klasse musst du verschiedene Methoden implementieren:

#### Für MessagingPlugin:

```python
def read_messages(self, limit: int = 10) -> List[Dict]:
    """Get recent messages"""
    script = '''
    tell application "WhatsApp"
        -- AppleScript zum Lesen von Nachrichten
    end tell
    '''
    result = self._execute_applescript(script)
    return [{'raw': result}]

def send_message(self, recipient: str, message: str, **kwargs) -> bool:
    """Send a message"""
    script = f'''
    tell application "WhatsApp"
        -- AppleScript zum Senden
    end tell
    '''
    result = self._execute_applescript(script)
    return "Error" not in result

def search(self, query: str, **kwargs) -> List[Dict]:
    """Search messages"""
    # Implementierung
    pass
```

#### Für EmailPlugin:

```python
def get_unread_emails(self, limit: int = 10) -> List[Dict]:
    """Get unread emails"""
    pass

def send_email(self, to: str, subject: str, body: str, **kwargs) -> bool:
    """Send email"""
    pass

def reply_to_email(self, email_id: str, reply_body: str) -> bool:
    """Reply to email"""
    pass
```

## Schritt 3: AppleScript-Integration

Die meisten macOS-Apps können über AppleScript gesteuert werden:

### 3.1 Teste AppleScript-Befehle

Öffne **Script Editor** (im /Applications/Utilities Ordner) und teste:

```applescript
tell application "WhatsApp"
    activate
end tell

tell application "System Events"
    tell process "WhatsApp"
        -- UI-Elemente auslesen
        get entire contents
    end tell
end tell
```

### 3.2 Integriere in Plugin

```python
def _execute_applescript(self, script: str) -> str:
    """Execute AppleScript"""
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"
```

## Schritt 4: Custom Actions hinzufügen

Für app-spezifische Funktionen:

```python
def execute_action(self, action: str, **params) -> Dict:
    """Execute custom actions"""

    if action == 'create_group':
        name = params.get('name')
        members = params.get('members', [])
        return self._create_group(name, members)

    elif action == 'set_status':
        status = params.get('status')
        return self._set_status(status)

    return {'status': 'error', 'message': f'Unknown action: {action}'}

def _create_group(self, name: str, members: List[str]) -> Dict:
    """Create a group chat"""
    # Implementierung
    return {'status': 'success', 'group_id': '...'}

def _set_status(self, status: str) -> Dict:
    """Set user status"""
    # Implementierung
    return {'status': 'success'}
```

## Schritt 5: Plugin registrieren

Öffne `core_v2.py` und füge dein Plugin hinzu:

```python
# 1. Import hinzufügen (oben in der Datei)
from mac_assistant.plugins.whatsapp_plugin import WhatsAppPlugin

# 2. In _register_plugins() registrieren
def _register_plugins(self):
    # ... existing plugins ...

    # Your new plugin
    self.plugin_manager.register(WhatsAppPlugin())
```

## Schritt 6: Testen

```python
# Test in Python
from mac_assistant.core_v2 import MacAssistantCore

core = MacAssistantCore()

# Check if plugin is available
plugin = core.get_plugin('WhatsApp')
print(plugin.is_available())

# Test functionality
plugin.send_message('Max', 'Hello from plugin!')

# Or use task executor
result = core.execute_task("Sende WhatsApp Nachricht an Max: Hallo!")
print(result)
```

## Beispiel: WhatsApp Plugin

```python
from typing import Dict, List
from .base_plugin import MessagingPlugin
import subprocess
import os


class WhatsAppPlugin(MessagingPlugin):
    """Plugin for WhatsApp Desktop"""

    def __init__(self):
        super().__init__('WhatsApp')

    def is_available(self) -> bool:
        return os.path.exists('/Applications/WhatsApp.app')

    def _execute_applescript(self, script: str) -> str:
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def read_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages"""
        script = '''
        tell application "WhatsApp"
            activate
        end tell

        tell application "System Events"
            tell process "WhatsApp"
                return "WhatsApp is active"
            end tell
        end tell
        '''
        result = self._execute_applescript(script)
        return [{'info': result}]

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        """Send message via keyboard automation"""
        script = f'''
        tell application "WhatsApp"
            activate
        end tell

        delay 0.5

        tell application "System Events"
            tell process "WhatsApp"
                -- Search for contact
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
        """Search in WhatsApp"""
        script = f'''
        tell application "WhatsApp"
            activate
        end tell

        tell application "System Events"
            tell process "WhatsApp"
                keystroke "f" using command down
                delay 0.3
                keystroke "{query}"
            end tell
        end tell
        '''
        self._execute_applescript(script)
        return [{'status': 'Search initiated'}]
```

## Tipps & Best Practices

### 1. **Fehlerbehandlung**

```python
def send_message(self, recipient: str, message: str, **kwargs) -> bool:
    try:
        result = self._execute_applescript(script)

        if "Error" in result:
            print(f"AppleScript error: {result}")
            return False

        return True

    except Exception as e:
        print(f"Exception in send_message: {e}")
        return False
```

### 2. **Logging**

```python
def send_message(self, recipient: str, message: str, **kwargs) -> bool:
    print(f"[{self.name}] Sending to {recipient}: {message}")

    result = self._execute_applescript(script)

    if "Error" not in result:
        print(f"[{self.name}] Message sent successfully")
        return True
    else:
        print(f"[{self.name}] Failed: {result}")
        return False
```

### 3. **Timeouts**

```python
result = subprocess.run(
    ['osascript', '-e', script],
    capture_output=True,
    text=True,
    timeout=30  # Timeout nach 30 Sekunden
)
```

### 4. **Delays für UI-Automation**

```python
tell application "System Events"
    tell process "MyApp"
        keystroke "f" using command down
        delay 0.3  -- Warte 300ms
        keystroke "search query"
        delay 0.5  -- Warte 500ms
        keystroke return
    end tell
end tell
```

## Web API Alternative

Wenn die App eine Web-API hat, ist das oft besser als AppleScript:

```python
import requests


class SlackPlugin(MessagingPlugin):
    def __init__(self, api_token: str = None):
        super().__init__('Slack')
        self.api_token = api_token or os.getenv('SLACK_API_TOKEN')
        self.base_url = 'https://slack.com/api'

    def send_message(self, recipient: str, message: str, **kwargs) -> bool:
        """Send via Slack API"""
        url = f'{self.base_url}/chat.postMessage'
        headers = {'Authorization': f'Bearer {self.api_token}'}
        data = {
            'channel': recipient,
            'text': message
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json().get('ok', False)
```

## Debugging

### 1. Test AppleScript separat

```bash
osascript -e 'tell application "WhatsApp" to activate'
```

### 2. Check Berechtigungen

Systemeinstellungen > Sicherheit > Datenschutz > Automation

### 3. Verbose Output

```python
def _execute_applescript(self, script: str) -> str:
    print(f"Executing AppleScript:\n{script}")

    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output=True,
        text=True
    )

    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")

    return result.stdout.strip()
```

## Fertig! 🎉

Dein Plugin ist jetzt einsatzbereit. Nutzer können es verwenden via:

```python
# Natural language
"Sende eine Nachricht über WhatsApp an Max: Hallo!"

# Task execution
core.execute_task("send WhatsApp message to Max: Hello!")

# Direct API
plugin = core.get_plugin('WhatsApp')
plugin.send_message('Max', 'Hello!')
```
