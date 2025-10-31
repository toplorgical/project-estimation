import scrapy
from datetime import datetime
from ..items import MaterialItem


class MaterialsSpider(scrapy.Spider):
    name = 'materials'
    allowed_domains = [
        'travisperkins.co.uk',
        'wickes.co.uk',
        'screwfix.com',
        'toolstation.com',
        'diy.com',  # B&Q
        'homebase.co.uk',
        'buildbase.co.uk',
        'jewson.co.uk',
        'selcobw.com',
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [
            'https://www.travisperkins.co.uk/building-materials',
            'https://www.wickes.co.uk/building-materials',
            'https://www.screwfix.com/c/building-materials',
            'https://www.toolstation.com/building-materials',
            'https://www.diy.com/departments/building-materials',
            'https://www.homebase.co.uk/building-materials',
            'https://www.buildbase.co.uk/building-materials',
            'https://www.jewson.co.uk/building-materials',
            'https://www.selcobw.com/building-materials',
        ]
    
    def parse(self, response):
        """Parse main category pages"""
        # Extract product links
        product_links = response.css('a[href*="product"]::attr(href)').getall()
        
        for link in product_links:
            yield response.follow(link, self.parse_product)
        
        # Follow pagination
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_product(self, response):
        """Parse individual product pages"""
        supplier_name = self.get_supplier_name(response.url)
        
        item = MaterialItem()
        item['name'] = response.css('h1::text').get()
        item['description'] = response.css('.product-description::text').get()
        item['price'] = response.css('.price::text').get()
        item['unit'] = response.css('.unit::text').get()
        item['brand'] = response.css('.brand::text').get()
        item['sku'] = response.css('.sku::text').get()
        item['supplier'] = supplier_name
        item['supplier_url'] = self.get_supplier_url(response.url)
        item['product_url'] = response.url
        item['scraped_at'] = datetime.now()
        
        # Extract specifications
        specs = {}
        for spec in response.css('.specifications li'):
            key = spec.css('.spec-name::text').get()
            value = spec.css('.spec-value::text').get()
            if key and value:
                specs[key.strip()] = value.strip()
        item['specifications'] = specs
        
        # Extract availability
        stock_text = response.css('.stock-info::text').get()
        item['in_stock'] = 'in stock' in stock_text.lower() if stock_text else False
        
        # Extract dimensions
        item['length'] = response.css('.length::text').get()
        item['width'] = response.css('.width::text').get()
        item['height'] = response.css('.height::text').get()
        item['weight'] = response.css('.weight::text').get()
        
        # Extract images
        item['image_urls'] = response.css('.product-images img::attr(src)').getall()
        
        # Determine category
        breadcrumbs = response.css('.breadcrumb a::text').getall()
        if len(breadcrumbs) > 1:
            item['category'] = breadcrumbs[-2]
        
        yield item
    
    def get_supplier_name(self, url):
        """Extract supplier name from URL"""
        if 'travisperkins' in url:
            return 'Travis Perkins'
        elif 'wickes' in url:
            return 'Wickes'
        elif 'screwfix' in url:
            return 'Screwfix'
        elif 'toolstation' in url:
            return 'Toolstation'
        elif 'diy.com' in url:
            return 'B&Q'
        elif 'homebase' in url:
            return 'Homebase'
        elif 'buildbase' in url:
            return 'Buildbase'
        elif 'jewson' in url:
            return 'Jewson'
        elif 'selcobw' in url:
            return 'Selco'
        return 'Unknown'
    
    def get_supplier_url(self, url):
        """Extract base supplier URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"


class TravisPerkinsMaterialsSpider(scrapy.Spider):
    name = 'travis_perkins_materials'
    allowed_domains = ['travisperkins.co.uk']
    start_urls = ['https://www.travisperkins.co.uk/building-materials']
    
    def parse(self, response):
        """Parse Travis Perkins specific structure"""
        # Extract category links
        category_links = response.css('.category-nav a::attr(href)').getall()
        
        for link in category_links:
            yield response.follow(link, self.parse_category)
    
    def parse_category(self, response):
        """Parse category page"""
        # Extract product links
        product_links = response.css('.product-tile a::attr(href)').getall()
        
        for link in product_links:
            yield response.follow(link, self.parse_product)
        
        # Follow pagination
        next_page = response.css('.pagination .next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_category)
    
    def parse_product(self, response):
        """Parse Travis Perkins product page"""
        item = MaterialItem()
        
        # Basic information
        item['name'] = response.css('.product-title h1::text').get()
        item['description'] = response.css('.product-description p::text').get()
        item['brand'] = response.css('.product-brand::text').get()
        item['sku'] = response.css('.product-code::text').get()
        
        # Pricing
        price_text = response.css('.price-current::text').get()
        item['price'] = price_text
        item['unit'] = response.css('.price-unit::text').get()
        
        # Supplier info
        item['supplier'] = 'Travis Perkins'
        item['supplier_url'] = 'https://www.travisperkins.co.uk'
        item['product_url'] = response.url
        
        # Availability
        availability = response.css('.availability-status::text').get()
        item['in_stock'] = 'available' in availability.lower() if availability else False
        
        # Category from breadcrumbs
        breadcrumbs = response.css('.breadcrumb-item a::text').getall()
        if breadcrumbs:
            item['category'] = breadcrumbs[-1]
        
        # Specifications
        specs = {}
        for row in response.css('.specifications-table tr'):
            key = row.css('td:first-child::text').get()
            value = row.css('td:last-child::text').get()
            if key and value:
                specs[key.strip()] = value.strip()
        item['specifications'] = specs
        
        # Images
        item['image_urls'] = response.css('.product-gallery img::attr(src)').getall()
        
        # Timestamp
        item['scraped_at'] = datetime.now()
        
        yield item