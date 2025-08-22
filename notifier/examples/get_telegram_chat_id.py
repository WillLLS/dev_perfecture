#!/usr/bin/env python3
"""
Script pour récupérer le Chat ID Telegram automatiquement
"""

import requests
import time
from config import TELEGRAM_CONFIG

class TelegramChatIDFinder:
    """Utilitaire pour trouver le Chat ID Telegram"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def get_bot_info(self):
        """Récupère les informations du bot"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    return bot_info['result']
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos du bot: {e}")
            return None
    
    def get_updates(self):
        """Récupère les derniers messages reçus par le bot"""
        try:
            url = f"{self.base_url}/getUpdates"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result', [])
            return []
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des updates: {e}")
            return []
    
    def find_chat_ids(self):
        """Trouve tous les Chat IDs qui ont interagi avec le bot"""
        updates = self.get_updates()
        chat_ids = {}
        
        for update in updates:
            if 'message' in update:
                message = update['message']
                chat = message.get('chat', {})
                from_user = message.get('from', {})
                
                chat_id = chat.get('id')
                chat_type = chat.get('type')
                username = from_user.get('username')
                first_name = from_user.get('first_name', '')
                last_name = from_user.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip()
                
                if chat_id:
                    chat_ids[chat_id] = {
                        'username': username,
                        'name': full_name,
                        'type': chat_type,
                        'last_message': message.get('text', ''),
                        'date': message.get('date')
                    }
        
        return chat_ids
    
    def send_test_message(self, chat_id: int):
        """Envoie un message de test pour confirmer le Chat ID"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': '✅ Chat ID confirmé ! Votre système de notification peut maintenant vous envoyer des messages.',
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=data)
            return response.status_code == 200
        except Exception:
            return False

def main():
    """Fonction principale"""
    print("🤖 RÉCUPÉRATION AUTOMATIQUE DU CHAT ID TELEGRAM")
    print("=" * 60)
    
    bot_token = TELEGRAM_CONFIG['telegram_bot_token']
    
    if not bot_token or bot_token == 'votre_bot_token':
        print("❌ Token bot Telegram non configuré !")
        print("💡 Veuillez configurer TELEGRAM_CONFIG dans config.py")
        return
    
    finder = TelegramChatIDFinder(bot_token)
    
    # Test du bot
    print("🔍 Vérification du bot...")
    bot_info = finder.get_bot_info()
    
    if bot_info:
        print(f"✅ Bot trouvé: @{bot_info['username']}")
        print(f"📝 Nom: {bot_info['first_name']}")
        print(f"🆔 ID Bot: {bot_info['id']}")
    else:
        print("❌ Impossible de contacter le bot !")
        print("💡 Vérifiez votre token dans config.py")
        return
    
    print("\n" + "=" * 60)
    print("📱 INSTRUCTIONS POUR RÉCUPÉRER VOTRE CHAT ID")
    print("=" * 60)
    print(f"1. Ouvrez Telegram et cherchez votre bot: @{bot_info['username']}")
    print("2. Envoyez un message à votre bot (par exemple: /start ou 'Hello')")
    print("3. Appuyez sur Entrée ici pour scanner les messages...")
    
    input("\n⏳ Envoyez un message à votre bot puis appuyez sur Entrée...")
    
    print("\n🔍 Recherche des Chat IDs...")
    chat_ids = finder.find_chat_ids()
    
    if not chat_ids:
        print("❌ Aucun Chat ID trouvé !")
        print("💡 Assurez-vous d'avoir envoyé un message à votre bot")
        print(f"   Bot: @{bot_info['username']}")
        return
    
    print(f"\n📋 {len(chat_ids)} Chat ID(s) trouvé(s):")
    print("-" * 40)
    
    for i, (chat_id, info) in enumerate(chat_ids.items(), 1):
        print(f"\n{i}. Chat ID: {chat_id}")
        if info['username']:
            print(f"   👤 Username: @{info['username']}")
        if info['name']:
            print(f"   📝 Nom: {info['name']}")
        print(f"   💬 Type: {info['type']}")
        print(f"   📝 Dernier message: {info['last_message'][:50]}...")
        
        # Si c'est votre username, on le signale
        if info['username'] == 'automate_y':
            print("   🎯 ← C'est VOTRE Chat ID !")
    
    # Sélection du Chat ID
    if len(chat_ids) == 1:
        selected_chat_id = list(chat_ids.keys())[0]
        print(f"\n✅ Chat ID sélectionné automatiquement: {selected_chat_id}")
    else:
        print(f"\n❓ Quel Chat ID voulez-vous utiliser ? (1-{len(chat_ids)})")
        try:
            choice = int(input("Votre choix: ")) - 1
            selected_chat_id = list(chat_ids.keys())[choice]
        except (ValueError, IndexError):
            print("❌ Choix invalide !")
            return
    
    # Test d'envoi
    print(f"\n🧪 Test d'envoi vers Chat ID: {selected_chat_id}")
    success = finder.send_test_message(selected_chat_id)
    
    if success:
        print("✅ Message de test envoyé avec succès !")
        print("📱 Vérifiez votre Telegram")
    else:
        print("❌ Erreur lors de l'envoi du test")
    
    # Instructions finales
    print("\n" + "=" * 60)
    print("🎯 CONFIGURATION FINALE")
    print("=" * 60)
    print("Pour utiliser ce Chat ID dans votre système, vous avez 2 options:")
    print()
    print("📝 Option 1 - Avec Chat ID (recommandé):")
    print(f"   Utilisez: {selected_chat_id}")
    print()
    print("📝 Option 2 - Avec Username:")
    selected_info = chat_ids[selected_chat_id]
    if selected_info['username']:
        print(f"   Utilisez: @{selected_info['username']}")
    else:
        print("   ❌ Pas d'username disponible pour ce chat")
    
    print(f"\n💾 SAUVEGARDEZ VOTRE CHAT ID: {selected_chat_id}")
    print("🔧 Vous pouvez maintenant l'utiliser dans vos scripts de notification !")

if __name__ == "__main__":
    main()
