#!/usr/bin/env python3
"""
Package scraper - Outils pour scraper les préfectures
"""

# Imports principaux pour faciliter l'utilisation
from .browser_proxied import BrowserProxied
from .config import ChromeConfig, create_driver, get_config, visible_config, stealth_config

# Version du package
__version__ = "1.0.0"

# Exports principaux
__all__ = [
    'BrowserProxied',
    'ChromeConfig', 
    'create_driver',
    'get_config',
    'visible_config', 
    'stealth_config'
]
