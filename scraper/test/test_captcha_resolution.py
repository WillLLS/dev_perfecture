#!/usr/bin/env python3
"""
Script de test pour vérifier la résolution de captcha
Test sur une seule préfecture (ID 4600) en mode visible
"""

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from twocaptcha import TwoCaptcha

import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging détaillé avec encodage UTF-8
import sys
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'captcha_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)

# Désactiver les logs verbeux de Selenium et undetected_chromedriver
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.remote').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.common').setLevel(logging.WARNING)
logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger("CaptchaTest")

class CaptchaTestScraper:
    """Scraper de test pour captcha uniquement avec proxy et gestion Cloudflare"""
    
    def __init__(self, twocaptcha_key: str, proxy: str = None):
        self.twocaptcha_key = twocaptcha_key
        self.solver = TwoCaptcha(twocaptcha_key) if twocaptcha_key else None
        self.proxy = proxy  # Format: "host:port"
        self.driver = None
        self.wait = None
        
        # URL de test pour préfecture ID 4600
        self.test_prefecture_id = 4600
        self.base_url = f"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/{self.test_prefecture_id}/cgu/"
        self.creneau_url = f"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/{self.test_prefecture_id}/creneau/"
        
        logger.info(f"Initialisation du test captcha pour préfecture ID {self.test_prefecture_id}")
        logger.info(f"Clé 2captcha: {'CONFIGURÉE' if self.solver else 'MANQUANTE'}")
        logger.info(f"Proxy: {'DÉFINI - ' + proxy if proxy else 'AUCUN PROXY'}")
    
    def create_driver(self):
        """Crée un driver Chrome en mode visible avec proxy et protection Cloudflare"""
        try:
            options = uc.ChromeOptions()
            
            # Configuration du proxy si fourni - DIAGNOSTIC DÉTAILLÉ
            if self.proxy:
                # Vérifier le format du proxy
                if ':' not in self.proxy:
                    logger.error(f"PROXY - Format invalide: {self.proxy} (attendu: host:port)")
                    return None
                
                proxy_parts = self.proxy.split(':')
                if len(proxy_parts) != 2:
                    logger.error(f"PROXY - Format invalide: {self.proxy} (attendu: host:port)")
                    return None
                
                proxy_host, proxy_port = proxy_parts
                logger.info(f"PROXY - Host: {proxy_host}, Port: {proxy_port}")
                
                # Test de connexion au proxy
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((proxy_host, int(proxy_port)))
                    sock.close()
                    
                    if result != 0:
                        logger.error(f"PROXY - Impossible de se connecter à {proxy_host}:{proxy_port}")
                        logger.error("PROXY - Le proxy n'est pas accessible ou ne répond pas")
                        return None
                    else:
                        logger.info(f"PROXY - Connexion au proxy réussie: {proxy_host}:{proxy_port}")
                        
                except Exception as proxy_test_error:
                    logger.error(f"PROXY - Erreur lors du test de connexion: {proxy_test_error}")
                    return None
                
                # Configuration du proxy pour Chrome
                proxy_url = f"http://{self.proxy}"
                options.add_argument(f'--proxy-server={proxy_url}')
                logger.info(f"PROXY - Configuration Chrome: {proxy_url}")
            
            # Configuration ANTI-DÉTECTION améliorée
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1366,768")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-infobars")
            
            # Activer les logs de la console et réseau pour diagnostic
            options.add_argument("--enable-logging")
            options.add_argument("--log-level=0")
            options.add_experimental_option('useAutomationExtension', False)
            
            # Capacités pour logs détaillés
            options.add_experimental_option('loggingPrefs', {
                'browser': 'ALL',
                'performance': 'ALL',
                'driver': 'ALL'
            })
            
            # User agent plus récent et réaliste
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # PAS de mode headless pour le test
            logger.info("DRIVER - Création du driver en mode VISIBLE pour test captcha")
            
            # Créer le driver SANS navigation automatique
            self.driver = uc.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 30)
            
            # Scripts anti-détection après création
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR', 'fr']})")
            self.driver.execute_script("window.chrome = { runtime: {} }")
            
            logger.info("SUCCESS - Driver créé avec succès")
            return self.driver
                
        except Exception as e:
            logger.error(f"ERREUR - Erreur critique lors de la création du driver: {e}")
            logger.error(f"ERREUR - Type d'erreur: {type(e).__name__}")
            logger.error(f"ERREUR - Détails complets: {str(e)}")
            return None
    
    def check_environment_variables(self):
        """Vérifie les variables d'environnement"""
        logger.info("=== VÉRIFICATION VARIABLES D'ENVIRONNEMENT ===")
        
        # Variables critiques pour le test
        env_vars = {
            'TWOCAPTCHA_API_KEY': os.environ.get('TWOCAPTCHA_API_KEY'),
            'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN'),
            'TELEGRAM_CHAT_ID': os.environ.get('TELEGRAM_CHAT_ID')
        }
        
        for var_name, var_value in env_vars.items():
            if var_value:
                if 'TOKEN' in var_name or 'API_KEY' in var_name:
                    masked_value = var_value[:10] + '...' + var_value[-5:] if len(var_value) > 15 else var_value
                    logger.info(f"OK - {var_name}: {masked_value}")
                else:
                    logger.info(f"OK - {var_name}: {var_value}")
            else:
                logger.warning(f"MANQUANT - {var_name}: NON DÉFINIE")
        
        logger.info("=" * 50)
    
    def check_driver_health(self):
        """Vérifie si le driver est encore actif et fonctionnel"""
        try:
            if not self.driver:
                return False
            
            # Test simple pour vérifier si le driver répond
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            logger.debug(f"DRIVER_CHECK - URL: {current_url}, Title: {page_title[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"ERREUR - Driver non fonctionnel: {e}")
            return False
    
    def restart_driver_if_needed(self):
        """Redémarre le driver s'il est planté"""
        if not self.check_driver_health():
            logger.warning("RESTART - Driver planté, tentative de redémarrage...")
            
            # Fermer l'ancien driver si possible
            try:
                if self.driver:
                    self.driver.quit()
            except:
                pass
            
            # Recréer le driver
            self.driver = None
            if self.create_driver():
                logger.info("SUCCESS - Driver redémarré avec succès")
                return True
            else:
                logger.error("ERREUR - Impossible de redémarrer le driver")
                return False
        
        return True
    
    def safe_driver_action(self, action_func, *args, **kwargs):
        """Exécute une action sur le driver avec gestion d'erreur et redémarrage automatique"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if not self.check_driver_health() and attempt > 0:
                    if not self.restart_driver_if_needed():
                        return None
                
                return action_func(*args, **kwargs)
                
            except Exception as e:
                logger.warning(f"ATTENTION - Erreur dans action driver (tentative {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"ERREUR - Action échouée après {max_retries} tentatives")
                    return None
        
        return None
    
    def get_browser_console_logs(self):
        """Capture et affiche les logs de la console du navigateur Chrome"""
        try:
            if not self.driver:
                logger.warning("Driver non disponible pour récupérer les logs console")
                return
            
            # Récupérer les logs de la console
            logs = self.driver.get_log('browser')
            
            if logs:
                logger.info("=== LOGS CONSOLE NAVIGATEUR ===")
                for log_entry in logs:
                    level = log_entry['level']
                    message = log_entry['message']
                    timestamp = log_entry['timestamp']
                    
                    # Convertir le timestamp en format lisible
                    from datetime import datetime
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
    
    def get_browser_network_logs(self):
        """Capture et affiche les logs réseau du navigateur (si activés)"""
        try:
            if not self.driver:
                logger.warning("Driver non disponible pour récupérer les logs réseau")
                return
            
            # Récupérer les logs réseau (performance)
            logs = self.driver.get_log('performance')
            
            if logs:
                logger.info("=== LOGS RÉSEAU NAVIGATEUR ===")
                for log_entry in logs[-10:]:  # Afficher seulement les 10 derniers
                    message = log_entry['message']
                    # Parser le JSON du message
                    import json
                    try:
                        log_data = json.loads(message)
                        method = log_data.get('message', {}).get('method', 'Unknown')
                        params = log_data.get('message', {}).get('params', {})
                        
                        if method in ['Network.responseReceived', 'Network.requestWillBeSent', 'Network.loadingFailed']:
                            logger.info(f"NETWORK: {method} - {params}")
                    except:
                        logger.debug(f"NETWORK_RAW: {message[:100]}...")
                        
                logger.info("=== FIN LOGS RÉSEAU ===")
            else:
                logger.info("Aucun log réseau disponible")
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des logs réseau: {e}")

    def check_cloudflare(self):
        """Détecte et gère la protection Cloudflare avec gestion d'erreur robuste"""
        try:
            # Vérifier la santé du driver d'abord
            if not self.check_driver_health():
                logger.error("Driver non fonctionnel pour vérification Cloudflare")
                return False
            
            page_source = self.safe_driver_action(lambda: self.driver.page_source.lower())
            page_title = self.safe_driver_action(lambda: self.driver.title.lower())
            current_url = self.safe_driver_action(lambda: self.driver.current_url)
            
            if not page_source or not page_title or not current_url:
                logger.warning("Impossible de récupérer les informations de la page")
                return True  # Continuer même si on ne peut pas vérifier
            
            # Indicateurs de Cloudflare
            cloudflare_indicators = [
                "cloudflare",
                "checking your browser",
                "just a moment",
                "please wait",
                "ddos protection",
                "security check",
                "ray id"
            ]
            
            is_cloudflare = any(indicator in page_source or indicator in page_title for indicator in cloudflare_indicators)
            
            if is_cloudflare:
                logger.warning("Protection Cloudflare détectée!")
                logger.info(f"Titre de la page: {page_title}")
                logger.info(f"URL: {current_url}")
                
                # Attendre que Cloudflare passe avec vérifications robustes
                logger.info("Attente de la résolution Cloudflare (max 60s)...")
                wait_time = 0
                max_wait = 60  # Augmenter le temps d'attente
                
                while wait_time < max_wait:
                    time.sleep(3)  # Augmenter l'intervalle
                    wait_time += 3
                    
                    # Vérifier la santé du driver
                    if not self.check_driver_health():
                        logger.error("Driver planté pendant l'attente Cloudflare")
                        if not self.restart_driver_if_needed():
                            return False
                        # Retourner à la page si le driver a été redémarré
                        self.safe_driver_action(lambda: self.driver.get(current_url))
                        time.sleep(3)
                    
                    # Vérifier si on est toujours sur Cloudflare
                    current_source = self.safe_driver_action(lambda: self.driver.page_source.lower())
                    current_title = self.safe_driver_action(lambda: self.driver.title.lower())
                    
                    if not current_source or not current_title:
                        logger.warning("Impossible de vérifier l'état Cloudflare, continuation...")
                        continue
                    
                    still_cloudflare = any(indicator in current_source or indicator in current_title for indicator in cloudflare_indicators)
                    
                    if not still_cloudflare:
                        logger.info(f"Cloudflare résolu après {wait_time}s")
                        new_url = self.safe_driver_action(lambda: self.driver.current_url)
                        logger.info(f"Nouvelle URL: {new_url}")
                        return True
                    
                    logger.info(f"Cloudflare encore actif... {wait_time}s/{max_wait}s")
                
                logger.error(f"Cloudflare non résolu après {max_wait}s")
                return False
            
            return True  # Pas de Cloudflare détecté
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification Cloudflare: {e}")
            return True  # Continuer en cas d'erreur
    
    def verify_proxy_ip(self):
        """Vérifie que le proxy fonctionne en récupérant l'IP avec gestion d'erreur robuste"""
        if not self.proxy:
            logger.info("Aucun proxy configuré")
            return True
            
        try:
            logger.info("Vérification de l'IP via proxy...")
            
            # Navigation sécurisée vers le site de vérification IP
            def navigate_to_ip_check():
                self.driver.get("https://api.ipify.org")
                return True
            
            if not self.safe_driver_action(navigate_to_ip_check):
                logger.error("Impossible de naviguer vers le site de vérification IP")
                return False
            
            time.sleep(3)
            
            # Récupération sécurisée de l'IP
            def get_ip():
                ip_element = self.driver.find_element(By.TAG_NAME, "body")
                return ip_element.text.strip()
            
            detected_ip = self.safe_driver_action(get_ip)
            
            if detected_ip:
                logger.info(f"IP détectée: {detected_ip}")
                return True
            else:
                logger.warning("Impossible de récupérer l'IP")
                return True  # Continuer même si on ne peut pas vérifier
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification IP: {e}")
            return True  # Continuer même en cas d'erreur
    
    def solve_captcha(self):
        """Résout le captcha avec 2captcha - version fonctionnelle du script original"""
        if not self.solver:
            logger.error("Pas de solver 2captcha configuré")
            return False
        
        try:
            logger.info("Recherche de captcha...")
            # Correction: WebDriverWait n'accepte pas le paramètre timeout dans until()
            captcha = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha > img"))
            )
            logger.warning("CAPTCHA DÉTECTÉ!")
            
            # Prendre une capture d'écran du captcha
            captcha_filename = "captcha.png"
            captcha.screenshot(captcha_filename)
            logger.info(f"Capture d'écran sauvegardée: {captcha_filename}")
            
            # Résoudre avec 2captcha
            logger.info("Envoi du captcha à 2captcha...")
            result = self.solver.normal(captcha_filename)
            solution = result['code']
            
            logger.info(f"Solution reçue: {solution}")
            
            # Chercher le champ de saisie du captcha
            input_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "captchaFormulaireExtInput"))
            )
            
            # Saisir la solution
            input_field.clear()
            input_field.send_keys(solution)
            logger.info("Solution saisie dans le champ")
            
            # Soumettre le formulaire
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            submit_button.click()
            logger.info("Formulaire soumis")
            
            return True
            
        except TimeoutException:
            logger.info("Aucun captcha détecté")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la résolution du captcha: {e}")
            return False
    
    def run_test(self):
        """Lance le test complet avec vérifications d'URL comme dans le script original"""
        logger.info("DÉBUT DU TEST CAPTCHA")
        logger.info("=" * 60)
        
        try:
            # 1. Vérifier les variables d'environnement
            self.check_environment_variables()
            
            # 2. Créer le driver
            if not self.create_driver():
                logger.error("ERREUR - Impossible de créer le driver")
                return False
            
            # 3. Vérifier le proxy AVANT de naviguer vers la préfecture
            if self.proxy:
                logger.info("PROXY - Vérification du proxy en premier...")
                if not self.verify_proxy_ip():
                    logger.error("ERREUR - Problème avec le proxy")
                    return False
                logger.info("PROXY - Proxy validé, prêt pour navigation")
            
            # 4. Navigation vers la page CGU seulement maintenant
            logger.info("NAVIGATION - Navigation vers la page CGU...")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Capturer les logs de la console après navigation
            logger.info("DIAGNOSTIC - Capture des logs console après navigation...")
            self.get_browser_console_logs()
            
            # 5. Vérifier Cloudflare immédiatement après navigation
            if not self.check_cloudflare():
                logger.error("ERREUR - Impossible de résoudre la protection Cloudflare")
                # Capturer les logs en cas d'erreur Cloudflare
                logger.info("DIAGNOSTIC - Logs console après erreur Cloudflare...")
                self.get_browser_console_logs()
                return False
            
            # 6. Boucle de vérification avec logique d'URL comme dans le script original
            max_iterations = 10  # Limite pour éviter une boucle infinie
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                current_url = self.driver.current_url
                logger.info(f"ITERATION {iteration} - URL actuelle: {current_url}")
                
                # === LOGIQUE COMME DANS LE SCRIPT ORIGINAL ===
                if current_url == self.base_url:
                    logger.info("CGU - Sur la page CGU - Gestion cookies et captcha...")
                    
                    # Vérifier Cloudflare en premier
                    if not self.check_cloudflare():
                        logger.warning("ATTENTION - Protection Cloudflare encore active, nouvelle tentative...")
                        time.sleep(5)
                        continue
                    
                    # Gestion des cookies
                    try:
                        cookie_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "tarteaucitronPersonalize2"))
                        )
                        cookie_button.click()
                        logger.info("COOKIES - Cookies acceptés")
                        time.sleep(2)
                    except TimeoutException:
                        logger.info("INFO - Pas de popup de cookies trouvé")

                    # Tentative de résolution du captcha
                    captcha_solved = self.solve_captcha()
                    if captcha_solved:
                        logger.info("SUCCESS - Captcha résolu, attente de redirection...")
                        time.sleep(5)
                        continue  # Revérifier l'URL
                    else:
                        # Si pas de captcha, attendre un peu et rafraîchir
                        logger.info("REFRESH - Pas de captcha détecté, rafraîchissement...")
                        
                        # Capturer les logs avant rafraîchissement
                        logger.info("DIAGNOSTIC - Logs console avant rafraîchissement...")
                        self.get_browser_console_logs()
                        
                        time.sleep(3)
                        self.driver.refresh()
                        
                elif self.creneau_url in current_url or "creneau" in current_url:
                    logger.info("Sur la page des créneaux - SUCCESS!")
                    
                    # Vérifier le contenu de la page des créneaux
                    page_title = self.driver.title
                    logger.info(f"Titre page créneaux: {page_title}")
                    
                    # Chercher des éléments de créneaux pour validation
                    try:
                        # Chercher les éléments indiquant l'absence de créneaux
                        no_slots_elements = self.driver.find_elements(By.XPATH, 
                            "//*[contains(text(), 'Aucun créneau') or contains(text(), 'aucun créneau') or contains(text(), 'Pas de créneau')]")
                        
                        # Chercher des éléments positifs
                        booking_buttons = self.driver.find_elements(By.XPATH, 
                            "//button[contains(text(), 'Réserver') or contains(@class, 'btn-primary')]")
                        
                        if no_slots_elements:
                            logger.info(f"Page créneaux validée - Aucun créneau disponible ({len(no_slots_elements)} éléments)")
                        elif booking_buttons:
                            logger.warning(f"Page créneaux validée - CRÉNEAUX DISPONIBLES! ({len(booking_buttons)} boutons)")
                        else:
                            logger.info("Page créneaux chargée - État indéterminé")
                            
                    except Exception as e:
                        logger.warning(f"Erreur lors de la validation de la page créneaux: {e}")
                    
                    # Test réussi
                    logger.info("TEST CAPTCHA COMPLET RÉUSSI")
                    
                    # Laisser le navigateur ouvert pour inspection
                    logger.info("Navigateur laissé ouvert pour inspection...")
                    logger.info("Appuyez sur Entrée pour fermer le navigateur et terminer le test...")
                    input()
                    
                    return True
                    
                else:
                    # URL inattendue - comme dans le script original
                    logger.warning(f"URL inattendue: {current_url}")
                    
                    # Vérifier si c'est Cloudflare
                    if not self.check_cloudflare():
                        logger.warning("Protection Cloudflare détectée sur URL inattendue")
                        time.sleep(5)
                        continue
                    
                    logger.info("Retour à la page CGU...")
                    self.driver.get(self.base_url)
                    time.sleep(3)
                
                # Pause entre les itérations
                time.sleep(2)
            
            # Si on arrive ici, on a atteint la limite d'itérations
            logger.error(f"Limite d'itérations atteinte ({max_iterations}) sans succès")
            return False
            
        except Exception as e:
            logger.error(f"Erreur critique dans le test: {e}")
            return False
        
        finally:
            # Nettoyer avec gestion d'erreur
            if self.driver:
                try:
                    logger.info("Laissez-vous le navigateur ouvert pour inspection ? (y/N)")
                    user_input = input().lower().strip()
                    
                    if user_input in ['y', 'yes', 'oui', 'o']:
                        logger.info("Navigateur laissé ouvert pour inspection manuelle")
                        logger.info("N'oubliez pas de fermer le navigateur manuellement")
                    else:
                        logger.info("Fermeture du navigateur...")
                        self.driver.quit()
                        
                except Exception as cleanup_error:
                    logger.warning(f"Erreur lors du nettoyage: {cleanup_error}")
                    try:
                        self.driver.quit()
                    except:
                        logger.warning("Impossible de fermer le driver proprement")
            
            logger.info("FIN DU TEST CAPTCHA")
            logger.info("=" * 60)

