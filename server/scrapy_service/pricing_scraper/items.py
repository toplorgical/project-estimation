import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Compose
from w3lib.html import remove_tags
import re


def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return None
    text = remove_tags(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_price(price_str):
    """Parse price string to float"""
    if not price_str:
        return None
    
    # Remove currency symbols and extra spaces
    price_str = re.sub(r'[£$€,\s]', '', price_str)
    
    # Extract numeric value
    match = re.search(r'(\d+\.?\d*)', price_str)
    if match:
        return float(match.group(1))
    return None


class MaterialItem(scrapy.Item):
    # Basic information
    name = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    category = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    brand = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    sku = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    
    # Pricing information
    price = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    unit = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    
    # Supplier information
    supplier = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    supplier_url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    product_url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    
    # Availability
    in_stock = scrapy.Field(
        output_processor=TakeFirst()
    )
    stock_quantity = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    # Location
    location = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    
    # Specifications
    specifications = scrapy.Field()
    
    # Dimensions
    length = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    width = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    height = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    weight = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    
    # Metadata
    scraped_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    image_urls = scrapy.Field()


class MachineryItem(scrapy.Item):
    # Basic information
    name = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    category = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    brand = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    model = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    
    # Pricing information
    rental_price_daily = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    rental_price_weekly = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    purchase_price = scrapy.Field(
        input_processor=MapCompose(parse_price),
        output_processor=TakeFirst()
    )
    
    # Supplier information
    supplier = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    supplier_url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    product_url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    
    # Availability
    available = scrapy.Field(
        output_processor=TakeFirst()
    )
    location = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    
    # Specifications
    specifications = scrapy.Field()
    power = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    fuel_type = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )
    
    # Metadata
    scraped_at = scrapy.Field(
        output_processor=TakeFirst()
    )
    image_urls = scrapy.Field()