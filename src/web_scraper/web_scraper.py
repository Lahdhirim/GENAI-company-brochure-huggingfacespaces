import requests
from bs4 import BeautifulSoup
from src.config_loader.config_loader import WebScraperConfig
from src.utils.logging_config import logger

class WebScraper:
    """Extracts visible text content from a given URL."""

    def __init__(self, config: WebScraperConfig):
        self.timeout = config.timeout
        self.logger = logger

    def fetch_text(self, url: str) -> str:
        try:
            self.logger.info(f"Fetching content from URL: {url}")
            response = requests.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, "html.parser")
            self.logger.info(f"Fetched text from URL: {url}")

            for tag in soup(["script", "style", "img", "input"]):
                tag.decompose()

            return soup.get_text(separator="\n", strip=True)

        except Exception as e:
            self.logger.error(f"Failed to fetch text from URL: {url}, error: {str(e)}")
            return f"Error fetching text from URL: {e}"