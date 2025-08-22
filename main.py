import sys
import csv
import time
import logging
import os
from typing import List, Dict, Any
from pathlib import Path
from multiprocessing import Process, Manager

# Ajouter le chemin du package
package_path = Path("C:/Users/lalis/OneDrive/Bureau/Perfecture/core/dev")
sys.path.insert(0, str(package_path))

from scraper import BrowserProxied

from notifier import Notifier
from notifier import get_config

logger = logging.getLogger(__name__)

# Configuration du logging principal avec encodage UTF-8
logging.basicConfig(
    level=logging.DEBUG,  # Changé en DEBUG pour voir plus de détails
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/main.log', encoding='utf-8')
    ],
    force=True
)


# Créer le répertoire logs s'il n'existe pas
os.makedirs('logs', exist_ok=True)

def read_csv_to_dict_list(file_path):
    """Lit un fichier CSV en gérant différents encodages et séparateurs"""
    data = []
    
    # Liste des encodages à essayer
    encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8', 'utf-8-sig']
    
    # Détecter le séparateur en lisant la première ligne
    separators = [';', ',', '\t']
    
    for encoding in encodings:
        for separator in separators:
            try:
                with open(file_path, mode='r', encoding=encoding) as file:
                    # Lire la première ligne pour vérifier le format
                    first_line = file.readline()
                    file.seek(0)  # Revenir au début
                    
                    # Vérifier si ce séparateur est pertinent
                    if separator in first_line:
                        reader = csv.DictReader(file, delimiter=separator)
                        data = []
                        for row in reader:
                            data.append(row)
                        
                        logger.info(f"Fichier CSV lu avec succès - Encodage: {encoding}, Séparateur: '{separator}', {len(data)} lignes")
                        logger.info(f"Colonnes détectées: {list(data[0].keys()) if data else 'Aucune'}")
                        return data
                        
            except UnicodeDecodeError:
                logger.debug(f"Échec de lecture avec l'encodage {encoding} et séparateur '{separator}', essai suivant...")
                continue
            except Exception as e:
                logger.debug(f"Erreur inattendue avec l'encodage {encoding} et séparateur '{separator}': {e}")
                continue
    
    # Si aucun encodage ne fonctionne
    raise UnicodeDecodeError(f"Impossible de lire le fichier {file_path} avec les encodages testés: {encodings}")

