# Toplorgical Construction Estimation Platform - Setup Guide

This guide will help you get the Toplorgical platform up and running on your local machine.

## 🏗️ Project Overview

**Toplorgical** is an AI-powered construction estimation platform with:
- **Backend**: Django REST Framework API
- **Frontend**: React + TypeScript with Vite
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Scraping Service**: Scrapy (optional)

## 📋 Prerequisites

### Required Software:
1. **Python 3.11+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
4. **Redis** - [Download for Windows](https://github.com/microsoftarchive/redis/releases)

### Optional (for Docker setup):
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)

---

## 🚀 Quick Start (Without Docker)

### Step 1: Database Setup

#### Install and Start PostgreSQL:
```powershell
# After installing PostgreSQL, start the service
# PostgreSQL should be running on port 5432 (default)

# Create the database (using psql or pgAdmin)
psql -U postgres
CREATE DATABASE toplorgical;
CREATE USER toplorgical WITH PASSWORD 'toplorgical123';
GRANT ALL PRIVILEGES ON DATABASE toplorgical TO toplorgical;
\q
```

#### Install and Start Redis:
```powershell
# Download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases

# Start Redis
redis-server
# Redis should be running on port 6379 (default)
```

### Step 2: Backend Setup

```powershell
# Navigate to server directory
cd server

# Create a virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify .env file exists and configure it
# The .env file should already be present with default values
# Edit if needed for your local setup

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow the prompts to create your admin account

# Create logs directory
New-Item -ItemType Directory -Force -Path logs

# Start the development server
python manage.py runserver
# Server will run on http://localhost:8000
```

### Step 3: Frontend Setup

```powershell
# Open a new terminal
# Navigate to client directory
cd client

# Install dependencies (using Bun or npm)
npm install
# OR if you have Bun installed
bun install

# Verify .env file exists
# The .env file should already be present with:
# VITE_API_BASE_URL=http://localhost:8000/api/v1

# Start the development server
npm run dev
# OR with Bun
bun dev

# Frontend will run on http://localhost:8080
```

### Step 4: Access the Application

1. **Frontend**: http://localhost:8080
2. **Backend API**: http://localhost:8000/api/v1/
3. **API Documentation**: http://localhost:8000/api/docs/
4. **Admin Panel**: http://localhost:8000/admin/

---

## 🐳 Docker Setup (Alternative)

If you prefer using Docker:

```powershell
# Navigate to server directory
cd server

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Check logs
docker-compose logs -f web

# Stop services
docker-compose down
```

Then run the frontend separately as described in Step 3 above.

---

## 🔧 Configuration

### Backend Environment Variables (server/.env)

```env
SECRET_KEY=django-insecure-change-this-in-production-12345678901234567890
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=toplorgical
DB_USER=toplorgical
DB_PASSWORD=toplorgical123
DB_HOST=localhost
DB_PORT=5433

REDIS_URL=redis://localhost:6379/0

# Optional: Stripe for payments
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

### Frontend Environment Variables (client/.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 📝 Testing the Setup

### 1. Test Backend API

Open your browser or use curl:

```powershell
# Health check
curl http://localhost:8000/health/

# API Documentation
# Visit: http://localhost:8000/api/docs/
```

### 2. Test Frontend

1. Visit http://localhost:8080
2. You should see the landing page
3. Click "Get Started" to register/login

### 3. Create a Test Estimate

1. Register a new account or login
2. Navigate to "New Estimate"
3. Fill out the project details
4. Generate an estimate
5. View the results with cost breakdown

---

## 🔍 Troubleshooting

### Backend Issues

**Problem: Port 8000 already in use**
```powershell
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Problem: Database connection error**
- Verify PostgreSQL is running: `pg_isready -U postgres`
- Check database credentials in `.env`
- Ensure database exists: `psql -U postgres -l`

**Problem: Redis connection error**
- Verify Redis is running: `redis-cli ping`
- Should return `PONG`

**Problem: ModuleNotFoundError**
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Problem: Port 8080 already in use**
```powershell
# Find and kill the process
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

**Problem: Module not found errors**
```powershell
# Clear node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

**Problem: API connection issues**
- Verify backend is running on http://localhost:8000
- Check CORS settings in backend settings.py
- Verify `.env` file has correct `VITE_API_BASE_URL`

---

## 🛠️ Development Workflow

### Running Tests

**Backend Tests:**
```powershell
cd server
python manage.py test
```

**Frontend Tests:**
```powershell
cd client
npm run test
```

### Database Migrations

When you modify models:

```powershell
cd server
python manage.py makemigrations
python manage.py migrate
```

### Code Formatting

**Backend:**
```powershell
cd server
pip install black
black .
```

**Frontend:**
```powershell
cd client
npm run lint
```

---

## 📚 Project Structure

```
project-estimation/
├── server/                  # Django Backend
│   ├── authentication/      # User auth & JWT
│   ├── projects/           # Project management
│   ├── materials/          # Materials catalog
│   ├── machinery/          # Equipment catalog
│   ├── pricing/            # Price tracking
│   ├── estimates/          # Estimation engine
│   ├── exports/            # PDF/Excel exports
│   ├── collaboration/      # Team features
│   ├── payments/           # Stripe integration
│   ├── toplorgical/        # Django settings
│   ├── manage.py           # Django CLI
│   ├── requirements.txt    # Python deps
│   └── docker-compose.yml  # Docker config
│
├── client/                  # React Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── contexts/       # React contexts
│   │   ├── hooks/          # Custom hooks
│   │   └── types/          # TypeScript types
│   ├── package.json        # Node deps
│   └── vite.config.ts      # Vite config
│
└── README.md               # This file
```

---

## 🎯 Next Steps

1. ✅ Complete the setup steps above
2. 📖 Review the API documentation at http://localhost:8000/api/docs/
3. 🧪 Create a test estimate to verify functionality
4. 💡 Explore the codebase and start customizing
5. 📊 Check out the Postman collection in `server/postman_collection.json`

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review the backend README: `server/README.md`
- Check Django logs: `server/logs/django.log`
- Check browser console for frontend errors

---

## 🔐 Security Notes

⚠️ **Important for Production:**

1. Change `SECRET_KEY` in `.env`
2. Set `DEBUG=False`
3. Configure proper `ALLOWED_HOSTS`
4. Use environment-specific credentials
5. Enable HTTPS
6. Set up proper database backups
7. Configure rate limiting
8. Add API key authentication for sensitive endpoints

---

## ✨ Features

- ✅ User Authentication (JWT)
- ✅ Project Management
- ✅ Cost Estimation Engine
- ✅ Material & Equipment Catalogs
- ✅ Real-time Price Tracking
- ✅ Export to PDF/Excel
- ✅ Team Collaboration
- ✅ Subscription Management (Stripe)
- ✅ API Documentation (Swagger)
- ✅ Responsive UI with Dark Mode

---

Happy Building! 🏗️✨
