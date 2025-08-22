#!/usr/bin/env python3
"""
Exemple d'utilisation du système de notification
"""

from main import Notifier, NotificationConfig
from config import get_config, get_email_only_config, EMAIL_CONFIG, TELEGRAM_CONFIG

def exemple_email_simple():
    """Exemple d'envoi d'email simple"""
    print("=== Exemple Email Simple ===")
    
    # Configuration pour email uniquement (depuis config.py)
    config = get_email_only_config()
    
    # Initialisation du notificateur
    notifier = Notifier(config)
    
    # Vérification des méthodes disponibles
    print(f"Méthodes disponibles: {notifier.get_available_methods()}")
    
    # Envoi d'email de test
    success = notifier.send_email(
        recipient="xeefarfr@gmail.com",  # Votre propre email pour le test
        subject="🧪 Test de notification - Système fonctionnel !",
        message="Félicitations ! Votre système de notification par email fonctionne parfaitement. Vous recevez ce message de test depuis votre propre système de notification."
    )
    print(f"Email envoyé: {success}")

def exemple_multi_canal():
    """Exemple d'utilisation multi-canal"""
    print("\n=== Exemple Multi-Canal ===")
    
    # Configuration complète (depuis config.py)
    config = get_config()
    
    notifier = Notifier(config)
    print(f"Méthodes disponibles: {notifier.get_available_methods()}")
    
    # Exemple d'envoi multi-canal (décommentez pour tester)
    # recipients = {
    #     'email': 'user@example.com',
    #     'sms': '+33123456789',
    #     'telegram': '@username_ou_chat_id'
    # }
    # 
    # results = notifier.send_to_all(
    #     recipients=recipients,
    #     subject="Alerte système",
    #     message="Ceci est une notification de test envoyée sur tous les canaux."
    # )
    # 
    # print("Résultats des envois:")
    # for canal, success in results.items():
    #     status = "✅ Succès" if success else "❌ Échec"
    #     print(f"  {canal}: {status}")

def exemple_configuration_partielle():
    """Exemple avec configuration partielle"""
    print("\n=== Exemple Configuration Partielle ===")
    
    # Configuration avec seulement Telegram (depuis config.py)
    config = NotificationConfig(
        telegram_bot_token=TELEGRAM_CONFIG['telegram_bot_token']
    )
    
    notifier = Notifier(config)
    print(f"Méthodes disponibles: {notifier.get_available_methods()}")
    
    # Test d'envoi Telegram (décommentez pour tester)
    # success = notifier.send_telegram(
    #     recipient="@votre_username",
    #     subject="Test Telegram",
    #     message="Message de test via Telegram Bot"
    # )
    # print(f"Telegram envoyé: {success}")

def exemple_email_avec_html():
    """Exemple d'email avec contenu HTML"""
    print("\n=== Exemple Email HTML ===")
    
    # Configuration email (depuis config.py)
    config = get_email_only_config()
    
    notifier = Notifier(config)
    
    message_texte = """
    Bonjour,
    
    Ceci est un email de test avec du contenu HTML.
    
    Cordialement
    """
    
    message_html = """
    <html>
    <body>
        <h2>🎉 Email de Test</h2>
        <p>Bonjour,</p>
        <p>Ceci est un email de test avec du <strong>contenu HTML</strong>.</p>
        <ul>
            <li>✅ Support du texte enrichi</li>
            <li>✅ Support des listes</li>
            <li>✅ Support des emojis</li>
        </ul>
        <p>Cordialement</p>
    </body>
    </html>
    """
    
    # Envoi avec HTML (décommentez pour tester)
    # success = notifier.send_email(
    #     recipient="destinataire@example.com",
    #     subject="📧 Test Email HTML",
    #     message=message_texte,
    #     html_message=message_html
    # )
    # print(f"Email HTML envoyé: {success}")

def main():
    """Fonction principale avec tous les exemples"""
    print("🚀 Exemples d'utilisation du système de notification")
    print("=" * 50)
    
    # Exécution des exemples
    exemple_email_simple()
    exemple_multi_canal()
    exemple_configuration_partielle()
    exemple_email_avec_html()
    
    print("\n" + "=" * 50)
    print("📝 Note: Décommentez les lignes d'envoi après avoir configuré vos tokens/mots de passe")
    print("📖 Consultez le README.md pour plus d'informations sur la configuration")

if __name__ == "__main__":
    main()
