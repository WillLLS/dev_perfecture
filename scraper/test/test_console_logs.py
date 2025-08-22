#!/usr/bin/env python3
"""
Script simple pour tester la capture des logs de la console Chrome
"""

import undetected_chromedriver as uc
import time
import logging
from datetime import datetime
import sys

# Configuration du logging avec encodage UTF-8
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("ConsoleLogsTest")

def get_browser_console_logs(driver):
    """Capture et affiche les logs de la console du navigateur Chrome"""
    try:
        # Récupérer les logs de la console
        logs = driver.get_log('browser')
        
        if logs:
            logger.info("=== LOGS CONSOLE NAVIGATEUR ===")
            for log_entry in logs:
                level = log_entry['level']
                message = log_entry['message']
                timestamp = log_entry['timestamp']
                
                # Convertir le timestamp en format lisible
                dt = datetime.fromtimestamp(timestamp / 1000.0)
                formatted_time = dt.strftime("%H:%M:%S.%f")[:-3]
                
                # Afficher selon le niveau
                if level in ['SEVERE', 'ERROR']:
                    logger.error(f"CONSOLE[{formatted_time}] {level}: {message}")
                elif level == 'WARNING':
                    logger.warning(f"CONSOLE[{formatted_time}] {level}: {message}")
                else:
                    logger.info(f"CONSOLE[{formatted_time}] {level}: {message}")
                    
            logger.info("=== FIN LOGS CONSOLE ===")
        else:
            logger.info("Aucun log console disponible")
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs console: {e}")

def main():
    """Test simple pour les logs console"""
    logger.info("=== TEST LOGS CONSOLE CHROME ===")
    
    try:
        # Configuration Chrome compatible - version simplifiée
        options = uc.ChromeOptions()
        
        # Configuration de base (version compatible)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1366,768")
        
        # Logging simple (sans options expérimentales)
        options.add_argument("--enable-logging")
        options.add_argument("--v=1")
        
        # Configuration proxy si disponible
        proxy = "94:80@5.45.36.49:5432"  # Format corrigé
        options.add_argument(f'--proxy-server=http://{proxy}')
        logger.info(f"Proxy configuré: {proxy}")
        
        # Créer le driver sans options expérimentales
        logger.info("Création du driver Chrome...")
        driver = uc.Chrome(options=options)
        
        # Naviguer vers une page de test
        logger.info("Navigation vers page de test...")
        driver.get("https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4600/cgu/")
        
        # Attendre le chargement
        time.sleep(5)
        
        # Essayer de capturer les logs (peut ne pas fonctionner sans loggingPrefs)
        logger.info("Tentative de capture des logs de la console...")
        try:
            get_browser_console_logs(driver)
        except Exception as log_error:
            logger.warning(f"Impossible de capturer les logs console: {log_error}")
            logger.info("Ceci est normal avec certaines versions de Chrome")
        
        # Informations sur la page actuelle
        logger.info(f"URL actuelle: {driver.current_url}")
        logger.info(f"Titre de la page: {driver.title}")
        
        # Attendre un peu plus
        logger.info("Attente 10 secondes...")
        time.sleep(10)
        
        # Nouvelle tentative de logs
        try:
            get_browser_console_logs(driver)
        except Exception as log_error:
            logger.warning(f"Logs toujours inaccessibles: {log_error}")
        
        # Laisser le navigateur ouvert pour inspection
        logger.info("Test terminé. Navigateur laissé ouvert.")
        logger.info("Appuyez sur Entrée pour fermer...")
        input()
        
        driver.quit()
        logger.info("Driver fermé.")
        
    except Exception as e:
        logger.error(f"Erreur dans le test: {e}")
        logger.error(f"Type d'erreur: {type(e).__name__}")
        
        # Informations de debug
        logger.info("Tentative de création d'un driver minimal...")
        try:
            minimal_options = uc.ChromeOptions()
            minimal_options.add_argument("--no-sandbox")
            minimal_driver = uc.Chrome(options=minimal_options)
            logger.info("Driver minimal créé avec succès")
            minimal_driver.quit()
        except Exception as minimal_error:
            logger.error(f"Même le driver minimal échoue: {minimal_error}")

if __name__ == "__main__":
    main()
