"""
Setup script for creating native macOS app with py2app
Usage: python3 setup_py2app.py py2app
"""

from setuptools import setup

APP = ['launcher.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['anthropic', 'tkinter'],
    'includes': [
        'mac_assistant.core_v2',
        'mac_assistant.ui.dashboard',
        'mac_assistant.plugins',
        'mac_assistant.tasks',
        'mac_assistant.database',
        'mac_assistant.utils',
        'mac_assistant.scripts',
    ],
    'excludes': ['matplotlib', 'numpy', 'scipy'],
    'plist': {
        'CFBundleName': 'Mac Remote Assistant',
        'CFBundleDisplayName': 'Mac Remote Assistant',
        'CFBundleGetInfoString': 'AI-powered Mac automation assistant',
        'CFBundleIdentifier': 'com.macassistant.app',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0',
        'NSHumanReadableCopyright': 'MIT License',
        'NSAppleEventsUsageDescription': 'Diese App benötigt Zugriff auf andere Apps um sie zu steuern.',
        'NSSystemAdministrationUsageDescription': 'Diese App benötigt Administratorrechte für bestimmte Funktionen.',
    }
}

setup(
    name='Mac Remote Assistant',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
