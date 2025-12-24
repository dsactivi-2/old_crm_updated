"""
Setup script for creating native macOS app with py2app
Usage: python3 setup_py2app.py py2app
"""

from setuptools import setup

APP = ['launcher.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['anthropic', 'tkinter', 'mac_assistant'],
    'includes': [
        'mac_assistant',
        'mac_assistant.core_v2',
        'mac_assistant.core',
        'mac_assistant.main',
        'mac_assistant.ui',
        'mac_assistant.ui.dashboard',
        'mac_assistant.plugins',
        'mac_assistant.plugins.base',
        'mac_assistant.plugins.mail',
        'mac_assistant.plugins.slack',
        'mac_assistant.plugins.viber',
        'mac_assistant.plugins.telegram',
        'mac_assistant.plugins.photos',
        'mac_assistant.tasks',
        'mac_assistant.tasks.executor',
        'mac_assistant.tasks.nlp_parser',
        'mac_assistant.database',
        'mac_assistant.database.activity_tracker',
        'mac_assistant.database.time_travel',
        'mac_assistant.utils',
        'mac_assistant.utils.claude',
        'mac_assistant.scripts',
        'mac_assistant.autonomous',
        'mac_assistant.voice',
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
