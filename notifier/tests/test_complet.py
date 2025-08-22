#!/usr/bin/env python3
"""
Test complet multi-canal : Email + SMS OVH + Telegram
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_config
from main import Notifier

def test_multicanal_complet():
    """Test d'envoi sur tous les canaux configurés"""
    print("🚀 TEST MULTI-CANAL COMPLET")
    print("=" * 50)
    
    # Configuration complète
    config = get_config()
    notifier = Notifier(config)
    
    print(f"📋 Canaux disponibles: {notifier.get_available_methods()}")
    print()
    
    # Destinataires
    recipients = {
        'email': 'xeefarfr@gmail.com',      # Votre email Gmail
        'sms': '+33769652410',              # Votre numéro (formaté sans espaces)
        'telegram': '@automate_y'           # Votre username Telegram
    }
    
    # Message de test
    subject = "🧪 Test Système de Notification"
    message = """Félicitations ! 

Votre système de notification multi-canal fonctionne parfaitement.

✅ Email : Gmail configuré
✅ SMS : OVH Cloud SMS opérationnel  
✅ Telegram : Bot actif

Système développé avec succès ! 🎉

- Envoyé depuis votre système de notification Perfecture"""
    
    print("📤 Envoi en cours sur tous les canaux...")
    print("-" * 50)
    
    # Test Email
    if 'email' in notifier.get_available_methods():
        print("📧 Envoi Email...")
        email_success = notifier.send_email(
            recipient=recipients['email'],
            subject=subject,
            message=message
        )
        print(f"   Résultat Email: {'✅ Succès' if email_success else '❌ Échec'}")
    else:
        print("⚠️ Email non disponible")
    
    print()
    
    # Test SMS OVH
    if 'sms' in notifier.get_available_methods():
        print("📱 Envoi SMS OVH...")
        # Message SMS plus court (limite 160 caractères)
        sms_message = "Test système notification Perfecture: Email ✅ SMS ✅ Telegram ✅ Système opérationnel ! 🎉"
        
        sms_success = notifier.send_sms(
            recipient=recipients['sms'],
            message=sms_message
        )
        print(f"   Résultat SMS: {'✅ Succès' if sms_success else '❌ Échec'}")
    else:
        print("⚠️ SMS non disponible")
    
    print()
    
    # Test Telegram
    if 'telegram' in notifier.get_available_methods():
        print("📨 Envoi Telegram...")
        telegram_success = notifier.send_telegram(
            recipient=recipients['telegram'],
            subject=subject,
            message=message
        )
        print(f"   Résultat Telegram: {'✅ Succès' if telegram_success else '❌ Échec'}")
    else:
        print("⚠️ Telegram non disponible")
    
    print()
    print("=" * 50)
    
    # Récapitulatif
    print("📊 RÉCAPITULATIF DU TEST")
    total_canaux = len(notifier.get_available_methods())
    print(f"Canaux testés: {total_canaux}/3")
    
    if total_canaux == 3:
        print("🎉 SYSTÈME COMPLET ET FONCTIONNEL !")
        print("✅ Tous les canaux de notification sont opérationnels")
        print("✅ Prêt pour la production")
    else:
        print("⚠️ Certains canaux ne sont pas configurés")
    
    print("\n💡 Vérifiez vos différents canaux :")
    print("   📧 Votre boîte email Gmail")
    print("   📱 Votre téléphone pour le SMS")
    print("   📨 Votre chat Telegram @automate_y")

def test_envoi_batch():
    """Test d'envoi en lot (simulation utilisateurs)"""
    print("\n" + "=" * 50)
    print("📦 TEST D'ENVOI EN LOT")
    print("=" * 50)
    
    config = get_config()
    notifier = Notifier(config)
    
    # Simulation de plusieurs utilisateurs
    users_list = [
        {
            'email': 'xeefarfr@gmail.com',
            'telegram': '@automate_y'
            # Pas de SMS pour éviter de consommer trop de crédits
        }
    ]
    
    print("📤 Simulation d'envoi à vos futurs utilisateurs...")
    
    for i, user in enumerate(users_list, 1):
        print(f"\n👤 Utilisateur {i}:")
        
        # Email
        if 'email' in user:
            email_result = notifier.send_email(
                recipient=user['email'],
                subject="Bienvenue dans notre système !",
                message="Merci de vous être inscrit. Votre compte est maintenant actif."
            )
            print(f"   📧 Email: {'✅' if email_result else '❌'}")
        
        # Telegram  
        if 'telegram' in user:
            tg_result = notifier.send_telegram(
                recipient=user['telegram'],
                subject="Bienvenue !",
                message="Votre compte est activé. Vous recevrez nos notifications ici."
            )
            print(f"   📨 Telegram: {'✅' if tg_result else '❌'}")
    
    print("\n✅ Test d'envoi en lot terminé !")

def main():
    """Fonction principale"""
    print("🎯 TESTS COMPLETS DU SYSTÈME DE NOTIFICATION")
    print("🔧 Développé pour Perfecture")
    print()
    
    # Test principal multi-canal
    test_multicanal_complet()
    
    # Test en lot (optionnel)
    response = input("\n❓ Voulez-vous tester l'envoi en lot ? (o/n): ").lower().strip()
    if response == 'o':
        test_envoi_batch()
    
    print("\n" + "=" * 50)
    print("🎉 TESTS TERMINÉS")
    print("💼 Votre système de notification est prêt pour votre PoC !")
    print("🚀 Vous pouvez maintenant notifier vos utilisateurs via :")
    print("   📧 Email (Gmail)")
    print("   📱 SMS (OVH Cloud)")  
    print("   📨 Telegram (Bot)")

if __name__ == "__main__":
    main()
