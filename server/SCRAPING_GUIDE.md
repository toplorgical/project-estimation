# 🕷️ Web Scraping System Guide

## Overview

The Toplorgical platform uses **Scrapy** to dynamically scrape construction material and equipment pricing from major UK suppliers.

## How It Works

```
┌─────────────────┐
│  Scrapy Service │ ──> Scrapes supplier websites
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    MongoDB      │ ──> Stores raw scraped data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django API     │ ──> Processes and stores in PostgreSQL/SQLite
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pricing Models │ ──> Makes data available to users
└─────────────────┘
```

## Suppliers Being Scraped

The system scrapes the following UK construction suppliers:

1. **Travis Perkins** - https://www.travisperkins.co.uk
2. **Wickes** - https://www.wickes.co.uk
3. **Screwfix** - https://www.screwfix.com
4. **Toolstation** - https://www.toolstation.com
5. **B&Q** - https://www.diy.com
6. **Homebase** - https://www.homebase.co.uk
7. **Buildbase** - https://www.buildbase.co.uk
8. **Jewson** - https://www.jewson.co.uk
9. **Selco** - https://www.selcobw.com

## Project Structure

```
scrapy_service/
├── scrapy.cfg                      # Scrapy configuration
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container for scraping service
└── pricing_scraper/
    ├── settings.py                 # Scrapy settings
    ├── items.py                    # Data structures (MaterialItem, MachineryItem)
    ├── pipelines.py                # Data processing pipelines
    ├── middlewares.py              # User agent rotation, proxies
    └── spiders/
        └── materials.py            # Spider implementations
```

## Running the Scraper

### Option 1: Run Locally (Without Docker)

#### 1. Install Scrapy Dependencies

```powershell
cd server\scrapy_service
pip install -r requirements.txt
```

#### 2. Run a Spider

```powershell
# Scrape all suppliers
scrapy crawl materials

# Scrape specific supplier (Travis Perkins)
scrapy crawl travis_perkins_materials

# Save output to JSON
scrapy crawl materials -o output.json

# Save to CSV
scrapy crawl materials -o output.csv
```

### Option 2: Run with Docker Compose

```powershell
cd server
docker-compose up scrapy
```

### Option 3: Schedule with Celery

The Django app can schedule scraping tasks using Celery:

```python
# In Django shell or management command
from pricing.tasks import trigger_scraping
trigger_scraping.delay()
```

## Data Flow

### 1. Scraping Phase

The spider visits supplier websites and extracts:

- **Materials**: Name, price, brand, SKU, specifications, availability
- **Pricing**: Current price, unit, location
- **Supplier**: Name, URL, contact info
- **Metadata**: Timestamp, images, descriptions

### 2. Validation Pipeline

```python
ValidationPipeline:
- Checks required fields (name, supplier)
- Validates price format
- Cleans text fields
- Filters invalid data
```

### 3. Deduplication Pipeline

```python
DuplicationPipeline:
- Creates unique identifier (name + supplier + SKU)
- Prevents duplicate items in same scraping session
```

### 4. Storage Pipelines

**MongoDB Pipeline** (Optional):
```python
MongoPipeline:
- Stores raw scraped data in MongoDB
- Useful for debugging and data analysis
- Can be disabled if not needed
```

**API Pipeline** (Primary):
```python
APIPipeline:
- Authenticates with Django API
- Sends data to /api/pricing/scraped-data/
- Creates/updates PriceData records
- Links to existing Materials/Machinery
```

## Configuration

### Scrapy Settings

Located in `scrapy_service/pricing_scraper/settings.py`:

```python
# Request delays (respect servers)
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Obey robots.txt
ROBOTSTXT_OBEY = True

# MongoDB (optional)
MONGODB_SERVER = 'mongodb://localhost:27017/'
MONGODB_DB = 'pricing_data'

# Django API
API_BASE_URL = 'http://localhost:8000/api/'
```

### Django Settings

The API endpoint that receives scraped data needs to be created.

## Creating the API Endpoint

You need to create an endpoint to receive scraped data from the scraper:

```python
# pricing/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PriceData, Supplier
from materials.models import Material, MaterialCategory

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_scraped_data(request):
    """Receive and process scraped pricing data"""
    data = request.data
    
    # Get or create supplier
    supplier, _ = Supplier.objects.get_or_create(
        name=data.get('supplier'),
        defaults={
            'website': data.get('supplier_url', ''),
            'is_active': True
        }
    )
    
    # Get or create material (if it doesn't exist yet)
    material = None
    if data.get('name') and data.get('category'):
        category, _ = MaterialCategory.objects.get_or_create(
            name=data.get('category')
        )
        
        material, created = Material.objects.get_or_create(
            sku=data.get('sku', ''),
            defaults={
                'name': data.get('name'),
                'category': category,
                'unit': data.get('unit', 'piece'),
                'brand': data.get('brand', ''),
                'description': data.get('description', ''),
                'specifications': data.get('specifications', {}),
            }
        )
    
    # Create price data
    price_data = PriceData.objects.create(
        material=material,
        supplier=supplier,
        price=data.get('price', 0),
        unit=data.get('unit', ''),
        in_stock=data.get('in_stock', True),
        location=data.get('location', ''),
        source_url=data.get('product_url', ''),
        sku=data.get('sku', ''),
        is_active=True
    )
    
    return Response({
        'status': 'success',
        'price_data_id': price_data.id
    }, status=status.HTTP_201_CREATED)
```

