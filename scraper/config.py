#!/usr/bin/env python3
"""
Configuration simplifiée pour les drivers Chrome avec undetected_chromedriver
Version élégante et facile à utiliser
"""

import undetected_chromedriver as uc
import os
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class ChromeConfig:
    """Configuration simplifiée pour Chrome driver"""
    
    # Paramètres essentiels
    headless: bool = True
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    window_size: str = "1366,768"
    
    # Paramètres avancés optionnels
    enable_logging: bool = False
    anti_detection: bool = True
    
    def __post_init__(self):
        """Récupère les variables d'environnement automatiquement (sauf proxy)"""
        # Le proxy doit être passé explicitement en paramètre
        # Plus de récupération automatique via PROXY env var
        
        if self.user_agent is None:
            self.user_agent = os.environ.get("USER_AGENT", self._default_user_agent())
    
    def _default_user_agent(self) -> str:
        """User agent par défaut"""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    def create_driver(self) -> uc.Chrome:
        """Crée un driver Chrome configuré"""
        options = uc.ChromeOptions()
        
        # Configuration de base
        if self.user_agent:
            options.add_argument(f"--user-agent={self.user_agent}")
        
        if self.proxy:
            proxy_url = f"http://{self.proxy}" if not self.proxy.startswith('http') else self.proxy
            options.add_argument(f'--proxy-server={proxy_url}')
            logger.info(f"Proxy configuré: {proxy_url}")
        else:
            logger.info("Aucun proxy configuré")
        
        # Mode headless
        if self.headless:
            options.add_argument("--headless=new")
        
        # Arguments essentiels
        essential_args = [
            "--disable-gpu",
            "--no-sandbox",
            "--disable-notifications",
            "--disable-infobars", 
            "--disable-extensions",
            f"--window-size={self.window_size}",
            "--disable-dev-shm-usage"
        ]
        
        for arg in essential_args:
            options.add_argument(arg)
        
        # Anti-détection si activé (version compatible)
        if self.anti_detection:
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-features=VizDisplayCompositor")
            # Suppression des options expérimentales incompatibles
        
        # Logging si activé (version simplifiée)
        if self.enable_logging:
            options.add_argument("--enable-logging")
            options.add_argument("--v=1")
            # Suppression de loggingPrefs qui peut être incompatible
        
        # Créer le driver
        logger.info("Création du driver Chrome")
        driver = uc.Chrome(options=options) #, use_subprocess=True)
        
        # Scripts anti-détection
        if self.anti_detection:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        logger.info("Driver Chrome créé avec succès")
        return driver

# === CONFIGURATIONS RAPIDES ===

def get_config(headless: bool = True, proxy: Optional[str] = None, logging: bool = False) -> ChromeConfig:
    """Configuration rapide et simple"""
    return ChromeConfig(
        headless=headless,
        proxy=proxy,
        enable_logging=logging,
        anti_detection=True
    )

def visible_config(proxy: Optional[str] = None) -> ChromeConfig:
    """Configuration visible pour tests"""
    return get_config(headless=False, proxy=proxy, logging=True)

def stealth_config(proxy: Optional[str] = None) -> ChromeConfig:
    """Configuration furtive"""
    return get_config(headless=True, proxy=proxy, logging=False)

# === USAGE SIMPLE ===
def create_driver(headless: bool = True, proxy: Optional[str] = None, logging: bool = False) -> uc.Chrome:
    """Fonction directe pour créer un driver - ultra simple"""
    config = get_config(headless=headless, proxy=proxy, logging=logging)
    return config.create_driver()

if __name__ == "__main__":
    # Exemples d'usage simple
    print("=== CONFIGURATION CHROME SIMPLIFIÉE ===\n")
    
    # Usage le plus simple
    print("1. Driver simple:")
    print("   driver = create_driver()")
    print("   driver = create_driver(headless=False, proxy='5.45.36.49:5432')")
    
    print("\n2. Avec configuration:")
    print("   config = visible_config(proxy='5.45.36.49:5432')")
    print("   driver = config.create_driver()")
    
    print("\n3. Configuration personnalisée:")
    print("   config = ChromeConfig(headless=False, proxy='5.45.36.49:5432')")
    print("   driver = config.create_driver()")
