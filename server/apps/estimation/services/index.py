from .ml_model import ProjectCostEstimator
from .web_scrapers import ScraperFactory
from django.db import transaction
from projects.models import Project, ProjectResources, ProjectLabour
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProjectEstimationService:
    def __init__(self):
        self.ml_estimator = ProjectCostEstimator()
        self.scraper_factory = ScraperFactory()

    def estimate_project_cost(self, project_id, method='auto'):
        """
        Estimate project cost using specified method
        Args:
            project_id: ID of the project to estimate
            method: 'ml' (machine learning), 'scraping', 'manual', or 'auto' (try both)
        Returns:
            tuple: (success: bool, estimated_cost: float, method_used: str)
        """
        try:
            project = Project.objects.get(pk=project_id)
            
            if method == 'auto':
                # Try ML first, then scraping if ML not confident
                ml_cost, ml_confidence = self._estimate_with_ml(project)
                if ml_confidence > 0.7:  # Confidence threshold
                    return True, ml_cost, 'ml'
                else:
                    scraping_cost = self._estimate_with_scraping(project)
                    if scraping_cost:
                        return True, scraping_cost, 'scraping'
                    elif ml_cost:  # Fall back to ML even if low confidence
                        return True, ml_cost, 'ml'
                    else:
                        return False, 0, 'none'
            
            elif method == 'ml':
                cost, confidence = self._estimate_with_ml(project)
                return bool(cost), cost or 0, 'ml'
            
            elif method == 'scraping':
                cost = self._estimate_with_scraping(project)
                return bool(cost), cost or 0, 'scraping'
            
            else:
                logger.error(f"Unknown estimation method: {method}")
                return False, 0, 'none'
                
        except Project.DoesNotExist:
            logger.error(f"Project with id {project_id} not found")
            return False, 0, 'none'
        except Exception as e:
            logger.error(f"Error estimating project cost: {str(e)}")
            return False, 0, 'none'

    def _estimate_with_ml(self, project):
        """Estimate project cost using machine learning model"""
        if not project.sector:
            logger.warning("Project has no sector assigned - ML estimation not possible")
            return None, 0.0
        
        # Get project size from labour records if available
        project_size = 0
        labour_records = project.project_labour.all()
        if labour_records.exists():
            project_size = sum(l.days_required for l in labour_records)
        
        estimated_cost, confidence = self.ml_estimator.predict_cost(
            sector=project.sector.name,
            project_type=project.project_type,
            project_location=project.project_location,
            project_size=project_size
        )
        
        if estimated_cost:
            # Update project with estimation data
            project.estimated_cost = estimated_cost
            project.estimation_method = 'ml'
            project.estimation_confidence = confidence
            project.estimation_metadata = {
                'sector': project.sector.name,
                'project_type': project.project_type,
                'location': project.project_location,
                'size': project_size,
                'confidence': confidence
            }
            project.save()
        
        return estimated_cost, confidence

    def _estimate_with_scraping(self, project):
        """Estimate project cost by scraping current prices for resources and labour"""
        total_cost = 0
        updated_resources = []
        updated_labour = []
        
        # Get appropriate scraper for the project's sector
        scraper = self.scraper_factory.get_scraper(project.sector.name if project.sector else 'generic')
        
        # Estimate resources costs
        resources = project.project_resources.all()
        for resource in resources:
            if resource.resource_category:
                # Try to get current market price
                current_price, source = scraper.get_material_price(
                    resource.resource_name or resource.resource_type,
                    project.project_location
                )
                
                if current_price:
                    resource.current_market_price = current_price
                    resource.price_source = source
                    resource.price_last_updated = datetime.now()
                    updated_resources.append(resource)
                    total_cost += float(resource.total_cost)
                else:
                    # Use manual price if scraping fails
                    total_cost += float(resource.total_cost)
            else:
                # No category - just use manual price
                total_cost += float(resource.total_cost)
        
        # Estimate labour costs
        labour_records = project.project_labour.all()
        for labour in labour_records:
            job_title = f"{labour.labour_type} {project.sector.name if project.sector else 'worker'}"
            current_rate, source = scraper.get_labour_rate(
                job_title,
                project.project_location
            )
            
            if current_rate:
                labour.current_market_rate = current_rate
                labour.rate_source = source
                labour.rate_last_updated = datetime.now()
                updated_labour.append(labour)
                total_cost += float(labour.total_cost)
            else:
                # Use manual rate if scraping fails
                total_cost += float(labour.total_cost)
        
        # Bulk update changed records
        if updated_resources:
            ProjectResources.objects.bulk_update(
                updated_resources,
                ['current_market_price', 'price_source', 'price_last_updated']
            )
        
        if updated_labour:
            ProjectLabour.objects.bulk_update(
                updated_labour,
                ['current_market_rate', 'rate_source', 'rate_last_updated']
            )
        
        if total_cost > 0:
            # Update project with estimation data
            project.estimated_cost = total_cost
            project.estimation_method = 'scraping'
            project.estimation_confidence = 0.8  # Default confidence for scraping
            project.estimation_metadata = {
                'resources_updated': len(updated_resources),
                'labour_updated': len(updated_labour),
                'total_items': len(resources) + len(labour_records)
            }
            project.save()
        
        return total_cost if total_cost > 0 else None

    def train_ml_model(self):
        """Train the ML model with historical project data"""
        try:
            # Get completed projects with actual costs
            training_data = Project.objects.filter(
                status='completed',
                actual_cost__isnull=False,
                sector__isnull=False
            ).values(
                'sector__name',
                'project_type',
                'project_location',
                'estimation_metadata__size',
                'actual_cost'
            )
            
            if not training_data:
                logger.warning("No training data available")
                return False
            
            # Convert to DataFrame
            import pandas as pd
            df = pd.DataFrame.from_records(training_data)
            df.rename(columns={
                'sector__name': 'sector',
                'estimation_metadata__size': 'project_size'
            }, inplace=True)
            
            # Fill missing project sizes with median
            if 'project_size' in df.columns:
                df['project_size'].fillna(df['project_size'].median(), inplace=True)
            else:
                df['project_size'] = 1  # Default size
            
            return self.ml_estimator.train_model(df)
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False