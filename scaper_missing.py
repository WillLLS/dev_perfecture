from scraper.browser_proxied import BrowserProxied
from selenium.webdriver.common.by import By
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,  # Changé en DEBUG pour voir plus de détails
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ],
    force=True
)

logging.getLogger("undetected_chromedriver.patcher").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
## Création d'une classe enfer pour encapsuler le comportement du navigateur

CGU_URL = f"https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/{{}}/cgu/"

class BrowserScrap(BrowserProxied):

    def get_data(self, url):
        """Méthode pour récupérer les données d'une URL"""
        logging.info(f"FETCH: Récupération des données de {url}")
        
        try:
            logging.debug(f"NAVIGATE: Chargement de la page {url}")
            self.driver.get(url)
            logging.debug("WAIT: Attente de 5 secondes pour le chargement de la page")
            time.sleep(5)

            logging.debug("EXTRACT: Recherche de l'élément h1 (title)")
            title = self.driver.find_element(By.TAG_NAME, "h1").text
            logging.debug("EXTRACT: Recherche de l'élément h2 (subtitle)")
            subtitle = self.driver.find_element(By.TAG_NAME, "h2").text
            
            logging.info(f"SUCCESS: Title trouvé: '{title}'")
            logging.info(f"SUCCESS: Subtitle trouvé: '{subtitle}'")

            return (title, subtitle)
        
        except Exception as e:
            logging.error(f"ERROR: Erreur lors de la récupération des données de {url}: {e}")
            logging.debug(f"ERROR_DETAIL: Exception type: {type(e).__name__}")
            return None
        
    def scan_ids(self):
        """Méthode pour scanner une liste d'IDs"""
        logging.info(f"SCAN_START: Début du scan de {len(self.ids_prefecture)} IDs")
        results = []
        
        for i, id in enumerate(self.ids_prefecture, 1):
            logging.info(f"PROGRESS: [{i}/{len(self.ids_prefecture)}] Traitement de l'ID: {id}")
            url = CGU_URL.format(id)
            logging.debug(f"URL_GENERATED: {url}")
    
            data = self.get_data(url)
            if data:
                logging.info(f"SUCCESS: Données récupérées pour l'ID {id}")
                results.append({
                    "id": id,
                    "title": data[0],
                    "subtitle": data[1]
                })
            else:
                logging.warning(f"FAILED: Échec de récupération pour l'ID {id}")
                
            with open("scraped_data3.json", "w", encoding="utf-8") as file:
                json.dump(results, file, ensure_ascii=False, indent=4)
                
        logging.info(f"SCAN_COMPLETE: Scan terminé. {len(results)} résultats obtenus sur {len(self.ids_prefecture)} IDs")
        return results
    
    
if __name__ == "__main__":
    
    logging.info("="*60)
    logging.info("SCRIPT_START: Démarrage du script de scraping des préfectures")
    logging.info("="*60)
    
    logging.info("FILE_LOAD: Chargement du fichier d'IDs à scraper")
    with open("./get_prefectures_data/missing_demarches_data_ids.json", "r", encoding="utf-8") as file:
        outer_pref = json.load(file)
    logging.info(f"FILE_SUCCESS: {len(outer_pref)} IDs chargés depuis le fichier")
        
    PROXIES = [
        "5.45.36.49:5432",
        "84.200.208.39:5432",
        "194.53.140.80:5432"   
    ]
    
    
    logging.info(f"PROXY_CONFIG: {len(PROXIES)} proxies configurés")
    
    logging.info(f"BROWSER_INIT: Initialisation du navigateur avec proxy: {PROXIES[0]}")
    scraper = BrowserScrap(proxy=PROXIES[0], headless=False)
    
    logging.info("PROXY_VERIFY: Vérification du proxy")
    scraper.verify_proxy()
    
    logging.info("IDS_LOAD: Chargement des IDs dans le scraper")
    scraper.load_ids(outer_pref)
    
    logging.info("SCAN_BEGIN: Début du processus de scan")
    res = scraper.scan_ids()
    
    logging.info("BROWSER_CLOSE: Fermeture du navigateur")
    scraper.quit()
    
    output_file = "scraped_missing_data_url.json"
    logging.info(f"FILE_SAVE: Sauvegarde des résultats dans {output_file}")
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(res, file, ensure_ascii=False, indent=4)
    
    logging.info("="*60)
    logging.info(f"SCRIPT_COMPLETE: Script terminé avec succès")
    logging.info(f"RESULTS: {len(res)} résultats sauvegardés dans {output_file}")
    logging.info("="*60)
    
    