def main():
    """Fonction principale du test"""
    print("=== TEST DE RÉSOLUTION CAPTCHA AVEC PROTECTION CLOUDFLARE ===")
    print("Préfecture ID: 4600")
    print("Mode: VISIBLE (headless=False)")
    print("Focus: Test captcha avec gestion Cloudflare")
    print()
    
    # Récupérer la clé 2captcha
    twocaptcha_key = os.environ.get('TWOCAPTCHA_API_KEY')
    
    if not twocaptcha_key:
        print("ERREUR: Variable TWOCAPTCHA_API_KEY non définie")
        print("Veuillez définir cette variable dans votre fichier .env")
        return
    
    # Configuration du proxy (pour contourner Cloudflare)
    PROXY = "5.45.36.49:5432"  # Proxy de test
    
    # DIAGNOSTIC: Test sans proxy d'abord
    print("=== DIAGNOSTIC ===")
    print("Voulez-vous tester:")
    print("1. Avec proxy (recommandé)")
    print("2. Sans proxy (diagnostic)")
    choice = input("Votre choix (1/2): ").strip()
    
    if choice == "2":
        print("Test SANS proxy")
        PROXY = None
    else:
        print(f"Test AVEC proxy: {PROXY}")
    
    print()
    
    # Lancer le test avec ou sans proxy
    tester = CaptchaTestScraper(twocaptcha_key, proxy=PROXY)
    success = tester.run_test()
    
    if success:
        print("\nSUCCESS - TEST CAPTCHA TERMINÉ AVEC SUCCÈS")
    else:
        print("\nERREUR - TEST CAPTCHA ÉCHOUÉ")
        print("Consultez les logs pour plus de détails")

if __name__ == "__main__":
    main()
