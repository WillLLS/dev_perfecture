# Notifiers
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import json
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NotificationConfig:
    """Configuration pour les différents types de notifications"""
    # Configuration Email
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    email_user: Optional[str] = None
    email_password: Optional[str] = None
    
    # Configuration SMS OVH
    ovh_application_key: Optional[str] = None
    ovh_application_secret: Optional[str] = None
    ovh_consumer_key: Optional[str] = None
    ovh_service_name: Optional[str] = None
    ovh_sender: Optional[str] = "Notifier"
    
    # Configuration Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class NotificationInterface(ABC):
    """Interface abstraite pour les notifications"""
    
    @abstractmethod
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """Envoie une notification"""
        pass


class EmailNotifier(NotificationInterface):
    """Gestionnaire de notifications par email"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """Valide la configuration email"""
        required_fields = ['smtp_server', 'smtp_port', 'email_user', 'email_password']
        for field in required_fields:
            if getattr(self.config, field) is None:
                raise ValueError(f"Configuration email manquante: {field}")
    
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Envoie un email
        
        Args:
            recipient: Adresse email du destinataire
            subject: Sujet de l'email
            message: Corps du message
            **kwargs: Arguments supplémentaires (html_message, attachments, etc.)
        
        Returns:
            bool: True si envoyé avec succès, False sinon
        """
        try:
            # Création du message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.email_user
            msg['To'] = recipient
            
            # Ajout du texte
            text_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Ajout du HTML si fourni
            if 'html_message' in kwargs:
                html_part = MIMEText(kwargs['html_message'], 'html', 'utf-8')
                msg.attach(html_part)
            
            # Connexion et envoi
            context = ssl.create_default_context()
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.config.email_user, self.config.email_password)
                server.send_message(msg)
            
            logger.debug(f"Email envoyé avec succès à {recipient}")
            return True
            
        except Exception as e:
            logger.debug(f"Erreur lors de l'envoi de l'email: {e}")
            return False


