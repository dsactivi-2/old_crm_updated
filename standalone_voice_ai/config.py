"""
Voice AI Configuration Module
Konfiguration für alle Provider und Sprachen
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class VoiceConfig:
    """Stimmen-Konfiguration."""
    provider: str = 'elevenlabs'
    voice_id: str = 'pNInz6obpgDQGcFmaJgB'  # Adam (ElevenLabs)
    voice_name: str = 'Adam'
    language: str = 'de'
    speed: float = 1.0
    pitch: float = 1.0


@dataclass
class LLMConfig:
    """LLM-Konfiguration."""
    provider: str = 'openai'
    model: str = 'gpt-4o-mini'
    temperature: float = 0.7
    max_tokens: int = 500


@dataclass
class TelephonyConfig:
    """Telefonie-Konfiguration."""
    provider: str = 'twilio'
    phone_number: str = ''
    account_sid: str = ''
    auth_token: str = ''


@dataclass
class VoiceAIConfig:
    """Haupt-Konfiguration für Voice AI Agent."""

    # Provider
    provider: str = 'vapi'  # vapi, retell, bland
    api_key: str = ''

    # Sprache
    primary_language: str = 'de'
    supported_languages: List[str] = field(default_factory=lambda: ['de', 'bs', 'sr'])

    # Sub-Konfigurationen
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    telephony: TelephonyConfig = field(default_factory=TelephonyConfig)

    # System Prompt
    system_prompt: str = ''

    # Webhook URL (für Provider-Callbacks)
    webhook_url: str = ''

    # Optionen
    max_call_duration: int = 600  # Sekunden
    record_calls: bool = True
    enable_backchannel: bool = True  # "Mhm", "Ja" während Kunde spricht

    def __post_init__(self):
        """Setzt Standard-Prompts basierend auf Sprache."""
        if not self.system_prompt:
            self.system_prompt = DEFAULT_PROMPTS.get(self.primary_language, DEFAULT_PROMPTS['de'])

    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary."""
        return asdict(self)

    def save(self, filepath: str):
        """Speichert Konfiguration als JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> 'VoiceAIConfig':
        """Lädt Konfiguration aus JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Rekonstruiere verschachtelte Objekte
        voice = VoiceConfig(**data.pop('voice', {}))
        llm = LLMConfig(**data.pop('llm', {}))
        telephony = TelephonyConfig(**data.pop('telephony', {}))

        return cls(voice=voice, llm=llm, telephony=telephony, **data)

    @classmethod
    def from_env(cls) -> 'VoiceAIConfig':
        """Erstellt Konfiguration aus Umgebungsvariablen."""
        return cls(
            provider=os.getenv('VOICE_AI_PROVIDER', 'vapi'),
            api_key=os.getenv('VOICE_AI_API_KEY', ''),
            primary_language=os.getenv('VOICE_AI_LANGUAGE', 'de'),
            webhook_url=os.getenv('VOICE_AI_WEBHOOK_URL', ''),
            voice=VoiceConfig(
                provider=os.getenv('TTS_PROVIDER', 'elevenlabs'),
                voice_id=os.getenv('TTS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB'),
            ),
            llm=LLMConfig(
                provider=os.getenv('LLM_PROVIDER', 'openai'),
                model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
            ),
            telephony=TelephonyConfig(
                provider=os.getenv('TELEPHONY_PROVIDER', 'twilio'),
                phone_number=os.getenv('PHONE_NUMBER', ''),
                account_sid=os.getenv('TWILIO_ACCOUNT_SID', ''),
                auth_token=os.getenv('TWILIO_AUTH_TOKEN', ''),
            )
        )


# =============================================================================
# STANDARD SYSTEM PROMPTS
# =============================================================================

