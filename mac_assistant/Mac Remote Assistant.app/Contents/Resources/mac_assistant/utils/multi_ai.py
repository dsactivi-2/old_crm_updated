"""
Multi-AI Provider Support
Supports Claude, ChatGPT (OpenAI), and Grok (xAI)
"""

import os
from typing import Optional, Dict
import anthropic


class MultiAIProvider:
    """Unified interface for multiple AI providers"""

    def __init__(self):
        self.providers = {}
        self._init_providers()
        self.active_provider = 'claude'  # Default

    def _init_providers(self):
        """Initialize all available AI providers"""

        # Claude (Anthropic)
        claude_key = os.getenv('ANTHROPIC_API_KEY')
        if claude_key:
            self.providers['claude'] = ClaudeProvider(claude_key)

        # ChatGPT (OpenAI)
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.providers['chatgpt'] = ChatGPTProvider(openai_key)

        # Grok (xAI)
        grok_key = os.getenv('XAI_API_KEY') or os.getenv('GROK_API_KEY')
        if grok_key:
            self.providers['grok'] = GrokProvider(grok_key)

    def query(self, prompt: str, provider: str = None, **kwargs) -> str:
        """Query AI provider"""
        provider_name = provider or self.active_provider

        if provider_name not in self.providers:
            return f"❌ Provider '{provider_name}' nicht verfügbar. Setze API Key."

        try:
            return self.providers[provider_name].query(prompt, **kwargs)
        except Exception as e:
            return f"❌ Fehler bei {provider_name}: {str(e)}"

    def set_active_provider(self, provider: str):
        """Set active AI provider"""
        if provider in self.providers:
            self.active_provider = provider
            return f"✓ Aktiver Provider: {provider}"
        return f"❌ Provider '{provider}' nicht verfügbar"

    def get_available_providers(self) -> list:
        """Get list of available providers"""
        return list(self.providers.keys())

    def add_provider_key(self, provider: str, api_key: str):
        """Add API key for a provider"""
        if provider == 'claude':
            self.providers['claude'] = ClaudeProvider(api_key)
        elif provider == 'chatgpt':
            self.providers['chatgpt'] = ChatGPTProvider(api_key)
        elif provider == 'grok':
            self.providers['grok'] = GrokProvider(api_key)


class ClaudeProvider:
    """Claude (Anthropic) provider"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def query(self, prompt: str, **kwargs) -> str:
        """Query Claude API"""
        max_tokens = kwargs.get('max_tokens', 2048)
        system = kwargs.get('system', '')

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system if system else None,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text


class ChatGPTProvider:
    """ChatGPT (OpenAI) provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gpt-4-turbo-preview"

        # Try to import openai
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.available = True
        except ImportError:
            print("⚠️  OpenAI package not installed. Run: pip install openai")
            self.available = False

    def query(self, prompt: str, **kwargs) -> str:
        """Query OpenAI API"""
        if not self.available:
            return "❌ OpenAI package nicht installiert. Run: pip install openai"

        max_tokens = kwargs.get('max_tokens', 2048)
        system = kwargs.get('system', 'You are a helpful AI assistant.')

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )

        return response.choices[0].message.content


class GrokProvider:
    """Grok (xAI) provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "grok-beta"
        self.base_url = "https://api.x.ai/v1"

        # xAI uses OpenAI-compatible API
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=self.base_url
            )
            self.available = True
        except ImportError:
            print("⚠️  OpenAI package needed for Grok. Run: pip install openai")
            self.available = False

    def query(self, prompt: str, **kwargs) -> str:
        """Query Grok API"""
        if not self.available:
            return "❌ OpenAI package nicht installiert (für Grok benötigt)"

        max_tokens = kwargs.get('max_tokens', 2048)
        system = kwargs.get('system', 'You are Grok, a helpful AI assistant.')

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )

        return response.choices[0].message.content


# ===== Convenience Functions =====

def ask_claude(prompt: str, api_key: str = None) -> str:
    """Quick Claude query"""
    key = api_key or os.getenv('ANTHROPIC_API_KEY')
    provider = ClaudeProvider(key)
    return provider.query(prompt)


def ask_chatgpt(prompt: str, api_key: str = None) -> str:
    """Quick ChatGPT query"""
    key = api_key or os.getenv('OPENAI_API_KEY')
    provider = ChatGPTProvider(key)
    return provider.query(prompt)


def ask_grok(prompt: str, api_key: str = None) -> str:
    """Quick Grok query"""
    key = api_key or os.getenv('XAI_API_KEY', os.getenv('GROK_API_KEY'))
    provider = GrokProvider(key)
    return provider.query(prompt)


def ask_all(prompt: str) -> Dict[str, str]:
    """Ask all available providers"""
    multi = MultiAIProvider()
    results = {}

    for provider in multi.get_available_providers():
        results[provider] = multi.query(prompt, provider=provider)

    return results
