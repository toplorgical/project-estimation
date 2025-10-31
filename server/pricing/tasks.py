from celery import shared_task
from django.utils import timezone
from django.db.models import Avg, Min, Max
from datetime import timedelta
from .models import PriceData, PriceHistory, PriceAlert
from materials.models import Material
from machinery.models import Machinery
import logging

logger = logging.getLogger(__name__)


@shared_task
def update_all_prices():
    """Update price history and check alerts"""
    logger.info("Starting price update task")
    
    # Update price history
    update_price_history()
    
    # Check price alerts
    check_price_alerts()
    
    logger.info("Price update task completed")


@shared_task
def update_price_history():
    """Update daily price history aggregations"""
    today = timezone.now().date()
    
    # Update material price history
    materials = Material.objects.filter(is_active=True)
    for material in materials:
        locations = PriceData.objects.filter(
            material=material,
            is_active=True
        ).values_list('location', flat=True).distinct()
        
        for location in locations:
            if not location:
                continue
                
            price_data = PriceData.objects.filter(
                material=material,
                location=location,
                is_active=True,
                created_at__date=today
            )
            
            if price_data.exists():
                aggregates = price_data.aggregate(
                    avg_price=Avg('price'),
                    min_price=Min('price'),
                    max_price=Max('price')
                )
                
                PriceHistory.objects.update_or_create(
                    material=material,
                    location=location,
                    date=today,
                    defaults={
                        'avg_price': aggregates['avg_price'],
                        'min_price': aggregates['min_price'],
                        'max_price': aggregates['max_price'],
                        'data_points': price_data.count()
                    }
                )
    
    # Update machinery price history
    machinery_items = Machinery.objects.filter(is_active=True)
    for machinery in machinery_items:
        locations = PriceData.objects.filter(
            machinery=machinery,
            is_active=True
        ).values_list('location', flat=True).distinct()
        
        for location in locations:
            if not location:
                continue
                
            price_data = PriceData.objects.filter(
                machinery=machinery,
                location=location,
                is_active=True,
                created_at__date=today
            )
            
            if price_data.exists():
                aggregates = price_data.aggregate(
                    avg_price=Avg('price'),
                    min_price=Min('price'),
                    max_price=Max('price')
                )
                
                PriceHistory.objects.update_or_create(
                    machinery=machinery,
                    location=location,
                    date=today,
                    defaults={
                        'avg_price': aggregates['avg_price'] or 0,
                        'min_price': aggregates['min_price'] or 0,
                        'max_price': aggregates['max_price'] or 0,
                        'data_points': price_data.count()
                    }
                )
    
    logger.info(f"Updated price history for {today}")


@shared_task
def check_price_alerts():
    """Check and trigger price alerts"""
    active_alerts = PriceAlert.objects.filter(is_active=True)
    
    for alert in active_alerts:
        try:
            # Get current price
            if alert.material:
                current_prices = PriceData.objects.filter(
                    material=alert.material,
                    is_active=True
                )
            elif alert.machinery:
                current_prices = PriceData.objects.filter(
                    machinery=alert.machinery,
                    is_active=True
                )
            else:
                continue
            
            # Filter by location if specified
            if alert.location:
                current_prices = current_prices.filter(location__icontains=alert.location)
            
            if not current_prices.exists():
                continue
            
            # Check alert conditions
            should_trigger = False
            
            if alert.alert_type == 'price_drop' and alert.threshold_price:
                min_price = current_prices.aggregate(Min('price'))['price__min']
                if min_price and min_price <= alert.threshold_price:
                    should_trigger = True
            
            elif alert.alert_type == 'price_increase' and alert.threshold_price:
                max_price = current_prices.aggregate(Max('price'))['price__max']
                if max_price and max_price >= alert.threshold_price:
                    should_trigger = True
            
            elif alert.alert_type == 'back_in_stock':
                if current_prices.filter(in_stock=True).exists():
                    should_trigger = True
            
            elif alert.alert_type == 'out_of_stock':
                if not current_prices.filter(in_stock=True).exists():
                    should_trigger = True
            
            # Trigger alert if conditions are met
            if should_trigger:
                # Update last triggered time
                alert.last_triggered = timezone.now()
                alert.save()
                
                # Send notification (implement email/push notification here)
                send_price_alert_notification.delay(alert.id)
                
                logger.info(f"Triggered alert {alert.id} for user {alert.user.id}")
        
        except Exception as e:
            logger.error(f"Error checking alert {alert.id}: {str(e)}")


@shared_task
def send_price_alert_notification(alert_id):
    """Send price alert notification to user"""
    try:
        alert = PriceAlert.objects.get(id=alert_id)
        
        # TODO: Implement email notification
        # For now, just log the notification
        item = alert.material or alert.machinery
        logger.info(f"Price alert notification: {alert.alert_type} for {item.name} - User: {alert.user.email}")
        
        # Here you would integrate with email service, push notifications, etc.
        
    except PriceAlert.DoesNotExist:
        logger.error(f"Price alert {alert_id} not found")


@shared_task
def trigger_scraping():
    """Trigger Scrapy spiders to collect new price data"""
    import requests
    import os
    
    # This would trigger the Scrapy service
    # For now, just log the action
    logger.info("Triggering price scraping...")
    
    # In a real implementation, you might:
    # 1. Make HTTP request to Scrapy service
    # 2. Use Scrapyd API to schedule spiders
    # 3. Use message queue to trigger scraping
    
    return "Scraping triggered"


@shared_task
def cleanup_old_price_data():
    """Clean up old price data to manage database size"""
    cutoff_date = timezone.now() - timedelta(days=365)  # Keep 1 year of data
    
    # Delete old price data
    deleted_count = PriceData.objects.filter(
        created_at__lt=cutoff_date,
        is_active=False
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old price data records")
    
    # Keep price history for longer (2 years)
    history_cutoff = timezone.now().date() - timedelta(days=730)
    history_deleted = PriceHistory.objects.filter(
        date__lt=history_cutoff
    ).delete()[0]
    
    logger.info(f"Cleaned up {history_deleted} old price history records")
    
    return f"Cleaned up {deleted_count} price data and {history_deleted} history records"