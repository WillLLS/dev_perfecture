import undetected_chromedriver as uc
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import logger

# Configure undetected-chromedriver
logger.info("Configuring Chrome options")
options = uc.ChromeOptions()

# User-Agent réaliste par défaut
default_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
user_agent = os.environ.get("USER_AGENT", default_user_agent)
options.add_argument(f"--user-agent={user_agent}")

# Proxy support
proxy = os.environ.get("PROXY")
if proxy:
    logger.info(f"Utilisation du proxy : {proxy}")
    options.add_argument(f'--proxy-server={proxy}')

options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--window-size=1366,768")

# Gestion des cookies : le profil utilisateur permet de conserver les cookies
#user_data_dir = os.path.expanduser("~") + "/chrome_profile"
#options.add_argument(f'--user-data-dir={user_data_dir}')

logger.info("Initializing Chrome driver")
driver = uc.Chrome(
    options=options,
    #user_data_dir=user_data_dir,
    use_subprocess=True
    #version_main=138  # Spécifier une version stable de Chrome
)


