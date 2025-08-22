#!/usr/bin/env python3
"""
Exemple d'utilisation du package scraper depuis un autre dossier
"""

import sys
import os
from pathlib import Path

# === MÉTHODE 1: Ajouter le chemin manuellement ===
def setup_scraper_path():
    """Ajoute le chemin du package scraper au PYTHONPATH"""
    # Chemin vers le dossier contenant le package scraper
    scraper_parent_dir = Path(__file__).parent
    
    # Ajouter au PYTHONPATH
    if str(scraper_parent_dir) not in sys.path:
        sys.path.insert(0, str(scraper_parent_dir))
        print(f"✅ Chemin ajouté: {scraper_parent_dir}")

# === MÉTHODE 2: Import avec gestion d'erreur ===
def import_scraper():
    """Importe le package scraper avec gestion d'erreur"""
    try:
        # Essayer l'import direct
        from scraper import BrowserProxied, get_config
        print("✅ Import direct réussi")
        return BrowserProxied, get_config
    except ImportError:
        print("⚠️ Import direct échoué, ajout du chemin...")
        setup_scraper_path()
        from scraper import BrowserProxied, get_config
        print("✅ Import avec chemin réussi")
        return BrowserProxied, get_config

# === EXEMPLE D'UTILISATION ===
def main():
    """Exemple d'utilisation du scraper depuis un autre dossier"""
    print("=== EXEMPLE D'UTILISATION DU PACKAGE SCRAPER ===")
    
    # Importer les classes
    BrowserProxied, get_config = import_scraper()
    
    # Utiliser le scraper
    proxy = "5.45.36.49:5432"
    browser = BrowserProxied(proxy=proxy, headless=False)
    
    print(f"✅ BrowserProxied créé avec proxy: {proxy}")
    
    print("✅ Package scraper utilisable!")

if __name__ == "__main__":
    main()
