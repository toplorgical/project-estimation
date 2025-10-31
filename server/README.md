# Toplorgical Backend

AI-powered construction estimation platform backend built with Django REST Framework and Scrapy.

## Features

- **Django REST API Backend** with JWT authentication
- **Multi-app architecture** for scalability
- **Scrapy-based web scraping** for UK suppliers
- **Real-time cost estimation** with rule-based logic
- **Stripe integration** for subscription management
- **Export functionality** (PDF/Excel)
- **Team collaboration** features
- **Docker containerization** for easy deployment

## Architecture

### Django Apps

1. **authentication** - User management and JWT auth
2. **projects** - Project CRUD and management
3. **materials** - Material catalog and pricing
4. **machinery** - Equipment catalog and pricing
5. **pricing** - Price tracking and real-time updates
6. **estimates** - Cost estimation engine
7. **exports** - PDF/Excel generation
8. **collaboration** - Team management
9. **payments** - Stripe integration

### Scrapy Service

- **Target suppliers**: Travis Perkins, Wickes, Screwfix, Toolstation, B&Q, Homebase, Buildbase, Jewson, Selco
- **Data collection**: Materials, machinery, pricing, availability
- **Scheduling**: Daily price updates, weekly catalog refresh
- **Data pipeline**: MongoDB → Django API → PostgreSQL

## Quick Start

### One-step init (simple setup)

This backend auto-initializes on start: it runs migrations, ensures a superuser, and seeds sample data once.

- Local dev (Windows):

```powershell
cd server
./scripts/dev_start.ps1 -Email admin@local -Password admin123 -UseSqlite
```

- Docker:

```powershell
cd server
docker compose up --build
```

The first start will:

- Create superuser from env vars (defaults: admin@local / admin123)
- Populate sample suppliers, materials, machinery, and price data once

You can customize the superuser by setting these env vars (compose already sets sensible defaults):

```
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_FIRST_NAME
DJANGO_SUPERUSER_LAST_NAME
```

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+
- MongoDB 7+

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd toplorgical-backend
```

2. Copy environment variables:

```bash
cp .env.example .env
```

3. Update `.env` with your configuration:

```bash
# Update database credentials, API keys, etc.
```

4. Start services with Docker Compose:

```bash
docker-compose up -d
```

5. Run migrations:

```bash
docker-compose exec web python manage.py migrate
```

6. Create superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

7. Load sample data:

```bash
docker-compose exec web python manage.py loaddata fixtures/sample_data.json
```

### Development Setup

1. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start development server:

```bash
python manage.py runserver
```

## API Documentation

### Authentication Endpoints

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - User profile

### Project Management

- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Materials & Machinery

- `GET /api/materials/` - List materials
- `GET /api/materials/search/` - Search materials
- `GET /api/machinery/` - List machinery
- `GET /api/machinery/search/` - Search machinery

### Pricing

- `GET /api/pricing/materials/{id}/history/` - Price history
- `GET /api/pricing/realtime/` - Real-time pricing

### Estimates

- `POST /api/estimates/generate/` - Generate estimate
- `GET /api/estimates/{id}/` - Estimate details
- `GET /api/estimates/{id}/substitutions/` - Alternative suggestions

### Interactive Documentation

Visit `http://localhost:8000/api/docs/` for Swagger UI documentation.

## Estimation Engine

### Rule-Based Calculations

1. **Material Calculations**:

   - Quantity = Area × Thickness × Waste Factor (10-15%)
   - Regional adjustments based on location multipliers

2. **Labor Estimation**:

   - Hours = Base Hours × Complexity × Location Factor

3. **Equipment Costs**:

   - Rental Rate × Duration + Transport + Setup

4. **Substitution Logic**:
   - Price threshold triggers alternative suggestions
   - Ranked by cost savings and availability

### Location Multipliers

- London: 1.3x
- Manchester: 1.1x
- Birmingham: 1.05x
- Scotland: 0.9x
- Wales: 0.95x

## Scrapy Configuration

### Spiders

- `materials` - General materials spider
- `travis_perkins_materials` - Travis Perkins specific
- `wickes_materials` - Wickes specific
- `screwfix_materials` - Screwfix specific

### Running Scrapers

```bash
# Run all material scrapers
docker-compose exec scrapy scrapy crawl materials

# Run specific supplier
docker-compose exec scrapy scrapy crawl travis_perkins_materials

# Schedule daily runs
docker-compose exec scrapy scrapy crawl materials -s JOBDIR=crawls/materials-1
```

## Database Schema

### Core Models

- **User** - Extended Django user with subscription info
- **Project** - Construction project details
- **Material** - Material catalog with specifications
- **Machinery** - Equipment catalog with specifications
- **PriceData** - Current and historical pricing
- **Estimate** - Cost estimates with breakdowns

### Key Relationships

- Projects have many Estimates
- Estimates have many MaterialItems and MachineryItems
- PriceData links to Materials/Machinery and Suppliers
- Users can collaborate on Projects

## Testing

### Run Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run with coverage
docker-compose exec web pytest --cov=. --cov-report=html

# Run specific app tests
docker-compose exec web python manage.py test authentication
```

### Test Categories

- **Unit Tests** - Model and utility testing
- **Integration Tests** - API endpoint testing
- **Scrapy Tests** - Spider functionality testing
- **End-to-End Tests** - Complete workflow testing

## Deployment

### Production Setup

1. Update environment variables for production:

```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECRET_KEY=your-production-secret-key
```

2. Configure SSL certificates
3. Set up proper database backups
4. Configure monitoring and logging

### Docker Production Build

```bash
# Build production image
docker build -t toplorgical-backend:latest .

# Run with production settings
docker run -d \
  --name toplorgical-backend \
  -p 8000:8000 \
  -e DEBUG=False \
  -e DATABASE_URL=postgres://user:pass@db:5433/toplorgical \
  toplorgical-backend:latest
```

## Monitoring

### Health Checks

- `GET /health/` - Application health
- `GET /health/db/` - Database connectivity
- `GET /health/redis/` - Redis connectivity

### Logging

- Application logs: `logs/django.log`
- Scrapy logs: `scrapy_service/logs/`
- Error tracking with structured logging

### Performance Monitoring

- Database query optimization
- API response time monitoring
- Cache hit rate tracking
- Scrapy success rate monitoring

## Security

### Implemented Security Measures

- JWT authentication with refresh tokens
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting
- HTTPS enforcement

### Security Checklist

- [ ] Regular security updates
- [ ] API key rotation
- [ ] Database encryption
- [ ] Backup encryption
- [ ] Access log monitoring

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Keep files under 200 lines
- Use meaningful commit messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Email: support@toplorgical.com
- Documentation: https://docs.toplorgical.com