## Scheduled Scraping with Celery

### 1. Celery Configuration

Already configured in `toplorgical/celery.py` and `settings.py`

### 2. Schedule Periodic Tasks

```python
# pricing/tasks.py already has these tasks:

@shared_task
def trigger_scraping():
    """Trigger Scrapy spiders"""
    # Implementation needed based on your setup
    pass

@shared_task
def update_price_history():
    """Update daily price aggregations"""
    pass

@shared_task
def check_price_alerts():
    """Check user price alerts"""
    pass
```

### 3. Configure Celery Beat

Add to Django admin or configure in code:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'scrape-prices-daily': {
        'task': 'pricing.tasks.trigger_scraping',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM
    },
    'update-price-history-daily': {
        'task': 'pricing.tasks.update_price_history',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM
    },
    'check-alerts-hourly': {
        'task': 'pricing.tasks.check_price_alerts',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

## Testing the Scraper

### 1. Test Locally (No Database)

```powershell
cd server\scrapy_service

# Dry run - just print items
scrapy crawl materials -s ITEM_PIPELINES={}

# Save to file
scrapy crawl materials -o test.json -s ITEM_PIPELINES={}
```

### 2. Test with Django API

```powershell
# Start Django server
cd server
python manage.py runserver

# In another terminal, run scraper
cd scrapy_service
scrapy crawl materials
```

### 3. Check Results

```python
# Django shell
python manage.py shell

from pricing.models import PriceData
from materials.models import Material

# Check scraped materials
Material.objects.all()

# Check price data
PriceData.objects.all()

# Get latest prices
PriceData.objects.order_by('-created_at')[:10]
```

## Important Notes

### Legal & Ethical Considerations

⚠️ **Important**: Web scraping must comply with:

1. **Robots.txt**: The scraper respects `robots.txt` by default
2. **Terms of Service**: Check each supplier's terms
3. **Rate Limiting**: Configured with delays to avoid overloading servers
4. **Fair Use**: Use data for legitimate business purposes only

### Rate Limiting

Current settings:
- 3-second delay between requests
- Max 8 concurrent requests per domain
- Randomized delays
- Auto-throttle enabled

### Data Freshness

- Scrapers should run **daily** at off-peak hours
- Price history is aggregated daily
- Old data (>1 year) is automatically cleaned up

### Error Handling

The scraper handles:
- Network errors (retries)
- Invalid HTML structure (skips item)
- Missing data fields (uses defaults)
- Duplicate items (filters)
- Authentication failures (logs error)

## Troubleshooting

### Issue: Spider Not Finding Products

**Cause**: Website structure changed

**Solution**:
1. Open the supplier website in browser
2. Inspect the HTML structure
3. Update CSS selectors in spider
4. Test with `scrapy shell <url>`

### Issue: Authentication Failed

**Cause**: No scraper user in database

**Solution**:
```python
python manage.py shell

from authentication.models import User
User.objects.create_user(
    username='scraper',
    email='scraper@toplorgical.com',
    password='scraper_password',
    first_name='Scraper',
    last_name='Bot'
)
```

### Issue: MongoDB Connection Failed

**Solution**: MongoDB is optional
- Disable MongoPipeline in settings.py
- Or install and start MongoDB

### Issue: Too Many Requests (429 Error)

**Solution**: Increase delays in settings.py
```python
DOWNLOAD_DELAY = 5  # Increase from 3
CONCURRENT_REQUESTS_PER_DOMAIN = 4  # Decrease from 8
```

## Quick Start Commands

```powershell
# 1. Install dependencies
cd server\scrapy_service
pip install -r requirements.txt

# 2. Create scraper user
cd ..
python manage.py shell
# >>> from authentication.models import User
# >>> User.objects.create_user(username='scraper', email='scraper@toplorgical.com', password='scraper_password')

# 3. Run scraper
cd scrapy_service
scrapy crawl materials

# 4. Check results
cd ..
python manage.py shell
# >>> from pricing.models import PriceData
# >>> PriceData.objects.count()
```

## Next Steps

1. **Add API Endpoint**: Create the `receive_scraped_data` endpoint
2. **Create Scraper User**: Set up authentication for scraper
3. **Test Scraping**: Run a test scrape
4. **Schedule Tasks**: Set up Celery Beat for automated scraping
5. **Monitor Results**: Check Django admin for scraped data
6. **Customize Spiders**: Adjust selectors for specific suppliers

---

**Note**: This is a sophisticated web scraping system. Start with small tests and gradually scale up!
