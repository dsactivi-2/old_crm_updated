"""
Voice Controller
Handles voice input/output
"""

import subprocess
import threading
from typing import Callable


class VoiceController:
    """Main voice interface controller"""

    def __init__(self, core, on_command: Callable = None):
        self.core = core
        self.on_command = on_command

        self.listening = False
        self.speaking = False

        # Wake words
        self.wake_words = ["hey assistent", "hey assistant", "hallo assistent"]

    def start_listening(self):
        """Start continuous listening"""
        self.listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop_listening(self):
        """Stop listening"""
        self.listening = False

    def _listen_loop(self):
        """Continuous listening loop"""
        print("🎤 Voice listening started...")
        print(f"Say: {self.wake_words[0]}")

        while self.listening:
            try:
                # Use macOS speech recognition
                text = self._recognize_speech()

                if text:
                    # Check for wake word
                    if any(wake in text.lower() for wake in self.wake_words):
                        self.speak("Ja, ich höre zu")
                        # Wait for command
                        command = self._recognize_speech(timeout=10)
                        if command:
                            self._process_voice_command(command)

            except Exception as e:
                print(f"Listening error: {e}")

    def _recognize_speech(self, timeout: int = 5) -> str:
        """
        Recognize speech using macOS dictation
        Uses AppleScript to trigger dictation
        """
        try:
            # macOS native dictation via AppleScript
            script = f'''
            tell application "System Events"
                -- Trigger dictation (Fn key twice)
                -- This is a simplified version
            end tell
            '''

            # Alternative: Use Python speech_recognition library
            # For now, return placeholder
            return ""

        except Exception as e:
            print(f"Speech recognition error: {e}")
            return ""

    def speak(self, text: str):
        """
        Speak text using macOS say command
        """
        try:
            self.speaking = True

            # Use macOS native TTS (say command)
            # German voice: Anna, German female
            subprocess.run(
                ['say', '-v', 'Anna', text],
                check=True
            )

            self.speaking = False

        except Exception as e:
            print(f"TTS error: {e}")
            self.speaking = False

    def _process_voice_command(self, command: str):
        """Process voice command"""
        print(f"🎤 Voice command: {command}")

        # Speak acknowledgment
        self.speak("Verstanden")

        # Execute command
        if self.on_command:
            self.on_command(command)
        else:
            # Use core directly
            result = self.core.process_user_query(command)

            # Speak result (summarized)
            summary = self._summarize_result(result)
            self.speak(summary)

    def _summarize_result(self, result: str) -> str:
        """Summarize result for voice output"""
        # Keep it short for voice
        if len(result) > 200:
            return result[:200] + "... Siehe Dashboard für Details"
        return result

    # ===== Voice Commands =====

    def execute_voice_command(self, command: str) -> str:
        """Execute a voice command and return spoken response"""

        command_lower = command.lower()

        # Special voice commands
        if "befehle" in command_lower or "befehl" in command_lower:
            # Command mode activated
            return self._handle_command_mode(command)

        elif "status" in command_lower:
            return self._get_voice_status()

        elif "hilfe" in command_lower or "help" in command_lower:
            return self._get_voice_help()

        else:
            # Normal query
            result = self.core.process_user_query(command)
            return self._summarize_result(result)

    def _handle_command_mode(self, command: str) -> str:
        """Handle command mode - auto-execute everything"""

        # Extract actual command
        command_lower = command.lower()

        if "ich befehle dir" in command_lower:
            actual_command = command_lower.split("ich befehle dir")[1].strip()
        elif "befehl:" in command_lower:
            actual_command = command_lower.split("befehl:")[1].strip()
        else:
            actual_command = command

        print(f"⚡ COMMAND MODE: {actual_command}")

        # Execute without confirmation
        result = self.core.execute_task(actual_command)

        if result.get('success'):
            return f"Befehl ausgeführt. {result.get('result', '')}"
        else:
            return f"Fehler bei Befehlsausführung: {result.get('error', '')}"

    def _get_voice_status(self) -> str:
        """Get system status for voice"""
        plugins = len(self.core.plugin_manager.get_available_plugins())
        ai_status = "aktiv" if self.core.ai_enabled else "inaktiv"

        return f"{plugins} Plugins verfügbar. KI ist {ai_status}. System läuft normal."

    def _get_voice_help(self) -> str:
        """Get voice help"""
        return """Du kannst sagen:
        Was habe ich heute gemacht?
        Sende E-Mail an Max.
        Zeige meine Fotos.
        Ich befehle dir: Sende Nachricht.
        Status.
        """

    # ===== Advanced Voice Features =====

    def enable_continuous_listening(self):
        """Enable always-on listening mode"""
        self.start_listening()
        return "Kontinuierliches Zuhören aktiviert"

    def disable_continuous_listening(self):
        """Disable always-on listening"""
        self.stop_listening()
        return "Kontinuierliches Zuhören deaktiviert"

    def set_voice(self, voice_name: str = 'Anna'):
        """Set TTS voice"""
        self.voice = voice_name
        return f"Stimme auf {voice_name} gesetzt"
