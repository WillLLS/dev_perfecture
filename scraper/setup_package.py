#!/usr/bin/env python3
"""
Script d'installation simple pour le package scraper
"""

import os
import sys
from pathlib import Path

def setup_scraper_package():
    """Configure le package scraper pour être importable depuis n'importe où"""
    
    # Chemin du dossier scraper
    scraper_dir = Path(__file__).parent.absolute()
    
    # Ajouter le dossier parent au PYTHONPATH
    parent_dir = scraper_dir.parent
    
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
        print(f"✅ Ajouté au PYTHONPATH: {parent_dir}")
    
    # Vérifier que l'import fonctionne
    try:
        from scraper import BrowserProxied
        print("✅ Import du package scraper réussi!")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

if __name__ == "__main__":
    setup_scraper_package()
