BOT_NAME = 'pricing_scraper'

SPIDER_MODULES = ['pricing_scraper.spiders']
NEWSPIDER_MODULE = 'pricing_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure delays for requests
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Configure pipelines
ITEM_PIPELINES = {
    'pricing_scraper.pipelines.ValidationPipeline': 300,
    'pricing_scraper.pipelines.DuplicationPipeline': 400,
    'pricing_scraper.pipelines.MongoPipeline': 500,
    'pricing_scraper.pipelines.APIPipeline': 600,
}

# Configure user agents
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

DOWNLOADER_MIDDLEWARES = {
    'pricing_scraper.middlewares.RotateUserAgentMiddleware': 400,
    'pricing_scraper.middlewares.ProxyMiddleware': 410,
}

# MongoDB Configuration
MONGODB_SERVER = 'mongodb://toplorgical:toplorgical123@localhost:27017/'
MONGODB_DB = 'pricing_data'
MONGODB_COLLECTION = 'scraped_items'

# API Configuration
API_BASE_URL = 'http://localhost:8000/api/'
API_TOKEN = None  # Will be set dynamically

# Logging
LOG_LEVEL = 'INFO'

# AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'