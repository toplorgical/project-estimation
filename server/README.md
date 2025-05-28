Project Cost Estimation Application - Comprehensive User Guide
This guide explains how to use all functionalities of the Project Cost Estimation application, which combines machine learning and web scraping to provide accurate cost estimates for projects across various sectors.

Table of Contents
System Overview

Setting Up Projects

Adding Project Resources

Adding Labor Requirements

Cost Estimation Methods

Market Price Updates

Model Training

API Endpoints

Admin Functions

Best Practices

System Overview
The application provides three main approaches to cost estimation:

Machine Learning (ML) Estimation:

Uses historical project data to predict costs based on sector, type, and location

Becomes more accurate as more projects are completed

Provides confidence scores for predictions

Web Scraping Estimation:

Fetches current market prices for materials and labor

Updates project costs with real-time data

Supports multiple sectors (construction, IT, etc.)

Manual Estimation:

Allows users to input costs directly

Serves as fallback when automated methods aren't available

Setting Up Projects
Creating a New Project
Basic Information:

Navigate to "Projects" → "Create New Project"

Fill in:

Report name (e.g., "Downtown Office Building")

Project type (e.g., "Commercial Construction")

Location (e.g., "New York, NY")

Sector (select from dropdown)

Status (defaults to "Pending")

Sector Selection:

Choose the most relevant sector (critical for accurate estimation)

Common sectors include:

Construction/Building

Software/IT

Manufacturing

Infrastructure

Initial Save:

Save the project to create its record

You can now add resources and labor details

Adding Project Resources
For Construction Projects
Navigate to "Resources" tab in your project

Click "Add Resource"

Fill in:

Resource Type (e.g., "Building Materials")

Resource Name (e.g., "Concrete 3000psi")

Quantity (e.g., 500)

Unit (e.g., "cubic yards")

Unit Cost (your estimated cost)

Save - the system will later try to find current market prices

For IT/Software Projects
Add resources like:

"Cloud Services" - AWS/GCP instances

"Software Licenses" - Commercial software

"Third-party APIs" - External services

Adding Labor Requirements
Navigate to "Labor" tab in your project

Click "Add Labor"

Specify:

Labor Type (Skilled/Unskilled/Supervisor)

Quantity (number of workers)

Daily Rate (your estimated rate)

Days Required (duration)

The system will attempt to find current market rates for:

Construction workers

Software developers

Project managers

Other relevant roles

Cost Estimation Methods
Automatic Estimation (Recommended)
Navigate to project detail page

Click "Estimate Cost" button

System will:

First try ML estimation

If low confidence (<70%), try web scraping

Show which method was used

Display confidence percentage

Force Specific Method
Use the API endpoint with method parameter:

ml - Force machine learning

scraping - Force web scraping

manual - Use only entered costs

Viewing Estimates
Estimated cost appears on project dashboard

Breakdown available in "Estimation Details":

Method used

Confidence score

Resource-by-resource costs

Labor costs

Market Price Updates
Manual Update
On project page, click "Update Market Prices"

System will:

Scrape current prices for all resources

Find current labor rates

Update all costs

Recalculate total estimate

Automatic Updates
Configured to run daily at 5 AM

Updates all active ("In Progress") projects

Can be adjusted in Celery beat schedule

Price Sources
Construction: HomeAdvisor, local supplier sites

IT Services: Upwork, Glassdoor

Manufacturing: Industry-specific sources

View sources in:

Resource "Price Source" field

Labor "Rate Source" field

Model Training
Automatic Training
Runs weekly (Sunday 3 AM)

Uses all completed projects with actual costs

Only trains if sufficient new data exists

Manual Training
Navigate to Admin → Model Training

Click "Train Model Now"

System will:

Gather historical data

Train new model

Validate accuracy

Replace old model if better

Training Data Requirements
Minimum 10 completed projects

Should cover multiple:

Sectors

Project types

Locations

Actual costs must be recorded

API Endpoints
1. Estimate Project Cost
Endpoint: POST /api/projects/<project_id>/estimate/

Parameters:

method (optional): "ml", "scraping", or "auto"

Response:

json
{
  "status": "success",
  "estimated_cost": 125000.00,
  "method_used": "ml",
  "confidence": 0.85,
  "project_id": "a1b2c3d4..."
}
2. Train Model
Endpoint: POST /api/projects/train-model/

Response:

json
{
  "status": "success",
  "message": "Model training completed",
  "training_samples": 42,
  "mean_absolute_error": 1200.50
}
3. Update Market Prices
Endpoint: POST /api/projects/<project_id>/update-prices/

Response:

json
{
  "status": "success",
  "message": "Market prices updated",
  "resources_updated": 8,
  "labor_rates_updated": 3,
  "new_estimated_cost": 128750.00
}
Admin Functions
Sector Management
Add/Edit sectors to improve categorization

Set default resource categories per sector

Configure price sources per sector

Scraper Configuration
Manage scraping:

URLs

Selectors

Rate limits

Add new scrapers for:

New sectors

Geographic regions

Specialized materials/services

Model Monitoring
View model performance:

Accuracy metrics

Confidence trends

Feature importance

Compare model versions

Roll back to previous model if needed

Best Practices
For Accurate ML Estimates
Complete projects properly:

Set final "Actual Cost"

Mark status as "Completed"

Provide detailed project information:

Correct sector

Specific project type

Precise location

Regularly train the model

For Effective Scraping
Name resources specifically:

"2x4 Lumber" instead of "Wood"

"Senior Python Developer" instead of "Programmer"

Include locations when possible

Verify scraped prices periodically

General Recommendations
Start with Auto estimation, then refine

Use scraped prices as baseline for negotiations

Combine methods for critical projects:

Get ML estimate

Get scraped estimate

Compare and analyze differences

Document manual overrides with reasons

Troubleshooting
Common Issues
1. Low Confidence Estimates

Cause: Insufficient similar projects in history

Solution:

Add more completed projects

Try web scraping method

Adjust sector/project type to closest match

2. Failed Price Scraping

Cause: Website changes or geoblocking

Solution:

Try manual price update later

Use alternative resource names

Contact admin to update scraper config

3. Inaccurate ML Predictions

Cause: Outdated model or data drift

Solution:

Retrain model

Check for outliers in training data

Verify sector assignments

Advanced Features
Custom Scrapers
For specialized needs, admins can:

Add new scraper classes

Configure site-specific parsing

Set up proxies for geographic targeting

Sector-Specific Models
Option to train separate models for:

High-volume sectors

Unique cost structures

Geographic regions