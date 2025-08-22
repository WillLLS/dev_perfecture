#!/usr/bin/env python3
"""
Package notifier - Outils pour notifier les utilisateurs des résultats de scraping
"""

# Imports principaux pour faciliter l'utilisation
from .notifier import Notifier, NotificationConfig
from .config import get_config, get_email_only_config, get_telegram_only_config

# Version du package
__version__ = "1.0.0"


