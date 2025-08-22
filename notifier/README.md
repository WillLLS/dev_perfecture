# 🔔 Système de Notification Multi-Canal Perfecture

Un système de notification professionnel supportant **Email**, **SMS** et **Telegram** avec une architecture OOP propre et extensible.

## ✨ Fonctionnalités

- 📧 **Email** : SMTP Gmail avec support HTML
- 📱 **SMS** : OVH Cloud SMS avec crédits optimisés
- 💬 **Telegram** : Bot API avec formatage Markdown
- 🔄 **Multi-canal** : Envoi simultané sur tous les canaux
- ⚙️ **Configuration centralisée** : Un seul fichier de config
- 🛡️ **Robuste** : Gestion d'erreurs et validation

## 🚀 Installation Rapide

```bash
# Cloner le projet
git clone <votre-repo>
cd notifier

# Installer les dépendances
pip install -r requirements.txt

# Configurer
cp examples/config_example.py config.py
# Éditer config.py avec vos vraies clés
```

## 💻 Utilisation

### Envoi Simple

```python
from config import get_config
from main import Notifier

# Initialisation
notifier = Notifier(get_config())

# Email
notifier.send_email("user@example.com", "Subject", "Message")

# SMS
notifier.send_sms("+33123456789", "Message SMS")

# Telegram
notifier.send_telegram("chat_id", "Subject", "Message")
```

### Envoi Multi-Canal

```python
recipients = {
    'email': 'user@example.com',
    'sms': '+33123456789',
    'telegram': 'chat_id'
}

results = notifier.send_to_all(
    recipients=recipients,
    subject="Notification Importante",
    message="Votre message multi-canal !"
)

print(results)  # {'email': True, 'sms': True, 'telegram': True}
```

## 📁 Structure du Projet

```
notifier/
├── main.py              # Système principal
├── config.py            # Configuration (vos clés)
├── utils.py             # Utilitaires
├── requirements.txt     # Dépendances
├── README.md           # Ce fichier
├── tests/              # Tests du système
│   ├── test_simple.py  # Test rapide multi-canal
│   ├── test_complet.py # Test détaillé
│   ├── test_email.py   # Test email uniquement
│   └── test_ovh.py     # Test SMS OVH uniquement
├── examples/           # Exemples et utilitaires
│   ├── exemple.py      # Exemples d'usage
│   ├── config_example.py # Template de configuration
│   └── get_telegram_chat_id.py # Récupérer Chat ID
├── docs/               # Documentation
│   ├── GUIDE_CONFIGURATION.md
│   ├── GUIDE_OVH_SMS.md
│   └── ALTERNATIVES_SMS_FRANCE.md
└── archive/            # Fichiers de développement
```

## ⚡ Test Rapide

```bash
# Test complet du système
python tests/test_simple.py

# Tests individuels
python tests/test_email.py
python tests/test_ovh.py
```

## 🔧 Configuration

### 1. Gmail (Email)
- Activer l'authentification 2FA
- Générer un mot de passe d'application
- Configurer dans `config.py`

### 2. OVH SMS
- Créer une application OVH
- Générer les clés API
- Acheter des crédits SMS
- Voir `docs/GUIDE_OVH_SMS.md`

### 3. Telegram
- Créer un bot avec @BotFather
- Générer le token
- Obtenir votre Chat ID avec `examples/get_telegram_chat_id.py`

## 📊 Statistiques

- ✅ **3 canaux** supportés
- ✅ **100% fonctionnel** après tests
- ✅ **Architecture OOP** propre
- ✅ **Prêt pour production**

## 🆘 Support

- 📖 Documentation complète dans `/docs/`
- 🧪 Tests exhaustifs dans `/tests/`
- 💡 Exemples dans `/examples/`

## 🏷️ Version

**v1.0.0** - Système complet et opérationnel

---

🔧 **Développé pour Perfecture** | 🚀 **Prêt pour votre PoC**
