# Configuration du système de notification
# Généré automatiquement le 2025-07-19 16:39:39

from notifier import NotificationConfig

# Configuration Email
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email_user': 'xeefarfr@gmail.com',
    'email_password': 'zavz gelq zkbm tenx'
}

# Configuration SMS (OVH Cloud SMS)
SMS_CONFIG = {
    'ovh_application_key': 'c0263c18e17d2010',
    'ovh_application_secret': '6bae8a30c58fe3cc60dfd2d171486e18',
    'ovh_consumer_key': '174c9193549f42ea01dad32e3feebfe4',
    'ovh_service_name': 'sms-lw62033-1',  # Nom de votre service SMS OVH
    'ovh_sender': None  # Utiliser le numéro court par défaut d'OVH (pas de sender personnalisé)
}

# Configuration Telegram
TELEGRAM_CONFIG = {
    'telegram_bot_token': '8025520370:AAHQN-YXBMx3mo_Nu1LuY0VkEVyDBtnJnL0',
    'telegram_chat_id': '6534222555'
}

def get_config():
    """Configuration complète"""
    return NotificationConfig(
        # Email
        smtp_server=EMAIL_CONFIG['smtp_server'],
        smtp_port=EMAIL_CONFIG['smtp_port'],
        email_user=EMAIL_CONFIG['email_user'],
        email_password=EMAIL_CONFIG['email_password'],
        
        # SMS OVH
        ovh_application_key=SMS_CONFIG['ovh_application_key'],
        ovh_application_secret=SMS_CONFIG['ovh_application_secret'],
        ovh_consumer_key=SMS_CONFIG['ovh_consumer_key'],
        ovh_service_name=SMS_CONFIG['ovh_service_name'],
        ovh_sender=SMS_CONFIG['ovh_sender'],
        
        # Telegram
        telegram_bot_token=TELEGRAM_CONFIG['telegram_bot_token'],
        telegram_chat_id=TELEGRAM_CONFIG['telegram_chat_id']
    )

def get_email_only_config():
    """Configuration email seulement"""
    return NotificationConfig(
        smtp_server=EMAIL_CONFIG['smtp_server'],
        smtp_port=EMAIL_CONFIG['smtp_port'],
        email_user=EMAIL_CONFIG['email_user'],
        email_password=EMAIL_CONFIG['email_password']
    )

def get_telegram_only_config():
    """Configuration Telegram seulement"""
    return NotificationConfig(
        telegram_bot_token=TELEGRAM_CONFIG['telegram_bot_token'],
        telegram_chat_id=TELEGRAM_CONFIG['telegram_chat_id']
    )
