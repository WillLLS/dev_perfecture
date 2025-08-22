# 📱 Guide Configuration OVH Cloud SMS

## 🚀 Pourquoi OVH pour votre PoC ?

✅ **Français** et accessible  
✅ **Pas de documents d'entreprise** requis  
✅ **Tarifs transparents** (~0.035€/SMS)  
✅ **Pas d'abonnement mensuel** minimum  
✅ **Parfait pour un PoC** 

## 📋 Étapes de configuration

### 1. **Création du service SMS**

1. **Connectez-vous** à https://www.ovh.com/manager/
2. **Allez dans** "Telecom" > "SMS"
3. **Commandez** un service SMS (minimum 5€ de crédit)
4. **Notez** le nom du service (ex: `sms-ab123456-1`)

### 2. **Création des clés API**

1. **Allez sur** https://api.ovh.com/createToken/
2. **Remplissez** :
   - **Account ID** : Votre identifiant OVH
   - **Password** : Votre mot de passe OVH
   - **Script name** : "Notificateur SMS" (ou autre)
   - **Script description** : "API pour notifications SMS"
   - **Validity** : "Unlimited" (recommandé)
   - **Rights** : 
     - `GET /sms/*`
     - `POST /sms/*`

3. **Validez** et **copiez** :
   - **Application Key**
   - **Application Secret** 
   - **Consumer Key**

### 3. **Configuration dans votre système**

Modifiez votre `config.py` :

```python
# Configuration SMS (OVH Cloud SMS)
SMS_CONFIG = {
    'ovh_application_key': 'votre_application_key_ici',
    'ovh_application_secret': 'votre_application_secret_ici', 
    'ovh_consumer_key': 'votre_consumer_key_ici',
    'ovh_service_name': 'sms-ab123456-1',  # Votre service SMS
    'ovh_sender': 'MonApp'  # Max 11 caractères
}
```

## 💰 Tarification OVH SMS

- **SMS France** : ~0.035€/SMS
- **SMS Europe** : ~0.05€/SMS
- **Pack 100 SMS** : ~3.50€
- **Pack 1000 SMS** : ~25€
- **Pas d'abonnement** : Vous payez seulement ce que vous consommez

## 🧪 Test de votre configuration

Une fois configuré, testez avec :

```python
from config import get_config
from main import Notifier

# Test
config = get_config()
notifier = Notifier(config)

# Vérification
print(f"Canaux disponibles: {notifier.get_available_methods()}")

# Envoi de test (remplacez par votre numéro)
notifier.send_sms("+33123456789", "Test OVH SMS depuis votre système!")
```

## 🔧 Avantages vs Twilio

| Critère | OVH | Twilio |
|---------|-----|--------|
| **Docs entreprise** | ❌ Non requis | ✅ Requis |
| **Numéro français** | ✅ Oui | ❌ Non |
| **Setup rapide** | ✅ < 30min | ❌ Plusieurs jours |
| **Prix SMS** | 0.035€ | 0.08€ |
| **Support français** | ✅ Oui | ❌ Anglais |
| **Parfait pour PoC** | ✅ Oui | ❌ Complexe |

## 🎯 Pour votre PoC

OVH est **parfait** car :
- **Setup en 30 minutes**
- **Aucun document** requis
- **Numéro d'expédition français**
- **Tarifs compétitifs**
- **Idéal pour tester** votre système

Voulez-vous que je vous aide à configurer vos clés OVH ? 😊
