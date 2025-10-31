from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import ExportJob
from .utils import generate_project_pdf, generate_estimate_pdf, generate_estimate_excel
import os
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_export(job_id):
    """Generate export file asynchronously"""
    try:
        job = ExportJob.objects.get(id=job_id)
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        # Generate file based on export type
        if job.export_type == 'project_pdf':
            content = generate_project_pdf(job.project, job.options)
            file_name = f"project_{job.project.id}_{job.project.name}.pdf"
        
        elif job.export_type == 'estimate_pdf':
            content = generate_estimate_pdf(job.estimate, job.options)
            file_name = f"estimate_{job.estimate.id}_{job.estimate.name}.pdf"
        
        elif job.export_type == 'estimate_excel':
            content = generate_estimate_excel(job.estimate, job.options)
            file_name = f"estimate_{job.estimate.id}_{job.estimate.name}.xlsx"
        
        else:
            raise ValueError(f"Unsupported export type: {job.export_type}")
        
        # Save file
        export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        file_path = os.path.join(export_dir, f"{job.id}_{file_name}")
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Update job
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.file_name = file_name
        job.file_path = file_path
        job.file_size = len(content)
        job.expires_at = timezone.now() + timedelta(days=7)  # Expire after 7 days
        job.progress = 100
        job.save()
        
        logger.info(f"Export job {job_id} completed successfully")
        
    except ExportJob.DoesNotExist:
        logger.error(f"Export job {job_id} not found")
    
    except Exception as e:
        logger.error(f"Export job {job_id} failed: {str(e)}")
        
        try:
            job = ExportJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
        except:
            pass


@shared_task
def cleanup_expired_exports():
    """Clean up expired export files"""
    expired_jobs = ExportJob.objects.filter(
        status='completed',
        expires_at__lt=timezone.now()
    )
    
    cleaned_count = 0
    for job in expired_jobs:
        try:
            # Delete file
            if job.file_path and os.path.exists(job.file_path):
                os.remove(job.file_path)
            
            # Delete job record
            job.delete()
            cleaned_count += 1
            
        except Exception as e:
            logger.error(f"Failed to clean up export job {job.id}: {str(e)}")
    
    logger.info(f"Cleaned up {cleaned_count} expired export files")
    return cleaned_count