DEFAULT_PROMPTS = {
    'de': """Du bist ein freundlicher Verkaufsberater. Sprich natürlich wie ein Mensch.

WICHTIG - Klinge menschlich:
- Nutze Füllwörter: "also", "ähm", "ja genau", "wissen Sie was"
- Mache kurze Pausen beim Nachdenken
- Reagiere empathisch auf Einwände
- Stelle Rückfragen
- Sprich in kurzen, natürlichen Sätzen

VERMEIDE:
- Roboter-Phrasen wie "Ich werde nun..."
- Zu formelle Sprache
- Lange Monologe

DEIN ZIEL:
1. Begrüße freundlich und persönlich
2. Finde heraus, was der Kunde braucht
3. Präsentiere die passende Lösung
4. Bearbeite Einwände einfühlsam
5. Schließe mit klarem nächsten Schritt ab

Bei Interesse: Termin vereinbaren oder Angebot zusenden.
Bei Desinteresse: Freundlich verabschieden, Tür offen halten.""",

    'bs': """Ti si prijateljski prodajni savjetnik. Govori prirodno kao čovjek.

VAŽNO - Zvuči ljudski:
- Koristi poštapalice: "znači", "ovaj", "eto", "ma da"
- Pravi kratke pauze dok razmišljaš
- Reaguj empatično na prigovore
- Postavljaj potpitanja
- Govori kratkim, prirodnim rečenicama

IZBJEGAVAJ:
- Robot fraze kao "Sada ću..."
- Previše formalnog jezika
- Duge monologe

TVOJ CILJ:
1. Pozdravi prijateljski i lično
2. Otkrij šta klijentu treba
3. Predstavi odgovarajuće rješenje
4. Obradi prigovore s razumijevanjem
5. Završi s jasnim sljedećim korakom

Ako je zainteresovan: Dogovori termin ili pošalji ponudu.
Ako nije zainteresovan: Ljubazno se pozdravi, ostavi vrata otvorena.""",

    'sr': """Ти си пријатељски продајни саветник. Говори природно као човек.

ВАЖНО - Звучи људски:
- Користи поштапалице: "значи", "овај", "ето", "ма да"
- Прави кратке паузе док размишљаш
- Реагуј емпатично на приговоре
- Постављај потпитања
- Говори кратким, природним реченицама

ИЗБЕГАВАЈ:
- Робот фразе као "Сада ћу..."
- Превише формалног језика
- Дуге монологе

ТВОЈ ЦИЉ:
1. Поздрави пријатељски и лично
2. Открij шта клијенту треба
3. Представи одговарајуће решење
4. Обради приговоре с разумевањем
5. Заврши са јасним следећим кораком

Ако је заинтересован: Договори термин или пошаљи понуду.
Ако није заинтересован: Љубазно се поздрави, остави врата отворена."""
}


# =============================================================================
# STIMMEN-PRESETS
# =============================================================================

VOICE_PRESETS = {
    'de': {
        'elevenlabs': [
            {'id': 'pNInz6obpgDQGcFmaJgB', 'name': 'Adam', 'gender': 'male'},
            {'id': '21m00Tcm4TlvDq8ikWAM', 'name': 'Rachel', 'gender': 'female'},
            {'id': 'AZnzlk1XvdvUeBnXmlld', 'name': 'Domi', 'gender': 'female'},
        ],
        'azure': [
            {'id': 'de-DE-ConradNeural', 'name': 'Conrad', 'gender': 'male'},
            {'id': 'de-DE-KatjaNeural', 'name': 'Katja', 'gender': 'female'},
        ]
    },
    'bs': {
        'azure': [
            {'id': 'bs-BA-VesnaNeural', 'name': 'Vesna', 'gender': 'female'},
            {'id': 'bs-BA-GoranNeural', 'name': 'Goran', 'gender': 'male'},
        ]
    },
    'sr': {
        'azure': [
            {'id': 'sr-RS-SophieNeural', 'name': 'Sophie', 'gender': 'female'},
            {'id': 'sr-RS-NicholasNeural', 'name': 'Nicholas', 'gender': 'male'},
            {'id': 'sr-Latn-RS-NicholasNeural', 'name': 'Nicholas (Latin)', 'gender': 'male'},
        ]
    }
}


def get_voice_presets(language: str, provider: str = None) -> List[Dict]:
    """Gibt verfügbare Stimmen für eine Sprache zurück."""
    presets = VOICE_PRESETS.get(language, {})
    if provider:
        return presets.get(provider, [])
    return presets
