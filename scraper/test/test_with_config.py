#!/usr/bin/env python3
"""
Exemple d'intégration de ChromeDriverConfig dans le script de test captcha
"""

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
import os

# Import de notre nouvelle configuration
from config import ChromeDriverConfig, get_visible_config, get_stealth_config

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging avec encodage UTF-8
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'captcha_test_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)

logger = logging.getLogger("CaptchaTestWithConfig")

class CaptchaTestWithConfig:
    """Test captcha utilisant la nouvelle ChromeDriverConfig"""
    
    def __init__(self, proxy: str = None, mode: str = "visible"):
        self.proxy = proxy
        self.mode = mode
        self.driver = None
        self.wait = None
        
        # URLs de test
        self.test_prefecture_id = 4600
        self.base_url = f"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/{self.test_prefecture_id}/cgu/"
        
        # Créer la configuration selon le mode
        self.config = self._create_config()
        
        logger.info(f"=== CONFIGURATION UTILISÉE ===")
        logger.info(self.config.get_summary())
        logger.info("=" * 40)
    
    def _create_config(self) -> ChromeDriverConfig:
        """Crée la configuration selon le mode choisi"""
        if self.mode == "visible":
            # Mode visible pour debugging
            return get_visible_config(proxy=self.proxy)
        
        elif self.mode == "stealth":
            # Mode furtif pour éviter la détection
            return get_stealth_config(proxy=self.proxy)
        
        elif self.mode == "debug":
            # Mode debug avec logs complets
            config = ChromeDriverConfig(
                headless=False,
                proxy=self.proxy,
                enable_logging=True,
                log_level=0,
                enable_anti_detection=True,
                custom_chrome_args=[
                    "--remote-debugging-port=9222",
                    "--enable-logging",
                    "--v=1"
                ]
            )
            return config
        
        else:
            # Configuration personnalisée pour préfectures
            return ChromeDriverConfig(
                headless=False,  # Mode visible par défaut
                proxy=self.proxy,
                enable_anti_detection=True,
                enable_logging=True,
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                custom_chrome_args=[
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-timer-throttling"
                ],
                experimental_options={
                    'prefs': {
                        'profile.default_content_setting_values.notifications': 2,
                        'profile.default_content_settings.popups': 0
                    }
                }
            )
    
    def create_driver(self):
        """Crée le driver en utilisant la configuration"""
        try:
            logger.info("Création du driver avec ChromeDriverConfig...")
            
            # Utiliser la méthode create_driver de la configuration
            self.driver = self.config.create_driver()
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("SUCCESS - Driver créé avec succès via ChromeDriverConfig")
            return True
            
        except Exception as e:
            logger.error(f"ERREUR - Impossible de créer le driver: {e}")
            return False
    
    def get_browser_console_logs(self):
        """Capture et affiche les logs de la console du navigateur"""
        if not self.config.enable_logging:
            logger.info("Logs non activés dans la configuration")
            return
            
        try:
            logs = self.driver.get_log('browser')
            
            if logs:
                logger.info("=== LOGS CONSOLE NAVIGATEUR ===")
                for log_entry in logs:
                    level = log_entry['level']
                    message = log_entry['message']
                    timestamp = log_entry['timestamp']
                    
                    dt = datetime.fromtimestamp(timestamp / 1000.0)
                    formatted_time = dt.strftime("%H:%M:%S.%f")[:-3]
                    
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
    
    def verify_proxy_ip(self):
        """Vérifie que le proxy fonctionne"""
        if not self.proxy:
            logger.info("Aucun proxy configuré")
            return True
            
        try:
            logger.info("Vérification de l'IP via proxy...")
            self.driver.get("https://api.ipify.org")
            time.sleep(3)
            
            ip_element = self.driver.find_element(By.TAG_NAME, "body")
            detected_ip = ip_element.text.strip()
            
            logger.info(f"IP détectée: {detected_ip}")
            
            # Vérifier si l'IP correspond au proxy
            expected_ip = self.proxy.split(':')[0]
            if detected_ip == expected_ip:
                logger.info("SUCCESS - Proxy fonctionne correctement")
            else:
                logger.warning(f"ATTENTION - IP détectée ({detected_ip}) différente du proxy ({expected_ip})")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification IP: {e}")
            return True
    
    def run_test(self):
        """Lance le test avec la nouvelle configuration"""
        logger.info("=== DÉBUT TEST AVEC ChromeDriverConfig ===")
        
        try:
            # 1. Créer le driver
            if not self.create_driver():
                return False
            
            # 2. Vérifier le proxy si configuré
            if self.proxy:
                if not self.verify_proxy_ip():
                    logger.warning("Problème avec le proxy, mais continuation du test...")
            
            # 3. Navigation vers la page de test
            logger.info("Navigation vers la page CGU...")
            self.driver.get(self.base_url)
            time.sleep(5)
            
            # 4. Capturer les logs console si activés
            if self.config.enable_logging:
                logger.info("Capture des logs console...")
                self.get_browser_console_logs()
            
            # 5. Vérifier le chargement de la page
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            logger.info(f"URL actuelle: {current_url}")
            logger.info(f"Titre de la page: {page_title}")
            
            # 6. Test simple de détection d'éléments
            try:
                # Chercher le bouton cookies
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "tarteaucitronPersonalize2"))
                )
                cookie_button.click()
                logger.info("SUCCESS - Bouton cookies trouvé et cliqué")
                time.sleep(2)
                
            except TimeoutException:
                logger.info("INFO - Pas de popup de cookies trouvé")
            
            # 7. Chercher des éléments de captcha
            try:
                captcha_img = self.driver.find_element(By.CSS_SELECTOR, ".captcha > img")
                logger.info("CAPTCHA DÉTECTÉ sur la page!")
            except:
                logger.info("Aucun captcha visible actuellement")
            
            # 8. Laisser la page ouverte pour inspection
            logger.info("Test terminé - Page laissée ouverte pour inspection")
            logger.info("Appuyez sur Entrée pour fermer le navigateur...")
            input()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur dans le test: {e}")
            return False
        
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("Driver fermé")
                except:
                    logger.warning("Erreur lors de la fermeture du driver")

def main():
    """Fonction principale"""
    print("=== TEST CAPTCHA AVEC ChromeDriverConfig ===")
    print()
    
    # Choix du mode
    print("Modes disponibles:")
    print("1. visible   - Mode visible avec logs (debugging)")
    print("2. stealth   - Mode furtif maximal")
    print("3. debug     - Mode debug avec logs complets")
    print("4. custom    - Configuration personnalisée")
    print()
    
    mode_choice = input("Choisissez un mode (1-4): ").strip()
    
    mode_map = {
        "1": "visible",
        "2": "stealth", 
        "3": "debug",
        "4": "custom"
    }
    
    mode = mode_map.get(mode_choice, "visible")
    print(f"Mode sélectionné: {mode}")
    
    # Configuration du proxy
    proxy_choice = input("Utiliser le proxy 5.45.36.49:5432 ? (Y/n): ").strip().lower()
    proxy = "5.45.36.49:5432" if proxy_choice != 'n' else None
    
    print(f"Proxy: {proxy or 'Aucun'}")
    print()
    
    # Lancer le test
    tester = CaptchaTestWithConfig(proxy=proxy, mode=mode)
    success = tester.run_test()
    
    if success:
        print("\nSUCCESS - Test terminé avec succès")
    else:
        print("\nERREUR - Test échoué")

if __name__ == "__main__":
    main()
