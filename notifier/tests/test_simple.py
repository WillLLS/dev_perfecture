#!/usr/bin/env python3
"""
Test simple et rapide des 3 canaux
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config
from main import Notifier

def test_simple_multi_canal():
    """Test simple de tous les canaux"""
    
    print("🚀 TEST SIMPLE MULTI-CANAL")
    print("=" * 50)
    
    # Configuration
    config = get_config()
    
    # Initialisation
    print("📋 Initialisation du notificateur...")
    notifier = Notifier(config)
    
    print(f"✅ Canaux disponibles: {notifier.get_available_methods()}")
    
    # Destinataires
    recipients = {
        'email': 'xeefarfr@gmail.com',  # Votre email
        'sms': '+33769652410',          # Votre numéro
        'telegram': '6534222555'        # Votre Chat ID
    }
    
    # Message de test
    subject = "🎉 Test Système Perfecture"
    message = "Votre système de notification multi-canal fonctionne parfaitement !"
    
    print(f"\n📤 ENVOI EN COURS...")
    print(f"📧 Email: {recipients['email']}")
    print(f"📱 SMS: {recipients['sms']}")
    print(f"💬 Telegram: {recipients['telegram']}")
    
    # Test séquentiel pour voir les erreurs éventuelles
    results = {}
    
    # 1. Test Email
    print(f"\n1️⃣ Test Email...")
    try:
        results['email'] = notifier.send_email(recipients['email'], subject, message)
        print(f"📧 Email: {'✅ Succès' if results['email'] else '❌ Échec'}")
    except Exception as e:
        print(f"📧 Email: ❌ Erreur - {e}")
        results['email'] = False
    
    # 2. Test SMS
    print(f"\n2️⃣ Test SMS...")
    try:
        results['sms'] = notifier.send_sms(recipients['sms'], message)
        print(f"📱 SMS: {'✅ Succès' if results['sms'] else '❌ Échec'}")
    except Exception as e:
        print(f"📱 SMS: ❌ Erreur - {e}")
        results['sms'] = False
    
    # 3. Test Telegram
    print(f"\n3️⃣ Test Telegram...")
    try:
        results['telegram'] = notifier.send_telegram(recipients['telegram'], subject, message)
        print(f"💬 Telegram: {'✅ Succès' if results['telegram'] else '❌ Échec'}")
    except Exception as e:
        print(f"💬 Telegram: ❌ Erreur - {e}")
        results['telegram'] = False
    
    # Résumé
    print(f"\n" + "=" * 50)
    print(f"📊 RÉSUMÉ DES TESTS")
    print(f"=" * 50)
    
    success_count = sum(results.values())
    total_count = len(results)
    
    for channel, success in results.items():
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"{channel.upper():>10}: {status}")
    
    print(f"\n🎯 Score: {success_count}/{total_count} canaux fonctionnels")
    
    if success_count == total_count:
        print(f"🎉 FÉLICITATIONS ! Votre système de notification est 100% opérationnel !")
        print(f"📧 Vérifiez votre email")
        print(f"📱 Vérifiez vos SMS")
        print(f"💬 Vérifiez Telegram")
    else:
        print(f"⚠️ Certains canaux nécessitent des ajustements")

if __name__ == "__main__":
    test_simple_multi_canal()