class OVHSMSNotifier(NotificationInterface):
    """Gestionnaire de notifications SMS via OVH Cloud SMS"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self._validate_config()
        self._init_ovh_client()
    
    def _validate_config(self):
        """Valide la configuration OVH SMS"""
        required_fields = ['ovh_application_key', 'ovh_application_secret', 'ovh_consumer_key', 'ovh_service_name']
        for field in required_fields:
            if getattr(self.config, field) is None:
                raise ValueError(f"Configuration OVH SMS manquante: {field}")
    
    def _init_ovh_client(self):
        """Initialise le client OVH"""
        try:
            import ovh
            self.client = ovh.Client(
                endpoint='ovh-eu',  # Europe
                application_key=self.config.ovh_application_key,
                application_secret=self.config.ovh_application_secret,
                consumer_key=self.config.ovh_consumer_key,
            )
            logger.debug("Client OVH SMS initialisé")
        except Exception as e:
            raise ValueError(f"Impossible d'initialiser le client OVH: {e}")
    
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Envoie un SMS via OVH Cloud SMS
        
        Args:
            recipient: Numéro de téléphone au format international (+33...)
            subject: Ignoré pour les SMS (ou ajouté au début du message)
            message: Corps du message SMS
        
        Returns:
            bool: True si envoyé avec succès, False sinon
        """
        try:
            logger.debug(f"Début envoi SMS via OVH...")
            logger.debug(f"Destinataire: {recipient}")
            
            # Formatage du message
            full_message = f"{subject}: {message}" if subject else message
            
            # Limitation SMS (160 caractères)
            if len(full_message) > 160:
                full_message = full_message[:157] + "..."
                logger.debug(f"Message tronqué à 160 caractères")
            
            logger.debug(f"Message final: {full_message}")
            
            # Formatage du numéro pour OVH
            # OVH attend le format international long : 00CCNNNNNNNNNN
            if recipient.startswith("+33"):
                # +33769652410 -> 0033769652410 (format international long)
                formatted_recipient = "00" + recipient[1:].replace(" ", "")
            elif recipient.startswith("+"):
                # Autres pays : +1234567890 -> 001234567890
                formatted_recipient = "00" + recipient[1:].replace(" ", "")
            else:
                # Si déjà au bon format, garder tel quel
                formatted_recipient = recipient.replace(" ", "")
            
            logger.debug(f"Numéro formaté: {formatted_recipient}")
            
            # Données pour l'API OVH
            sms_data = {
                "charset": "UTF-8",
                "class": "phoneDisplay", 
                "coding": "7bit",
                "message": full_message,
                "noStopClause": False,
                "priority": "high",
                "receivers": [formatted_recipient],
                "validityPeriod": 2880  # 48h en minutes
            }
            
            # Ajouter le sender seulement s'il est défini
            if self.config.ovh_sender:
                sms_data["sender"] = self.config.ovh_sender
                sms_data["senderForResponse"] = True
            else:
                # Utiliser le numéro court par défaut d'OVH
                sms_data["senderForResponse"] = True
            
            logger.debug(f"Données envoi: {sms_data}")
            logger.debug(f"Service: {self.config.ovh_service_name}")
            
            # Envoi via le client OVH
            logger.debug("Appel API OVH...")
            result = self.client.post(f'/sms/{self.config.ovh_service_name}/jobs', **sms_data)
            
            logger.debug(f"Réponse OVH: {result}")
            
            # Vérification du résultat
            if result and 'totalCreditsRemoved' in result:
                total_credits = result.get('totalCreditsRemoved', 0)
                logger.debug(f"SMS OVH envoyé avec succès à {recipient}")
                logger.debug(f"Crédits utilisés: {total_credits}")
                return True
            elif result:
                logger.debug(f"SMS OVH envoyé (résultat: {result})")
                return True  # L'envoi a probablement réussi même sans info de crédits
            else:
                logger.debug("Aucune réponse de l'API OVH")
                return False
                
        except Exception as e:
            logger.debug(f"Erreur lors de l'envoi SMS OVH: {e}")
            #import traceback
            #traceback.logger.debug_exc()
            return False
    
    def get_credit_balance(self) -> dict:
        """Récupère le solde de crédits SMS"""
        try:
            service_info = self.client.get(f'/sms/{self.config.ovh_service_name}')
            
            return {
                'credits_left': service_info.get('creditsLeft', 0),
                'status': service_info.get('status', 'unknown'),
                'name': service_info.get('name', self.config.ovh_service_name)
            }
                
        except Exception as e:
            logger.debug(f"Erreur lors de la récupération du solde: {e}")
            return {'credits_left': 0, 'status': 'error'}
    
    def get_service_info(self) -> dict:
        """Récupère les informations détaillées du service SMS"""
        try:
            service_info = self.client.get(f'/sms/{self.config.ovh_service_name}')
            return service_info
        except Exception as e:
            logger.debug(f"Erreur lors de la récupération des infos service: {e}")
            return {}


