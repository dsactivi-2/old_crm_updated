"""
Plugin System for Mac Assistant
Allows easy extension for new apps and services
"""

from .base_plugin import BasePlugin
from .plugin_manager import PluginManager

__all__ = ['BasePlugin', 'PluginManager']
