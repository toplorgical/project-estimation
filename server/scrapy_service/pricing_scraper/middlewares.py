import random
from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """Rotate user agents to avoid detection"""
    
    def __init__(self, user_agent=''):
        self.user_agent = user_agent
        self.ua = UserAgent()
    
    def process_request(self, request, spider):
        ua = self.ua.random
        request.headers['User-Agent'] = ua
        return None


class ProxyMiddleware:
    """Rotate proxies if needed"""
    
    def __init__(self):
        self.proxies = [
            # Add proxy servers here if needed
        ]
    
    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy
        return None


class DelayMiddleware:
    """Add random delays between requests"""
    
    def __init__(self):
        self.delays = [1, 2, 3, 4, 5]
    
    def process_request(self, request, spider):
        delay = random.choice(self.delays)
        request.meta['download_delay'] = delay
        return None