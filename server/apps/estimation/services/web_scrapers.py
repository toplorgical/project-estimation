import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from datetime import datetime
import logging
from django.conf import settings
from fake_useragent import UserAgent
import time
import json

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.proxies = getattr(settings, 'SCRAPING_PROXIES', None)
        self.timeout = 30
        self.retries = 3
        self.delay = 2  

    def fetch_page(self, url):
        """Generic page fetcher with retries"""
        for attempt in range(self.retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    proxies=self.proxies
                )
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.retries} attempts")
                    return None

class ConstructionMaterialScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.homeadvisor.com/cost/"
        self.price_pattern = re.compile(r'\$([\d,]+(\.\d{2})?)')

    def get_material_price(self, material_name, location=None):
        """Get current price for a construction material"""
        try:
            search_url = urljoin(self.base_url, material_name.lower().replace(' ', '-'))
            page_content = self.fetch_page(search_url)
            
            if not page_content:
                return None, None
                
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Try to find price range (specific to homeadvisor)
            price_range = soup.find('div', class_='cost-range')
            if price_range:
                prices = self.price_pattern.findall(price_range.get_text())
                if prices:
                    numeric_prices = [float(p[0].replace(',', '')) for p in prices]
                    avg_price = sum(numeric_prices) / len(numeric_prices)
                    return avg_price, search_url
            
            # Alternative parsing if the above fails
            national_avg = soup.find('span', class_='national-average')
            if national_avg:
                price_match = self.price_pattern.search(national_avg.get_text())
                if price_match:
                    return float(price_match.group(1).replace(',', '')), search_url
            
            return None, None
        except Exception as e:
            logger.error(f"Error scraping {material_name}: {str(e)}")
            return None, None

class LabourRateScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.payscale.com/research/US/Job="
        self.rate_pattern = re.compile(r'\$([\d,]+(\.\d{2})?)\/hr')

    def get_labour_rate(self, job_title, location=None):
        """Get current labour rate for a job title"""
        try:
            search_url = urljoin(self.base_url, job_title.replace(' ', '_'))
            page_content = self.fetch_page(search_url)
            
            if not page_content:
                return None, None
                
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Try to find hourly rate
            hourly_rate = soup.find('div', class_='paycharts__value')
            if hourly_rate:
                rate_match = self.rate_pattern.search(hourly_rate.get_text())
                if rate_match:
                    return float(rate_match.group(1).replace(',', '')), search_url
            
            return None, None
        except Exception as e:
            logger.error(f"Error scraping {job_title} rates: {str(e)}")
            return None, None

class ITServiceScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.upwork.com/services/"
        self.price_pattern = re.compile(r'\$([\d,]+(\.\d{2})?)')

    def get_service_price(self, service_name):
        """Get current price for IT services"""
        try:
            search_url = urljoin(self.base_url, service_name.lower().replace(' ', '-'))
            page_content = self.fetch_page(search_url)
            
            if not page_content:
                return None, None
                
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Try to find price cards
            price_cards = soup.find_all('div', class_='price-card')
            if price_cards:
                prices = []
                for card in price_cards:
                    price_match = self.price_pattern.search(card.get_text())
                    if price_match:
                        prices.append(float(price_match.group(1).replace(',', '')))
                
                if prices:
                    avg_price = sum(prices) / len(prices)
                    return avg_price, search_url
            
            return None, None
        except Exception as e:
            logger.error(f"Error scraping {service_name} prices: {str(e)}")
            return None, None



class ScraperFactory:
    @staticmethod
    def get_scraper(sector):
        """Factory method to get appropriate scraper based on sector"""
        if 'construction' in sector.lower() or 'building' in sector.lower():
            return ConstructionMaterialScraper()
        elif 'it' in sector.lower() or 'software' in sector.lower():
            return ITServiceScraper()
        else:
            return BaseScraper() 