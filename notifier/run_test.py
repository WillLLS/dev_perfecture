#!/usr/bin/env python3
"""
Script de test rapide pour le système Perfecture
Usage: python run_test.py
"""

from config import get_config
from main import Notifier

def main():
    """Test rapide du système"""
    print("🚀 PERFECTURE NOTIFICATION SYSTEM")
    print("=" * 50)
    
    # Test rapide
    notifier = Notifier(get_config())
    print(f"✅ Système initialisé avec {len(notifier.get_available_methods())} canaux")
    print(f"📋 Canaux: {', '.join(notifier.get_available_methods())}")
    
    print("\n💡 Pour des tests complets :")
    print("  python tests/test_simple.py    # Test multi-canal")
    print("  python tests/test_email.py     # Test email uniquement")
    print("  python tests/test_ovh.py       # Test SMS uniquement")
    
    print("\n🔧 Utilitaires :")
    print("  python examples/get_telegram_chat_id.py  # Récupérer Chat ID")
    
    print(f"\n🎯 Votre système est prêt pour votre PoC !")

if __name__ == "__main__":
    main()
