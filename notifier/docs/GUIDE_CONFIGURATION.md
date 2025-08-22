# 📋 Guide de Configuration Détaillé

## 📧 Configuration Email (Gmail)

### Étapes pour Gmail :

1. **Activez l'authentification à 2 facteurs** :
   - Allez sur https://myaccount.google.com/security
   - Cliquez sur "Authentification à 2 facteurs"
   - Suivez les instructions pour l'activer

2. **Créez un mot de passe d'application** :
   - Toujours sur https://myaccount.google.com/security
   - Cliquez sur "Mots de passe d'application"
   - Sélectionnez "Mail" comme application
   - Générez le mot de passe (16 caractères)
   - **Copiez-le immédiatement** (vous ne pourrez plus le voir)

3. **Configuration dans le système** :
   ```python
   EMAIL_CONFIG = {
       'smtp_server': 'smtp.gmail.com',
       'smtp_port': 587,
       'email_user': 'votre_email@gmail.com',
       'email_password': 'abcd efgh ijkl mnop'  # Le mot de passe d'application
   }
   ```

### Autres fournisseurs email :

#### Outlook/Hotmail :
```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp-mail.outlook.com',
    'smtp_port': 587,
    'email_user': 'votre_email@outlook.com',
    'email_password': 'votre_mot_de_passe'
}
```

#### Yahoo :
```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.mail.yahoo.com',
    'smtp_port': 587,
    'email_user': 'votre_email@yahoo.com',
    'email_password': 'votre_mot_de_passe_app'  # Yahoo nécessite aussi un mot de passe d'app
}
```

## 📨 Configuration Telegram

### Étapes pour créer un bot Telegram :

1. **Ouvrez Telegram** et cherchez **@BotFather**

2. **Commandes à envoyer** :
   ```
   /start
   /newbot
   ```

3. **Choisissez un nom** pour votre bot (ex: "Mon Notificateur")

4. **Choisissez un nom d'utilisateur** (doit finir par 'bot', ex: "mon_notificateur_bot")

5. **Copiez le token** fourni par BotFather (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

6. **Configuration** :
   ```python
   TELEGRAM_CONFIG = {
       'telegram_bot_token': '123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
   }
   ```

### Comment trouver votre Chat ID :

1. **Envoyez un message** à votre bot
2. **Allez sur** : `https://api.telegram.org/bot<VOTRE_TOKEN>/getUpdates`
3. **Cherchez** le champ `"id"` dans `"from"` ou `"chat"`
4. **Utilisez ce numéro** comme destinataire

## 📱 Configuration SMS (Twilio)

### Étapes pour Twilio :

1. **Créez un compte** sur https://www.twilio.com

2. **Vérifiez votre numéro** de téléphone

3. **Achetez un numéro Twilio** (⚠️ Service payant) :
   - Allez dans "Phone Numbers" > "Manage" > "Buy a number"
   - Choisissez un numéro dans votre pays
   - Le coût est généralement ~1€/mois + coût par SMS

4. **Récupérez vos identifiants** :
   - **Account SID** : Visible sur le dashboard
   - **Auth Token** : Cliquez sur "Show" à côté de Auth Token

5. **Configuration** :
   ```python
   SMS_CONFIG = {
       'twilio_account_sid': 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
       'twilio_auth_token': 'votre_auth_token_secret',
       'twilio_phone_number': '+33123456789'  # Le numéro que vous avez acheté
   }
   ```

### Alternatives gratuites pour les SMS :

- **Pour les tests** : Vous pouvez utiliser le numéro de test de Twilio
- **Autres services** : Free Mobile, Orange API (France), etc.

## 🔧 Configuration par Variables d'Environnement (Production)

Pour la production, utilisez des variables d'environnement :

### Windows (PowerShell) :
```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:EMAIL_USER = "votre_email@gmail.com"
$env:EMAIL_PASSWORD = "votre_mot_de_passe_app"
$env:TELEGRAM_BOT_TOKEN = "votre_bot_token"
```

### Linux/Mac :
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export EMAIL_USER="votre_email@gmail.com"
export EMAIL_PASSWORD="votre_mot_de_passe_app"
export TELEGRAM_BOT_TOKEN="votre_bot_token"
```

Puis utilisez :
```python
from utils import load_config_from_env
config = load_config_from_env()
```

## 🧪 Test de Configuration

Une fois configuré, testez avec :

```python
from config import get_config
from main import Notifier

# Test complet
config = get_config()
notifier = Notifier(config)
print(f"Canaux disponibles: {notifier.get_available_methods()}")

# Test email
notifier.send_email(
    recipient="votre_email@exemple.com",
    subject="Test de configuration",
    message="Si vous recevez ceci, la configuration fonctionne !"
)
```

## ❗ Problèmes Courants

### Gmail "Connexion moins sécurisée" :
- **Solution** : Utilisez un mot de passe d'application, pas votre mot de passe habituel

### Telegram "Unauthorized" :
- **Solution** : Vérifiez que le token est correct et que le bot est activé

### SMS "Authentication failed" :
- **Solution** : Vérifiez Account SID et Auth Token, et que vous avez des crédits

### "Import requests could not be resolved" :
- **Solution** : `pip install requests`

## 💡 Conseils

1. **Commencez par l'email** - Plus simple à configurer
2. **Testez un canal à la fois** - Plus facile pour déboguer
3. **Gardez vos tokens secrets** - Ne les commitez jamais dans Git
4. **Utilisez des variables d'environnement** en production