class TelegramNotifier(NotificationInterface):
    """Gestionnaire de notifications par Telegram"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """Valide la configuration Telegram"""
        if self.config.telegram_bot_token is None:
            raise ValueError("Configuration Telegram manquante: telegram_bot_token")
    
    def send(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """
        Envoie un message Telegram
        
        Args:
            recipient: Chat ID ou nom d'utilisateur Telegram
            subject: Titre du message (optionnel)
            message: Corps du message
            **kwargs: Arguments supplémentaires (parse_mode, disable_web_page_preview, etc.)
        
        Returns:
            bool: True si envoyé avec succès, False sinon
        """
        try:
            # URL de l'API Telegram
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            
            # Formation du message final
            final_message = f"*{subject}*\n\n{message}" if subject else message
            
            # Données pour l'API
            data = {
                'chat_id': recipient,
                'text': final_message,
                'parse_mode': kwargs.get('parse_mode', 'Markdown'),
                'disable_web_page_preview': kwargs.get('disable_web_page_preview', True)
            }
            
            # Envoi de la requête
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                logger.debug(f"Message Telegram envoyé avec succès à {recipient}")
                return True
            else:
                logger.debug(f"Erreur lors de l'envoi du message Telegram: {response.text}")
                return False
                
        except Exception as e:
            logger.debug(f"Erreur lors de l'envoi du message Telegram: {e}")
            return False


class Notifier:
    """Classe principale pour gérer toutes les notifications"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self._notifiers: Dict[str, NotificationInterface] = {}
        self._initialize_notifiers()
    
    def _initialize_notifiers(self):
        """Initialise les notificateurs disponibles selon la configuration"""
        try:
            if all([self.config.smtp_server, self.config.smtp_port, 
                   self.config.email_user, self.config.email_password]):
                self._notifiers['email'] = EmailNotifier(self.config)
                logger.debug("Notificateur Email initialisé")
        except ValueError as e:
            logger.debug(f"Email non initialisé: {e}")
        
        try:
            if all([self.config.ovh_application_key, self.config.ovh_application_secret, 
                   self.config.ovh_consumer_key, self.config.ovh_service_name]):
                self._notifiers['sms'] = OVHSMSNotifier(self.config)
                logger.debug("📱 Notificateur OVH SMS initialisé")
        except ValueError as e:
            logger.debug(f"OVH SMS non initialisé: {e}")
        
        try:
            if self.config.telegram_bot_token:
                self._notifiers['telegram'] = TelegramNotifier(self.config)
                logger.debug("Notificateur Telegram initialisé")
        except ValueError as e:
            logger.debug(f"Telegram non initialisé: {e}")
    
    def get_available_methods(self) -> list:
        """Retourne la liste des méthodes de notification disponibles"""
        return list(self._notifiers.keys())
    
    def send_email(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """Envoie une notification par email"""
        if 'email' in self._notifiers:
            return self._notifiers['email'].send(recipient, subject, message, **kwargs)
        else:
            logger.debug("Notificateur Email non disponible")
            return False
    
    def send_sms(self, recipient: str, message: str, **kwargs) -> bool:
        """Envoie une notification par SMS"""
        if 'sms' in self._notifiers:
            return self._notifiers['sms'].send(recipient, "", message, **kwargs)
        else:
            logger.debug("Notificateur SMS non disponible")
            return False
    
    def send_telegram(self, recipient: str, subject: str, message: str, **kwargs) -> bool:
        """Envoie une notification par Telegram"""
        if 'telegram' in self._notifiers:
            return self._notifiers['telegram'].send(recipient, subject, message, **kwargs)
        else:
            logger.debug("Notificateur Telegram non disponible")
            return False
    
    def send_to_all(self, recipients: Dict[str, str], subject: str, message: str, **kwargs) -> Dict[str, bool]:
        """
        Envoie une notification à travers tous les canaux disponibles
        
        Args:
            recipients: Dictionnaire avec les clés 'email', 'sms', 'telegram' et leurs destinataires
            subject: Sujet de la notification
            message: Corps du message
        
        Returns:
            Dict[str, bool]: Résultats de l'envoi pour chaque canal
        """
        results = {}
        
        if 'email' in recipients and 'email' in self._notifiers:
            results['email'] = self.send_email(recipients['email'], subject, message, **kwargs)
        
        if 'sms' in recipients and 'sms' in self._notifiers:
            results['sms'] = self.send_sms(recipients['sms'], message, **kwargs)
        
        if 'telegram' in recipients and 'telegram' in self._notifiers:
            results['telegram'] = self.send_telegram(recipients['telegram'], subject, message, **kwargs)
        
        return results


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration (remplacez par vos vraies valeurs)
    config = NotificationConfig(
        # Email
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        email_user="votre_email@gmail.com",
        email_password="votre_mot_de_passe_app",
        
        # SMS (Twilio)
        twilio_account_sid="votre_account_sid",
        twilio_auth_token="votre_auth_token",
        twilio_phone_number="+1234567890",
        
        # Telegram
        telegram_bot_token="votre_bot_token"
    )
    
    # Initialisation du notificateur
    notifier = Notifier(config)
    
    # Vérification des méthodes disponibles
    logger.debug(f"Méthodes disponibles: {notifier.get_available_methods()}")
    
    # Exemples d'envoi
    
    # Email simple
    # notifier.send_email(
    #     recipient="destinataire@example.com",
    #     subject="Test de notification",
    #     message="Ceci est un test de notification par email."
    # )
    
    # SMS
    # notifier.send_sms(
    #     recipient="+33123456789",
    #     message="Ceci est un test de notification par SMS."
    # )
    
    # Telegram
    # notifier.send_telegram(
    #     recipient="@username_ou_chat_id",
    #     subject="Test Telegram",
    #     message="Ceci est un test de notification par Telegram."
    # )
    
    # Envoi vers tous les canaux
    # recipients = {
    #     'email': 'destinataire@example.com',
    #     'sms': '+33123456789',
    #     'telegram': '@username_ou_chat_id'
    # }
    # results = notifier.send_to_all(
    #     recipients=recipients,
    #     subject="Notification importante",
    #     message="Ceci est une notification envoyée sur tous les canaux disponibles."
    # )
    # logger.debug(f"Résultats: {results}")
