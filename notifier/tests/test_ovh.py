#!/usr/bin/env python3
"""
Test spécifique OVH SMS avec la bibliothèque officielle
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_config, SMS_CONFIG
from main import OVHSMSNotifier, NotificationConfig

def test_ovh_connection():
    """Test de connexion OVH"""
    print("🧪 Test de connexion OVH SMS")
    print("=" * 40)
    
    try:
        # Configuration OVH seulement
        config = NotificationConfig(
            ovh_application_key=SMS_CONFIG['ovh_application_key'],
            ovh_application_secret=SMS_CONFIG['ovh_application_secret'],
            ovh_consumer_key=SMS_CONFIG['ovh_consumer_key'],
            ovh_service_name=SMS_CONFIG['ovh_service_name'],
            ovh_sender=SMS_CONFIG['ovh_sender']
        )
        
        print(f"📋 Configuration:")
        print(f"  Application Key: {config.ovh_application_key}")
        print(f"  Service Name: {config.ovh_service_name}")
        print(f"  Sender: {config.ovh_sender}")
        
        # Initialisation du notificateur OVH
        print("\n🔌 Initialisation du client OVH...")
        notifier = OVHSMSNotifier(config)
        
        # Test de récupération des infos du service
        print("\n📊 Récupération des informations du service...")
        service_info = notifier.get_service_info()
        
        if service_info:
            print("✅ Connexion OVH réussie !")
            print(f"📋 Informations du service:")
            for key, value in service_info.items():
                print(f"  {key}: {value}")
        else:
            print("❌ Impossible de récupérer les informations du service")
            return False
        
        # Test de récupération du solde
        print("\n💰 Vérification du solde...")
        balance = notifier.get_credit_balance()
        print(f"💳 Crédits restants: {balance.get('credits_left', 'Inconnu')}")
        print(f"📊 Status: {balance.get('status', 'Inconnu')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test OVH: {e}")
        return False

def test_ovh_sms_send():
    """Test d'envoi SMS avec debug détaillé"""
    print("\n📱 Test d'envoi SMS")
    print("=" * 30)
    
    config = get_config()
    notifier = OVHSMSNotifier(config)
    
    # Numéro de test
    test_number = "+33769652410"  
    
    print(f"📞 Envoi vers: {test_number}")
    print(f"📤 Sender: {config.ovh_sender}")
    print(f"🔧 Service: {config.ovh_service_name}")
    
    try:
        # Test avec debug activé
        success = notifier.send(
            recipient=test_number,
            subject="Test",
            message="Test d'envoi SMS depuis votre système de notification OVH! ID: 12345"
        )
        
        print(f"📤 Résultat envoi SMS: {success}")
        
        # Vérification du solde après envoi
        print("\n💰 Vérification du solde après envoi...")
        balance = notifier.get_credit_balance()
        print(f"💳 Crédits restants: {balance.get('credits_left', 'Inconnu')}")
        
        if success:
            print("✅ SMS envoyé avec succès !")
            print("� Vérifiez votre téléphone")
        else:
            print("❌ Échec de l'envoi SMS")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Test principal"""
    print("🚀 Tests OVH Cloud SMS")
    print("=" * 50)
    
    # Test de connexion
    connection_ok = test_ovh_connection()
    
    if connection_ok:
        # Test d'envoi (optionnel)
        test_ovh_sms_send()
        
        print("\n🎉 Configuration OVH validée !")
        print("✅ Votre système peut maintenant envoyer des SMS via OVH")
    else:
        print("\n❌ Problème de configuration OVH")
        print("💡 Vérifiez vos clés API et le nom du service")

if __name__ == "__main__":
    main()

