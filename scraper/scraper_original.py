from driver import driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from logger import logger
import time
import argparse
import os
import requests  # Ajout pour envoyer des messages Telegram
from datetime import datetime
import pytz

from twocaptcha import TwoCaptcha

solver = TwoCaptcha('5281d1b2726b86a75560db65f0c9fa86')

CGU_URL = "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4600/cgu/"
CRENEAU_URL = "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4600/creneau/"

#CGU_URL = "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4143/cgu/"
#CRENEAU_URL = "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/4143/creneau/"

# Affichage de la variable d'environnement PROXY pour vérification
logger.info(f"Valeur de la variable d'environnement PROXY : {os.environ.get('PROXY')}")

# --- Configuration Telegram ---
TELEGRAM_BOT_TOKEN = '8025520370:AAHQN-YXBMx3mo_Nu1LuY0VkEVyDBtnJnL0'
TELEGRAM_CHAT_ID = 6534222555

def send_telegram_message(text):
    """Envoie un message via le bot Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Erreur lors de l'envoi Telegram: {response.text}")
    except Exception as e:
        logger.error(f"Exception lors de l'envoi Telegram: {str(e)}")

def check_proxy_connection(proxy_url=None):
    """Vérifie la connexion du proxy en testant une requête simple."""
    test_url = "https://httpbin.org/ip"
    try:
        if proxy_url:
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            response = requests.get(test_url, proxies=proxies, timeout=10)
        else:
            response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            ip_info = response.json()
            logger.info(f"Proxy test réussi. IP détectée: {ip_info.get('origin', 'Inconnue')}")
            return True
        else:
            logger.warning(f"Test proxy échoué. Code de statut: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Erreur lors du test proxy: {str(e)}")
        return False

def send_telegram_message_slot_available():
    """Envoie une notification Telegram uniquement si un créneau est disponible, avec heure Paris et emojis."""
    paris_tz = pytz.timezone('Europe/Paris')
    now_paris = datetime.now(paris_tz).strftime('%d/%m/%Y %H:%M:%S')
    message = (
        "🚨🚗 *Créneau disponible détecté !*\n\n"
        f"🕒 {now_paris} (heure de Paris)\n"
        "➡️ Rendez-vous sur le site pour réserver rapidement !"
        "\n\n🔗 [Réserver ici]({})".format(CRENEAU_URL)
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Erreur lors de l'envoi Telegram: {response.text}")
    except Exception as e:
        logger.error(f"Exception lors de l'envoi Telegram: {str(e)}")

def solve_captcha(wait):
    """Solve captcha if present"""
    try:
        captcha = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha > img")))
        logger.info("Captcha detected, attempting to solve")
        
        captcha.screenshot("captcha.png")
        result = solver.normal('captcha.png')    
        logger.info(f"Captcha solution: {result['code']}")
        
        input_field = wait.until(EC.presence_of_element_located((By.ID, "captchaFormulaireExtInput")))
        input_field.clear()
        input_field.send_keys(result["code"])
        
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()
        return True
        
    except TimeoutException:
        logger.info("No captcha found")
        return False
    except Exception as e:
        logger.error(f"Error solving captcha: {str(e)}")
        return False

import sys

def loading_bar(seconds):
    """Affiche une barre de chargement dans la console pendant 'seconds' secondes."""
    bar_length = 30  # Limite la taille de la barre pour éviter le débordement
    for i in range(seconds):
        filled_length = int(bar_length * (i + 1) // seconds)
        bar = "[" + "#" * filled_length + "-" * (bar_length - filled_length) + "]"
        sys.stdout.write(f"\rChargement {bar} {i+1}/{seconds}s")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * (bar_length + 30) + "\r")  # Efface la ligne après chargement
    sys.stdout.flush()

def check_appointments(is_test_mode=True):
        
    delay = 600 if not is_test_mode else 10  # 10 minutes en mode normal, 10s en test
    wait = WebDriverWait(driver, 15)
    
    logger.info("Démarrage du script de vérification des créneaux de permis de conduire")

    iteration = 0  # Compteur d'itérations

    while True:
        iteration += 1
        try:
            current_url = driver.current_url
            logger.info(f"Current URL: {current_url}")

            if current_url == CGU_URL or solve_captcha(wait):
                # We're either on CGU page or need to solve captcha
                logger.info("On CGU page or handling captcha")
                
                # Handle cookie consent if present
                try:
                    cookie_button = wait.until(
                        EC.element_to_be_clickable((By.ID, "tarteaucitronPersonalize2"))
                    )
                    cookie_button.click()
                except TimeoutException:
                    pass

                # Try to solve captcha if present
                if solve_captcha(wait):
                    logger.info("Captcha solved, waiting for redirect...")
                    loading_bar(3)
                
            elif current_url == CRENEAU_URL:
                # We're on the appointments page
                logger.info("Checking available slots...")
                titles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h2")))
                
                slot_available = True
                for title in titles:
                    title_text = title.text
                    logger.info(f"Found title: {title_text}")
                    if "Aucun créneau disponible" in title_text:
                        slot_available = False

                if slot_available:
                    logger.warning("SLOTS MIGHT BE AVAILABLE!")
                    send_telegram_message_slot_available()
                else:
                    logger.info("No slots available at the moment.")

                logger.info(f"Waiting {delay} seconds before refresh...")
                loading_bar(delay)
                driver.refresh()
            else:
                # Unexpected URL, go back to start
                logger.warning(f"Unexpected URL, restarting from CGU page")
                driver.get(CGU_URL)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            driver.save_screenshot(f"error_screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png")
            logger.info(f"Restarting from CGU page in {delay} seconds...")
            loading_bar(delay)
            driver.get(CGU_URL)

if __name__ == "__main__":
    
    PROXIES = [
        "http://94:80@5.45.36.49:5432",
        "http://94:80@84.200.208.39:5432",
        "http://94:80@194.53.140.80:5432"
    ]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run in test mode (10s delay)')
    parser.add_argument('--proxy', type=str, help='Proxy personnalisé à utiliser (ex: http://user:pass@host:port)')
    parser.add_argument('--proxy-index', type=int, choices=range(len(PROXIES)), default=0, 
                       help=f'Index du proxy par défaut à utiliser (0-{len(PROXIES)-1}). Par défaut: 0')
    parser.add_argument('--no-proxy', action='store_true', help='Désactiver l\'utilisation de proxy')
    parser.add_argument('--headless', action='store_true', help='Activer le mode headless (navigateur invisible)')
    parser.add_argument('--user-agent', type=str, help='User-Agent personnalisé')
    args = parser.parse_args()
    # Gestion de la sélection de proxy
    proxy_to_use = [
        "http://94:80@5.45.36.49:5432",
        "http://94:80@84.200.208.39:5432",
        "http://94:80@194.53.140.80:5432"
    ]
    
    if args.no_proxy:
        logger.info("Mode sans proxy activé")
        proxy_to_use = None
    elif args.proxy:
        # Proxy personnalisé spécifié
        proxy_to_use = args.proxy
        logger.info(f"Proxy personnalisé utilisé : {proxy_to_use}")
    else:
        # Utilisation d'un proxy par défaut
        proxy_to_use = PROXIES[args.proxy_index]
        logger.info(f"Proxy par défaut #{args.proxy_index} utilisé : {proxy_to_use}")
    
    # Test de la connexion
    if proxy_to_use:
        logger.info("Test de la connexion via proxy...")
        if not check_proxy_connection(proxy_to_use):
            logger.error("Impossible de se connecter via le proxy spécifié. Arrêt du script.")
            exit(1)
    else:
        # Test de la connexion normale
        logger.info("Test de la connexion directe...")
        if not check_proxy_connection():
            logger.warning("Problème de connexion internet détecté.")

    # Les arguments proxy et user-agent sont à utiliser dans driver.py (voir instructions dans ce fichier)
    if proxy_to_use:
        # Définir la variable d'environnement PROXY pour driver.py
        os.environ['PROXY'] = proxy_to_use
        logger.info(f"Variable d'environnement PROXY définie : {proxy_to_use}")
    
    if args.headless:
        # Définir la variable d'environnement HEADLESS pour driver.py
        os.environ['HEADLESS'] = 'true'
        logger.info("Mode headless activé")
    else:
        logger.info("Mode headless désactivé (navigateur visible)")
    
    if args.user_agent:
        logger.info(f"User-Agent personnalisé : {args.user_agent}")

    try:
        check_appointments(is_test_mode=args.test)
    except KeyboardInterrupt:
        logger.info("Script stopped by user")
        driver.quit()