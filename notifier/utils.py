#!/usr/bin/env python3
"""
Utilitaires pour le système de notification
"""

import os
from typing import Dict, Any
from main import NotificationConfig

def load_config_from_env() -> NotificationConfig:
    """
    Charge la configuration depuis les variables d'environnement
    Utile pour les déploiements en production
    """
    return NotificationConfig(
        # Email
        smtp_server=os.getenv('SMTP_SERVER'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        email_user=os.getenv('EMAIL_USER'),
        email_password=os.getenv('EMAIL_PASSWORD'),
        
        # SMS OVH
        ovh_application_key=os.getenv('OVH_APPLICATION_KEY'),
        ovh_application_secret=os.getenv('OVH_APPLICATION_SECRET'),
        ovh_consumer_key=os.getenv('OVH_CONSUMER_KEY'),
        ovh_service_name=os.getenv('OVH_SERVICE_NAME'),
        ovh_sender=os.getenv('OVH_SENDER'),
        
        # Telegram
        telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID')
    )

def validate_email(email: str) -> bool:
    """Validation basique d'une adresse email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    """Validation basique d'un numéro de téléphone international"""
    import re
    # Format international +[code pays][numéro]
    pattern = r'^\+[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def format_message_for_sms(message: str, max_length: int = 160) -> str:
    """
    Formate un message pour SMS en respectant la limite de caractères
    Tronque si nécessaire et ajoute ...
    """
    if len(message) <= max_length:
        return message
    
    return message[:max_length-3] + "..."

def create_html_template(title: str, content: str, footer: str = "") -> str:
    """
    Crée un template HTML simple pour les emails
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #f4f4f4;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
            }}
            .content {{
                padding: 20px;
                background-color: #fff;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 0.9em;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="content">
            {content}
        </div>
        <div class="footer">
            {footer}
        </div>
    </body>
    </html>
    """

def log_notification_attempt(method: str, recipient: str, subject: str, success: bool):
    """
    Log basique des tentatives de notification
    En production, utilisez un vrai système de logging
    """
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILED"
    
    log_entry = f"[{timestamp}] {method.upper()} to {recipient} - {subject} - {status}"
    
    # Écriture dans un fichier de log
    with open("notifications.log", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    
    print(log_entry)

def get_telegram_chat_id_from_username(bot_token: str, username: str) -> str:
    """
    Utilitaire pour récupérer le chat_id d'un utilisateur Telegram
    Note: L'utilisateur doit avoir envoyé au moins un message au bot
    """
    import requests
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            for update in data.get('result', []):
                if 'message' in update:
                    from_user = update['message']['from']
                    if from_user.get('username', '').lower() == username.lower().replace('@', ''):
                        return str(from_user['id'])
            
            print(f"❌ Utilisateur {username} non trouvé dans les messages récents")
            return ""
        else:
            print(f"❌ Erreur API Telegram: {response.text}")
            return ""
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du chat_id: {e}")
        return ""

def batch_send_notifications(notifier, recipients_list: list, subject: str, message: str) -> Dict[str, int]:
    """
    Envoi en lot de notifications
    
    Args:
        notifier: Instance de la classe Notifier
        recipients_list: Liste de dictionnaires avec les destinataires
        subject: Sujet des notifications
        message: Message à envoyer
    
    Returns:
        Dict avec les statistiques d'envoi
    """
    stats = {
        'total': len(recipients_list),
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    for i, recipients in enumerate(recipients_list, 1):
        print(f"📤 Envoi {i}/{stats['total']}...")
        
        try:
            results = notifier.send_to_all(recipients, subject, message)
            
            # Comptage des succès/échecs
            batch_success = all(results.values()) if results else False
            
            if batch_success:
                stats['success'] += 1
            else:
                stats['failed'] += 1
            
            stats['details'].append({
                'recipients': recipients,
                'results': results,
                'overall_success': batch_success
            })
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi à {recipients}: {e}")
            stats['failed'] += 1
            stats['details'].append({
                'recipients': recipients,
                'error': str(e),
                'overall_success': False
            })
    
    print(f"\n📊 Statistiques d'envoi:")
    print(f"  Total: {stats['total']}")
    print(f"  Succès: {stats['success']}")
    print(f"  Échecs: {stats['failed']}")
    print(f"  Taux de réussite: {(stats['success']/stats['total']*100):.1f}%")
    
    return stats

# Exemple d'utilisation des utilitaires
if __name__ == "__main__":
    print("🛠️ Utilitaires du système de notification")
    
    # Test de validation
    print(f"📧 Email valide: {validate_email('test@example.com')}")
    print(f"📧 Email invalide: {validate_email('invalid-email')}")
    
    print(f"📱 Téléphone valide: {validate_phone_number('+33123456789')}")
    print(f"📱 Téléphone invalide: {validate_phone_number('123456789')}")
    
    # Test de formatage SMS
    long_message = "Ceci est un très long message qui dépasse largement la limite de 160 caractères d'un SMS standard et qui devrait être tronqué automatiquement."
    print(f"📱 Message SMS formaté: {format_message_for_sms(long_message)}")
    
    # Test de template HTML
    html = create_html_template(
        title="Test de Template",
        content="<p>Ceci est un test du template HTML.</p>",
        footer="Envoyé par le système de notification"
    )
    print(f"📧 Template HTML créé ({len(html)} caractères)")
