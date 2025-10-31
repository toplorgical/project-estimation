# 🏗️ Toplorgical - AI-Powered Construction Estimation Platform

> A comprehensive web application for construction project cost estimation, featuring real-time pricing, material/equipment catalogs, team collaboration, and detailed export capabilities.

## 🌟 Features

- **User Authentication & Authorization** - JWT-based secure authentication
- **Project Management** - Create and manage multiple construction projects
- **Material & Equipment Catalogs** - Extensive databases with pricing
- **Smart Cost Estimation** - AI-powered estimation engine with detailed breakdowns
- **Real-time Pricing** - Web scraping for up-to-date UK supplier pricing
- **Export Capabilities** - Generate PDF and Excel reports
- **Team Collaboration** - Share projects and collaborate with team members
- **Payment Processing** - Stripe integration for subscription management
- **API Documentation** - Interactive Swagger/ReDoc documentation
- **Dark Mode** - Modern UI with theme switching

## 📁 Project Structure

```
project-estimation/
├── client/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   ├── services/      # API service layer
│   │   └── contexts/      # React context providers
│   └── package.json
│
├── server/                 # Django REST Framework backend
│   ├── authentication/    # User auth & JWT
│   ├── projects/          # Project management
│   ├── materials/         # Material catalog
│   ├── machinery/         # Equipment catalog
│   ├── pricing/           # Price tracking & scraping
│   ├── estimates/         # Estimation engine
│   ├── exports/           # PDF/Excel generation
│   ├── collaboration/     # Team features
│   ├── payments/          # Stripe integration
│   └── toplorgical/       # Django settings
│
├── start.ps1              # Master launcher script
├── SETUP.md               # Detailed setup guide
└── CHECKLIST.md           # Pre-flight checklist
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional but recommended)

### Installation

1. **Clone the repository**
   ```powershell
   git clone <repository-url>
   cd project-estimation
   ```

2. **Set up the database**
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres
   
   -- Create database and user
   CREATE DATABASE toplorgical;
   CREATE USER toplorgical WITH PASSWORD 'toplorgical123';
   GRANT ALL PRIVILEGES ON DATABASE toplorgical TO toplorgical;
   ```

3. **Run the setup script**
   ```powershell
   .\start.ps1
   ```
   
   The script will:
   - Check prerequisites
   - Set up virtual environments
   - Install dependencies
   - Run migrations
   - Launch both backend and frontend

### Manual Setup

If you prefer manual setup, see **[CHECKLIST.md](CHECKLIST.md)** for step-by-step instructions.

## 🔧 Configuration

### Backend Environment (server/.env)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=toplorgical
DB_USER=toplorgical
DB_PASSWORD=toplorgical123
DB_HOST=localhost
DB_PORT=5433

REDIS_URL=redis://localhost:6379/0

# Optional: Stripe integration
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### Frontend Environment (client/.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 📚 API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Postman Collection**: `server/postman_collection.json`

### API Endpoints Overview

```
/api/v1/auth/          # Authentication (register, login, logout)
/api/v1/projects/      # Project management
/api/v1/materials/     # Material catalog
/api/v1/machinery/     # Equipment catalog
/api/v1/pricing/       # Price tracking
/api/v1/estimates/     # Cost estimation
/api/v1/exports/       # PDF/Excel export
/api/v1/collaboration/ # Team collaboration
/api/v1/payments/      # Stripe payments
```

## 🧪 Testing

### Backend Tests

```powershell
cd server
.\venv\Scripts\activate
python manage.py test
```

### Frontend Tests

```powershell
cd client
npm run test
```

## 📊 Tech Stack

### Backend
- **Framework**: Django 4.2.7 + Django REST Framework 3.14
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Task Queue**: Celery 5.3 + Celery Beat
- **Authentication**: JWT (Simple JWT 5.3)
- **API Docs**: drf-spectacular 0.26
- **Payments**: Stripe 6.7
- **Scraping**: Scrapy 2.11
- **Exports**: ReportLab 4.0 (PDF), OpenPyXL 3.1 (Excel)

### Frontend
- **Framework**: React 18.3 + TypeScript
- **Build Tool**: Vite 5.4
- **Routing**: React Router 6.20
- **State Management**: TanStack Query 5.8
- **UI Components**: Radix UI + Tailwind CSS 3.3
- **Forms**: React Hook Form 7.48
- **Charts**: Recharts 2.10
- **HTTP Client**: Axios 1.6

## 🎯 Development Workflow

### Starting Development

```powershell
# Start both backend and frontend
.\start.ps1

# OR start individually
cd server && .\start-local.ps1  # Backend only
cd client && .\start-local.ps1  # Frontend only
```

### Making Database Changes

```powershell
cd server
.\venv\Scripts\activate
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser

```powershell
cd server
.\venv\Scripts\activate
python manage.py createsuperuser
```

## 🐳 Docker Deployment

The project includes Docker configuration for containerized deployment:

```powershell
cd server
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

Services in Docker Compose:
- **db**: PostgreSQL 15
- **redis**: Redis 7
- **mongodb**: MongoDB 7 (for Scrapy)
- **web**: Django application
- **celery**: Task worker
- **celery-beat**: Scheduled tasks
- **scrapy**: Web scraping service

## 📝 Available Scripts

### Backend (server/)

```powershell
python manage.py runserver    # Start development server
python manage.py test          # Run tests
python manage.py migrate       # Apply migrations
python manage.py createsuperuser  # Create admin user
python manage.py shell         # Django shell
```

### Frontend (client/)

```powershell
npm run dev       # Start development server
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
npm run test      # Run tests
```

## 🔍 Troubleshooting

See **[SETUP.md](SETUP.md)** for detailed troubleshooting guide.

### Common Issues

**Database Connection Error**
- Ensure PostgreSQL is running
- Check credentials in `.env`
- Verify database exists

**Port Already in Use**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process
taskkill /PID <PID> /F
```

**Module Not Found**
```powershell
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## 🔐 Security

For production deployment:

1. Change `SECRET_KEY` in `.env`
2. Set `DEBUG=False`
3. Configure `ALLOWED_HOSTS` properly
4. Use environment-specific database credentials
5. Enable HTTPS
6. Set up proper CORS settings
7. Configure rate limiting
8. Regular security updates

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Comprehensive setup guide
- **[CHECKLIST.md](CHECKLIST.md)** - Pre-flight checklist
- **Backend README**: `server/README.md`
- **Frontend README**: `client/README.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📞 Support

For issues or questions:
- Review the documentation
- Check troubleshooting guide
- Submit an issue on GitHub

---

**Built with ❤️ for the construction industry**

🏗️ Happy Estimating! ✨