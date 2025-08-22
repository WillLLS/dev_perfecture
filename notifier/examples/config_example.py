# Configuration d'exemple pour le système de notification
# Copiez ce fichier en config.py et remplissez avec vos vraies valeurs

from main import NotificationConfig

# Configuration Email (Gmail exemple)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email_user': 'votre_email@gmail.com',
    'email_password': 'votre_mot_de_passe_app'  # Utilisez un mot de passe d'application Gmail
}

# Configuration SMS (Twilio)
SMS_CONFIG = {
    'twilio_account_sid': 'votre_account_sid_twilio',
    'twilio_auth_token': 'votre_auth_token_twilio',
    'twilio_phone_number': '+1234567890'  # Votre numéro Twilio
}

# Configuration Telegram
TELEGRAM_CONFIG = {
    'telegram_bot_token': 'votre_bot_token_telegram'
}

# Configuration complète
def get_config():
    return NotificationConfig(
        # Email
        smtp_server=EMAIL_CONFIG['smtp_server'],
        smtp_port=EMAIL_CONFIG['smtp_port'],
        email_user=EMAIL_CONFIG['email_user'],
        email_password=EMAIL_CONFIG['email_password'],
        
        # SMS
        twilio_account_sid=SMS_CONFIG['twilio_account_sid'],
        twilio_auth_token=SMS_CONFIG['twilio_auth_token'],
        twilio_phone_number=SMS_CONFIG['twilio_phone_number'],
        
        # Telegram
        telegram_bot_token=TELEGRAM_CONFIG['telegram_bot_token']
    )

# Exemple d'utilisation avec configuration partielle (seulement email)
def get_email_only_config():
    return NotificationConfig(
        smtp_server=EMAIL_CONFIG['smtp_server'],
        smtp_port=EMAIL_CONFIG['smtp_port'],
        email_user=EMAIL_CONFIG['email_user'],
        email_password=EMAIL_CONFIG['email_password']
    )
