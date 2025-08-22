import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import sys
import json
import time
from typing import List, Optional
from dataclasses import dataclass, field
from . import config
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Importation absolue au lieu de relative
from notifier import Notifier
from notifier.config import get_config

from twocaptcha import TwoCaptcha

logger = logging.getLogger(__name__)


CGU_URL = f"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/{{}}/cgu/"
CRENEAU_URL = f"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/{{}}/creneau/"

js_get_slot = """
let colu = document.querySelectorAll("div.blocCreneauSelection");
let result = {};

for (let col of colu){
    const h3Element = col.querySelector("h3");
    if (!h3Element) continue;
    
    const pDate = h3Element.innerText.split('\\n').join(',');
    result[pDate] = [];

    const creneaux = col.querySelectorAll("li");
    console.log('Créneaux trouvés:', creneaux.length);

    if (creneaux.length > 0){
        for (let c of creneaux){
            const text = c.innerText.trim();
            if (text) {
                console.log('Créneau:', text);
                result[pDate].push(text);
            }
        }
    }
}

console.log('Résultat final:', result);
return result;"""


class BrowserProxied:
    """Classe pour gérer le navigateur avec proxy et fonctionnalités avancées."""
    
    def __init__(self, proxy: Optional[str] = None, headless: bool = True, notifier: Optional[Notifier] = None):
        """Initialise le navigateur avec les options de proxy et mode headless."""
        self.proxy = proxy
        self.headless = headless
        self.driver = None
        self.wait = None
        self.ids_prefecture: List[str] = []
        self.notifier = notifier
        
        logger.info(f"BrowserProxied initialisé - Proxy: {proxy}, Headless: {headless}")
        
        # Initialiser le driver automatiquement
        self.init_driver()  # Commenté pour permettre l'init manuelle
        
    def init_driver(self):
        """Initialise le driver avec les options de proxy si spécifié."""
        logger.info("Initialisation du driver Chrome avec proxy...")
        if not self.proxy:
            logger.warning("Aucun proxy spécifié, le driver sera lancé sans proxy.")
            
        # Utiliser la configuration simplifiée avec proxy explicite
        driver_config = config.get_config(headless=self.headless, proxy=self.proxy, logging=False)
        self.driver = driver_config.create_driver()
        
        self.wait = WebDriverWait(self.driver, 15)
        logger.info("Driver Chrome initialisé avec succès")

    def verify_proxy(self):
        
        if not self.proxy:
            logger.warning("Aucun proxy spécifié. Impossible de vérifier l'IP.")
            return
        
        time.sleep(2)
        self.driver.get("https://api.ipify.org")
        time.sleep(1)
        driver_ip = self.driver.find_element(By.TAG_NAME, "body").text.strip()
        logger.info(f"IP détectée par le driver : {driver_ip}")

        try:
            requests_ip = requests.get(
                "https://api.ipify.org",
                proxies={
                    "http": f"http://{self.proxy}",
                    "https": f"http://{self.proxy}"
                },
                timeout=10
            ).text.strip()
            logger.info(f"IP détectée par requests via proxy : {requests_ip}")
        except Exception as e:
            logger.error(f"Impossible de récupérer l'IP du proxy via requests : {e}")
            return

        if driver_ip != requests_ip:
            logger.error("L'IP du driver ne correspond pas à celle vue par requests via le proxy. Arrêt du process.")
            return False
        else:
            logger.info("L'IP du driver correspond à celle vue par requests via le proxy. Process continué.")
            return True


    def load_ids(self, ids_prefecture : list):
        """Charge les IDs des préfectures à scraper."""
        self.ids_prefecture = ids_prefecture
        
        logger.info(f"IDs de préfecture chargés : {self.ids_prefecture}")
        
    def scan_prefectures(self):
        """Méthode de scan pour les préfectures."""
        
        if not self.proxy:
            logger.warning("Aucun proxy spécifié. Le scan peut être limité.")
        
        if not self.ids_prefecture:
            logger.error("Aucun ID de préfecture chargé. Veuillez charger les IDs avant de scanner.")
            return
    
        logger.info("Démarrage du scan des préfectures...")


        delay = 10
        
           
        for id_pref in self.ids_prefecture:
            flag = True
            iteration = 0
            logger.info(f"Début du scan pour l'ID de préfecture : {id_pref}")
                
            while flag and iteration < 6:
                    
                iteration += 1
                logger.info(f"--- Itération {iteration} pour l'ID {id_pref} ---")
                    
                # Vérifier si le driver est initialisé
                try:

                    # Attendre que la page soit complètement chargée
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    logger.info("Page CGU complètement chargée.")

                    current_url = self.driver.current_url
                    logger.info(f"Current URL: {current_url}")

                    if current_url == CGU_URL.format(id_pref):
                        # On est sur la page CGU ou on doit résoudre le captcha
                        logger.info("On est sur la page CGU ou en train de gérer le captcha")
                            
                        try:
                            self.solve_captcha(id_pref)
                        except TimeoutException:
                            logger.info("Aucun captcha trouvé, on continue...")
                        
                        # On peut essayer de résoudre le captcha si présent
                        #if self.solve_captcha():
                        #    logger.info("Captcha résolu, en attente de redirection...")
                        time.sleep(3)

                    elif current_url == CRENEAU_URL.format(id_pref):
                        # On est sur la page des créneaux
                        logger.info("Vérification des créneaux disponibles...")
                        titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h2")))

                        slot_available = True
                        for title in titles:
                            title_text = title.text
                            logger.info(f"Titre trouvé : {title_text}")
                            if "Aucun créneau disponible" in title_text:
                                logger.info("Aucun créneau disponible pour cet ID.")
                                slot_available = False
                                flag = False
                                continue

                        if slot_available:
                            logger.warning("DES CRÉNEAUX SONT DISPONIBLES!")
                            
                            slot_available = self.driver.execute_script(js_get_slot)

                            # building message text

                            days = list(slot_available.keys())
                            
                            message = f"Alerte: Créneaux disponibles pour l'ID {id_pref}:\n"
                            
                            for d in days:
                                if len(slot_available[d]) > 0:
                                    header = f"Date: {d}\n"
                                    
                                    slots = ""
                                    for creneau in slot_available[d]:
                                        
                                        slots += f"\t-{creneau}\n"
                                    message += f"{header}{slots}\n"

                            time.sleep(2)  # Attendre que la page se charge complètement
                            
                            # Envoi de la notification Telegram
                            self.notifier.send_telegram(
                                recipient="6534222555", 
                                subject="Test de notification",
                                message=message
                            )
                            self.notifier.send_email(
                                recipient="lalis.william@gmail.com",
                                subject="Test de notification Email depuis BrowserProxied",
                                message=message
                            )
                            flag = False
                            
                            logger.info(f"\n\n{message}\n\n")
                            
                            continue
                            
                        else:
                            logger.info("Aucun créneau disponible pour le moment.")

                        logger.info(f"Attente de {delay} secondes avant le rafraîchissement...")
                        time.sleep(delay)
                        self.driver.refresh()
                            
                    else:
                        # URL inattendue, on revient au début
                        logger.warning(f"URL inattendue, redémarrage depuis la page CGU")
                        self.driver.get(CGU_URL.format(id_pref))
                        logger.info(f"Chargement de la page CGU pour l'ID {id_pref}...")
                except Exception as e:
                    logger.error(f"Une erreur s'est produite : {str(e)}")
                    # screen shot pour visualiser
                    self.driver.save_screenshot(f"./errors/error_screenshot_{id_pref}_{iteration}.png")

            time.sleep(5)  # Pause entre les préfectures

    def solve_captcha(self, id_pref=""):
        """Résout le captcha si présent."""
        try:
            captcha = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".captcha > img")))
            logger.info("Captcha detected!")
            
            solver = TwoCaptcha('5281d1b2726b86a75560db65f0c9fa86')
            
            path_captcha_img = f"./captcha/captcha-{id_pref}.png"
            
            try:
                captcha.screenshot(path_captcha_img)

            except Exception as e:
                logger.error(f"Erreur lors du screenshot du captcha")
                return False
            
            try:
                result = solver.normal(path_captcha_img)
                logger.info(f"Captcha solved: {result['code']}")
            except Exception as e:
                logger.error(f"Erreur lors de la résolution du captcha : {e}")
                return False
            
            input_field = self.wait.until(EC.presence_of_element_located((By.ID, "captchaFormulaireExtInput")))
            input_field.clear()
            # Résultat plus humain d'écriture de la réponse:
            time.sleep(1)  # Pause pour simuler une écriture humaine
            for char in result["code"]:
                input_field.send_keys(char)
                time.sleep(0.1)
            #input_field.send_keys(result["code"])
            
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            submit_button.click()
            logger.info("Captcha submitted successfully.")
            
            return True
        except TimeoutException:
            logger.info("No captcha found.")
            return False

    def quit(self):
        if self.driver:
            try:
                self.driver.close()
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture du navigateur : {e}")
                
    @staticmethod
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
    
    @staticmethod
    def send_telegram_message(text):
        
        TELEGRAM_BOT_TOKEN = '8025520370:AAHQN-YXBMx3mo_Nu1LuY0VkEVyDBtnJnL0'
        TELEGRAM_CHAT_ID = 6534222555

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

if __name__ == "__main__":


    PROXIES = [
        "5.45.36.49:5432",
        "84.200.208.39:5432",
        "194.53.140.80:5432"
        
    ]

    # Créer l'instance avec proxy et mode visible pour test
    browser = BrowserProxied(proxy=PROXIES[1], headless=True)
    
    try:
        # Initialiser le driver
        browser.init_driver()
        
        # Vérifier le proxy (optionnel)
        browser.verify_proxy()
        
        # Charger les IDs de préfecture (optionnel)
        browser.load_ids(["4600", "1182", "7720", "4154", "4155", "4159", "4165", "4181", "7760", "4185", "4187", "4188", "4189"])
                
        # Démarrer le scan
        browser.scan_prefectures()
        browser.quit()
        
        
    except KeyboardInterrupt:
        logger.info("Script stopped by user")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
    finally:
        browser.quit()
    