"""
# notifierManager.py
Class permettant de faire le lien entre la base de données et d'envoyer des notifications lorsque le scraper détect de nouveau rendez-vous.


"""

from notifier import Notifier
from config import get_config

class NotifierManager:
    """
    Classe pour gérer les notifications.
    Elle initialise le Notifier avec la configuration et fournit des méthodes pour envoyer des notifications.
    """

    def __init__(self):
        """Initialise le Notifier avec la configuration."""
        self.notifier = Notifier(get_config())
        
    def send(self, id_prefecture):
        """
        Envoie une notification pour l'ID de préfecture spécifié.
        Cette méthode utilise le Notifier pour envoyer la notification.
        """
        
        message = f"Nouvelle notification pour l'ID de préfecture: {id_prefecture}"
        
        self.notifier.send_email("lalis.william@gmail.com", "Nouveau rendez-vous détecté", message)

    def send_notification(self, message, method=None):
        """
        Envoie une notification avec le message spécifié.
        Si 'method' est None, utilise tous les canaux disponibles.
        """
        if method:
            self.notifier.send_email(message, method)
        else:
            self.notifier.send(message)
            
if __name__ == "__main__":
    # Exemple d'utilisation
    manager = NotifierManager()
    manager.send(12345)  # Envoie une notification pour l'ID de préfecture 12345