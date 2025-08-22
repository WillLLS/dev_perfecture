#!/usr/bin/env python3
"""
Test simple de connexion email
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import smtplib
import ssl
from config import EMAIL_CONFIG

def test_smtp_connection():
    """Test de connexion SMTP simple"""
    print("🔄 Test de connexion SMTP...")
    print(f"Serveur: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
    print(f"Utilisateur: {EMAIL_CONFIG['email_user']}")
    
    try:
        # Test de connexion
        context = ssl.create_default_context()
        print("📡 Connexion au serveur SMTP...")
        
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            print("🔒 Activation TLS...")
            server.starttls(context=context)
            
            print("🔑 Tentative d'authentification...")
            server.login(EMAIL_CONFIG['email_user'], EMAIL_CONFIG['email_password'])
            
            print("✅ Connexion SMTP réussie !")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erreur d'authentification: {e}")
        print("💡 Vérifiez votre mot de passe d'application Gmail")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Erreur SMTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de diagnostic email")
    print("=" * 30)
    test_smtp_connection()
