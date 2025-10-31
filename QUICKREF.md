# 🚀 Toplorgical - Quick Reference Card

## ⚡ Quick Start (One Command)

```powershell
.\start.ps1
```

## 📋 Essential Commands

### System Verification
```powershell
.\verify.ps1                    # Check if system is ready
```

### Backend Commands
```powershell
cd server
.\start-local.ps1               # Start backend with checks
python manage.py runserver      # Start backend (manual)
python manage.py migrate        # Run database migrations
python manage.py createsuperuser # Create admin account
python manage.py test           # Run tests
```

### Frontend Commands
```powershell
cd client
.\start-local.ps1               # Start frontend with checks
npm run dev                     # Start frontend (manual)
npm run build                   # Build for production
npm run test                    # Run tests
```

### Docker Commands
```powershell
cd server
docker-compose up -d            # Start all services
docker-compose down             # Stop all services
docker-compose logs -f web      # View backend logs
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 🌐 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8080 | Main application |
| Backend API | http://localhost:8000/api/v1/ | REST API |
| Health Check | http://localhost:8000/health/ | Server status |
| API Docs (Swagger) | http://localhost:8000/api/docs/ | Interactive API docs |
| API Docs (ReDoc) | http://localhost:8000/api/redoc/ | Alternative API docs |
| Admin Panel | http://localhost:8000/admin/ | Django admin |

## 🔧 Configuration Files

### Backend (.env location: server/.env)
```env
# Essential variables
DB_NAME=toplorgical
DB_USER=toplorgical
DB_PASSWORD=toplorgical123
DB_HOST=localhost
DB_PORT=5433
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=True
```

### Frontend (.env location: client/.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 🐛 Quick Troubleshooting

### Port Already in Use
```powershell
# Find process
netstat -ano | findstr :8000
# Kill process (replace <PID>)
taskkill /PID <PID> /F
```

### Database Connection Failed
```powershell
# Check PostgreSQL is running
pg_isready -U postgres
# Restart PostgreSQL service
# Verify credentials in .env
```

### Module Not Found
```powershell
# Backend
cd server
.\venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd client
npm install
```

### Reset Everything
```powershell
# Backend
cd server
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd client
Remove-Item -Recurse -Force node_modules
npm install
```

## 📦 Dependencies Overview

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional)

### Backend Stack
- Django 4.2.7
- Django REST Framework 3.14
- PostgreSQL
- Redis
- Celery
- JWT Authentication
- Stripe

### Frontend Stack
- React 18.3
- TypeScript
- Vite 5.4
- Tailwind CSS
- React Router
- TanStack Query

## 📁 Project Structure

```
project-estimation/
├── start.ps1              ← Start everything
├── verify.ps1             ← Check system
├── SETUP.md               ← Full setup guide
├── CHECKLIST.md           ← Setup checklist
├── ANALYSIS.md            ← Project analysis
├── server/
│   ├── start-local.ps1    ← Start backend
│   ├── .env               ← Backend config
│   ├── manage.py          ← Django CLI
│   ├── requirements.txt   ← Python deps
│   └── [Django apps]/
└── client/
    ├── start-local.ps1    ← Start frontend
    ├── .env               ← Frontend config
    ├── package.json       ← Node deps
    └── src/
```

## 🔑 Key Features

✅ User Authentication (JWT)
✅ Project Management
✅ Material & Equipment Catalogs
✅ Cost Estimation Engine
✅ Real-time Pricing
✅ PDF & Excel Export
✅ Team Collaboration
✅ Stripe Payments
✅ API Documentation
✅ Dark Mode UI

## 📖 Documentation

| File | Description |
|------|-------------|
| README.md | Project overview |
| SETUP.md | Detailed setup guide |
| CHECKLIST.md | Pre-flight checklist |
| ANALYSIS.md | Project analysis summary |
| QUICKREF.md | This quick reference |

## 🎯 First Time Setup

1. Run verification: `.\verify.ps1`
2. Create database (if needed)
3. Run launcher: `.\start.ps1`
4. Create superuser: `cd server; .\venv\Scripts\activate; python manage.py createsuperuser`
5. Access frontend: http://localhost:8080
6. Access admin: http://localhost:8000/admin/

## 🧪 Testing

### Test Backend
```powershell
cd server
.\venv\Scripts\activate
python manage.py test
```

### Test Frontend
```powershell
cd client
npm run test
```

### Test API
- Import `server/postman_collection.json` into Postman
- 90+ endpoints with tests

## 🔒 Security Checklist (Production)

- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use strong passwords
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable logging
- [ ] Regular updates

## 💡 Tips

- Use `.\start.ps1` for easy startup
- Check `.\verify.ps1` before starting
- Frontend auto-reloads on changes
- Backend auto-reloads with runserver
- API docs are interactive (try them!)
- Use Postman collection for API testing
- Check logs for debugging
- PostgreSQL port: 5432 (server), 5433 (mapped)

## 🆘 Need Help?

1. Run `.\verify.ps1` to check system
2. See SETUP.md for detailed guide
3. Check CHECKLIST.md for steps
4. Review ANALYSIS.md for overview
5. Check logs: `server/logs/django.log`
6. Browser console for frontend errors

## 📊 API Endpoints (Main)

```
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/
POST   /api/v1/auth/logout/
GET    /api/v1/auth/profile/

GET    /api/v1/projects/
POST   /api/v1/projects/
GET    /api/v1/projects/{id}/
PUT    /api/v1/projects/{id}/
DELETE /api/v1/projects/{id}/

GET    /api/v1/materials/
GET    /api/v1/machinery/
GET    /api/v1/estimates/
POST   /api/v1/exports/pdf/
POST   /api/v1/exports/excel/
```

See http://localhost:8000/api/docs/ for complete list.

---

**Ready?** Run: `.\start.ps1` 🚀
