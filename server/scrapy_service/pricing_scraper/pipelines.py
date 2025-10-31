import pymongo
import requests
from datetime import datetime
from itemadapter import ItemAdapter


class ValidationPipeline:
    """Validate scraped items"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Check required fields
        required_fields = ['name', 'supplier']
        for field in required_fields:
            if not adapter.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate price
        price = adapter.get('price')
        if price is not None:
            try:
                float(price)
            except (ValueError, TypeError):
                adapter['price'] = None
        
        # Clean and validate text fields
        text_fields = ['name', 'description', 'brand', 'category']
        for field in text_fields:
            value = adapter.get(field)
            if value:
                adapter[field] = str(value).strip()
        
        return item


class DuplicationPipeline:
    """Remove duplicate items"""
    
    def __init__(self):
        self.seen_items = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Create unique identifier
        identifier = (
            adapter.get('name', '').lower(),
            adapter.get('supplier', '').lower(),
            adapter.get('sku', '').lower()
        )
        
        if identifier in self.seen_items:
            raise ValueError(f"Duplicate item: {identifier}")
        
        self.seen_items.add(identifier)
        return item


class MongoPipeline:
    """Store items in MongoDB"""
    
    def __init__(self, mongo_server, mongo_db, mongo_collection):
        self.mongo_server = mongo_server
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.client = None
        self.db = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_server=crawler.settings.get('MONGODB_SERVER'),
            mongo_db=crawler.settings.get('MONGODB_DB'),
            mongo_collection=crawler.settings.get('MONGODB_COLLECTION')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_server)
        self.db = self.client[self.mongo_db]
    
    def close_spider(self, spider):
        if self.client:
            self.client.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Add metadata
        adapter['scraped_at'] = datetime.now()
        adapter['spider_name'] = spider.name
        
        # Insert into MongoDB
        collection = self.db[self.mongo_collection]
        collection.insert_one(adapter.asdict())
        
        return item


class APIPipeline:
    """Send processed items to Django API"""
    
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.auth_token = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            api_base_url=crawler.settings.get('API_BASE_URL')
        )
    
    def open_spider(self, spider):
        # Authenticate with API
        try:
            response = self.session.post(
                f"{self.api_base_url}auth/login/",
                json={
                    'email': 'scraper@toplorgical.com',
                    'password': 'scraper_password'
                }
            )
            if response.status_code == 200:
                self.auth_token = response.json().get('access')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
        except Exception as e:
            spider.logger.error(f"Failed to authenticate with API: {e}")
    
    def process_item(self, item, spider):
        if not self.auth_token:
            return item
        
        adapter = ItemAdapter(item)
        
        # Prepare data for API
        api_data = {
            'name': adapter.get('name'),
            'description': adapter.get('description'),
            'category': adapter.get('category'),
            'brand': adapter.get('brand'),
            'sku': adapter.get('sku'),
            'unit': adapter.get('unit'),
            'specifications': adapter.get('specifications', {}),
            'price': adapter.get('price'),
            'supplier': adapter.get('supplier'),
            'supplier_url': adapter.get('supplier_url'),
            'product_url': adapter.get('product_url'),
            'in_stock': adapter.get('in_stock'),
            'location': adapter.get('location'),
            'length': adapter.get('length'),
            'width': adapter.get('width'),
            'height': adapter.get('height'),
            'weight': adapter.get('weight'),
        }
        
        # Remove None values
        api_data = {k: v for k, v in api_data.items() if v is not None}
        
        try:
            # Send to pricing endpoint
            response = self.session.post(
                f"{self.api_base_url}pricing/scraped-data/",
                json=api_data
            )
            
            if response.status_code not in [200, 201]:
                spider.logger.error(
                    f"Failed to send item to API: {response.status_code} - {response.text}"
                )
        except Exception as e:
            spider.logger.error(f"Error sending item to API: {e}")
        
        return item