def setup_worker_logging(worker_id, proxy):
    """Configure un wrapper de logging global pour capturer tous les logs du processus"""
    
    # Créer un formatage personnalisé avec l'ID du worker
    class WorkerFormatter(logging.Formatter):
        def __init__(self, worker_id, proxy):
            self.worker_id = worker_id
            self.proxy = proxy
            super().__init__(fmt='%(asctime)s - %(levelname)s - %(message)s')
        
        def format(self, record):
            # Préfixer tous les messages avec l'identifiant du worker
            original_msg = super().format(record)
            return f"[WORKER-{self.worker_id}|{self.proxy}] {original_msg}"
    
    # Obtenir le root logger et nettoyer sa configuration
    root_logger = logging.getLogger()
    
    # Supprimer TOUS les handlers existants (y compris ceux de basicConfig)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Supprimer aussi les handlers des loggers spécifiques
    for name in logging.Logger.manager.loggerDict:
        specific_logger = logging.getLogger(name)
        for handler in specific_logger.handlers[:]:
            specific_logger.removeHandler(handler)
    
    root_logger.setLevel(logging.INFO)
    
    # Handler pour la console avec notre formatage
    console_handler = logging.StreamHandler()
    console_formatter = WorkerFormatter(worker_id, proxy)
    console_handler.setFormatter(console_formatter)
    # Gérer l'encodage UTF-8 pour la console
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except:
            pass
    root_logger.addHandler(console_handler)
    
    # Handler pour fichier log séparé par worker avec encodage UTF-8
    log_file = f'logs/worker_{worker_id}.log'
    os.makedirs('logs', exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_formatter = WorkerFormatter(worker_id, proxy)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Réactiver les logs des modules externes qui étaient désactivés
    logging.getLogger('selenium').setLevel(logging.WARNING)  # Pas trop verbeux
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('undetected_chromedriver').setLevel(logging.INFO)
    
    # S'assurer que tous les loggers propagent vers le root
    for name in logging.Logger.manager.loggerDict:
        specific_logger = logging.getLogger(name)
        specific_logger.propagate = True
    
    return logging.getLogger(f'worker_{worker_id}')

def worker_process(proxy, ids_segment, worker_id):
    """Fonction worker qui sera exécutée dans chaque processus enfant"""
    
    # IMPORTANT: Configurer le logging AVANT d'importer les modules scraper
    # car ils utilisent basicConfig() à l'import
    logger = setup_worker_logging(worker_id, proxy)
    
    logger.info(f"Démarrage du worker - IDs à traiter: {ids_segment}")
    
    BP = None
    try:
        logger.info("Création de l'instance BrowserProxied...")
        # Créer l'objet BrowserProxied dans le processus enfant
        BP = BrowserProxied(proxy=proxy, headless=True, notifier=Notifier(get_config()))
        
        logger.info("Vérification du proxy...")
        BP.verify_proxy()
        
        logger.info(f"Chargement de {len(ids_segment)} IDs...")
        BP.load_ids(ids_segment)
        
        logger.info("Début du scraping des préfectures...")
        # Exécuter le scraping
        BP.scan_prefectures()
        
        logger.info("Scraping terminé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur dans le processus worker: {e}")
        logger.exception("Détails de l'erreur:")
    finally:
        # S'assurer que le driver est fermé proprement
        if BP is not None:
            try:
                logger.info("Fermeture du driver...")
                # Ajouter un petit délai avant la fermeture
                time.sleep(1)
                BP.quit()
                logger.info("Driver fermé avec succès")
                # Délai supplémentaire pour s'assurer que tous les processus sont terminés
                time.sleep(2)
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture du driver: {e}")
                # Essayer une fermeture forcée si nécessaire
                try:
                    if hasattr(BP, 'driver') and BP.driver:
                        BP.driver.quit()
                        logger.info("Fermeture forcée du driver réussie")
                except:
                    logger.warning("Impossible de fermer le driver, il pourrait déjà être fermé")

def run_scrapers(id_list, proxies):
    step = len(id_list) // len(proxies)
    processes = []
    
    logger.info(f"Lancement du scraping avec {len(proxies)} workers")
    logger.info(f"IDs à traiter: {id_list}")
    logger.info(f"Proxies: {proxies}")
    
    # Scinder la liste d'IDs en segments pour chaque proxy
    ids_segments = []
    for i in range(len(proxies)):
        start_idx = i * step
        end_idx = (i + 1) * step if i < len(proxies) - 1 else len(id_list)
        ids_segments.append(id_list[start_idx:end_idx])
    
    logger.info(f"Répartition des IDs par worker:")
    for i, (proxy, segment) in enumerate(zip(proxies, ids_segments)):
        logger.info(f" Worker {i+1} ({proxy}): {len(segment)} IDs - {segment}")
    
    # Créer et démarrer les processus
    for i, proxy in enumerate(proxies):
        if i < len(ids_segments) and ids_segments[i]:  # Vérifier qu'il y a des IDs à traiter
            logger.info(f"Démarrage du worker {i+1} avec proxy {proxy}")
            p = Process(target=worker_process, args=(proxy, ids_segments[i], i + 1))
            p.start()
            processes.append(p)
            time.sleep(10)  # Délai entre les démarrages
    
    logger.info(f"Attente de la fin de tous les workers...")
    # Attendre que tous les processus se terminent
    for i, p in enumerate(processes):
        logger.info(f"Attente du worker {i+1}...")
        p.join()
        logger.info(f"Worker {i+1} terminé")
    
    logger.info("Tous les workers ont terminé leur travail !")



if __name__ == "__main__":
    # 4 Read the CSV file
    data = read_csv_to_dict_list('./study_and_sorty/merged_inner.csv')

    logger.info(f"Loaded {len(data)} records from CSV.")
    
    id_list = [int(row['id']) for row in data if 'id' in row]
    
    PROXIES = [
        "5.45.36.49:5432",
        "84.200.208.39:5432",
        "194.53.140.80:5432",
        "res.proxy-seller.com:10000"
    ]

    
    run_scrapers(id_list[0:20], PROXIES)



