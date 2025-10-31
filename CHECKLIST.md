# Quick Start Checklist for Toplorgical Platform

## ✅ Pre-flight Checklist

Complete these steps before running the application:

### 1. Install Required Software

- [ ] **Python 3.11+** installed and in PATH
  ```powershell
  python --version  # Should show 3.11 or higher
  ```

- [ ] **Node.js 18+** installed and in PATH
  ```powershell
  node --version  # Should show v18 or higher
  npm --version   # Should show 9 or higher
  ```

- [ ] **PostgreSQL 15+** installed and running
  ```powershell
  # Check if PostgreSQL is running
  Test-NetConnection -ComputerName localhost -Port 5432
  ```

- [ ] **Redis** installed and running (Optional but recommended)
  ```powershell
  # Check if Redis is running
  Test-NetConnection -ComputerName localhost -Port 6379
  ```

### 2. Database Setup

- [ ] Create PostgreSQL database and user
  ```sql
  -- Connect to PostgreSQL as postgres user
  psql -U postgres
  
  -- Run these commands
  CREATE DATABASE toplorgical;
  CREATE USER toplorgical WITH PASSWORD 'toplorgical123';
  GRANT ALL PRIVILEGES ON DATABASE toplorgical TO toplorgical;
  \q
  ```

- [ ] Verify database connection
  ```powershell
  psql -U toplorgical -d toplorgical -h localhost -p 5432
  # Enter password: toplorgical123
  # Should connect successfully, then \q to quit
  ```

### 3. Backend Configuration

- [ ] Verify `.env` file exists in `server/` directory
  ```powershell
  cd server
  Test-Path .env  # Should return True
  ```

- [ ] Check `.env` file content (should have these variables):
  ```
  SECRET_KEY=your-secret-key
  DEBUG=True
  DB_NAME=toplorgical
  DB_USER=toplorgical
  DB_PASSWORD=toplorgical123
  DB_HOST=localhost
  DB_PORT=5433
  REDIS_URL=redis://localhost:6379/0
  ```

- [ ] Create virtual environment (if not exists)
  ```powershell
  cd server
  python -m venv venv
  ```

- [ ] Install Python dependencies
  ```powershell
  .\venv\Scripts\activate
  pip install -r requirements.txt
  ```

- [ ] Run database migrations
  ```powershell
  python manage.py migrate
  ```

- [ ] Create superuser account
  ```powershell
  python manage.py createsuperuser
  # Follow prompts to create admin account
  ```

### 4. Frontend Configuration

- [ ] Verify `.env` file exists in `client/` directory
  ```powershell
  cd client
  Test-Path .env  # Should return True
  ```

- [ ] Check `.env` file content:
  ```
  VITE_API_BASE_URL=http://localhost:8000/api/v1
  ```

- [ ] Install Node.js dependencies
  ```powershell
  cd client
  npm install
  # OR if you have Bun: bun install
  ```

### 5. Test Individual Components

- [ ] Test Backend
  ```powershell
  cd server
  .\venv\Scripts\activate
  python manage.py runserver
  # Should start on http://localhost:8000
  # Visit http://localhost:8000/health/ to verify
  ```

- [ ] Test Frontend (in a new terminal)
  ```powershell
  cd client
  npm run dev
  # Should start on http://localhost:8080
  # Visit in browser to verify
  ```

---

## 🚀 Quick Start Commands

Once all prerequisites are met:

### Option 1: Use the Master Launcher (Easiest)

```powershell
# From project root
.\start.ps1
```

This will:
- Check prerequisites
- Let you choose what to start
- Launch services in separate windows

### Option 2: Use Individual Scripts

**Backend:**
```powershell
cd server
.\start-local.ps1
```

**Frontend:**
```powershell
cd client
.\start-local.ps1
```

### Option 3: Manual Start

**Backend:**
```powershell
cd server
.\venv\Scripts\activate
python manage.py runserver
```

**Frontend:**
```powershell
cd client
npm run dev
```

---

## 🔍 Verification Steps

After starting the application:

1. **Backend Health Check**
   - Visit: http://localhost:8000/health/
   - Should return: `{"status": "healthy", "service": "toplorgical-api"}`

2. **API Documentation**
   - Visit: http://localhost:8000/api/docs/
   - Should show Swagger UI with all endpoints

3. **Admin Panel**
   - Visit: http://localhost:8000/admin/
   - Login with superuser credentials

4. **Frontend Application**
   - Visit: http://localhost:8080
   - Should show the landing page

5. **Test Authentication**
   - Register a new account via frontend
   - Login with the account
   - Create a test project/estimate

---

## ❌ Common Issues

### Issue: "Port 8000 already in use"
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

### Issue: "Database connection failed"
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists: `psql -U postgres -l`

### Issue: "Redis connection failed"
- Start Redis server
- Redis is optional - app will work without it but caching won't function

### Issue: "Module not found" errors (Backend)
```powershell
cd server
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Module not found" errors (Frontend)
```powershell
cd client
Remove-Item -Recurse -Force node_modules
npm install
```

### Issue: "Permission denied" when running .ps1 scripts
```powershell
# Run this once to allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📝 Post-Setup Tasks

After successful startup:

- [ ] Create your first project
- [ ] Add materials to the catalog
- [ ] Add machinery/equipment
- [ ] Create a cost estimate
- [ ] Export estimate to PDF/Excel
- [ ] Explore the API documentation
- [ ] Import Postman collection from `server/postman_collection.json`

---

## 🎯 Next Steps

1. **For Development:**
   - Review code structure in SETUP.md
   - Set up your IDE (VS Code recommended)
   - Install recommended extensions
   - Review API endpoints in Postman

2. **For Testing:**
   - Import Postman collection
   - Test all API endpoints
   - Create sample data
   - Test export functionality

3. **For Production:**
   - See SETUP.md for production deployment guide
   - Change SECRET_KEY
   - Set DEBUG=False
   - Configure proper database credentials
   - Set up SSL/HTTPS
   - Configure Stripe for payments

---

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review `SETUP.md` for detailed information
3. Check Django logs: `server/logs/django.log`
4. Check browser console for frontend errors
5. Ensure all prerequisites are installed correctly

---

**Ready to start?** Run `.\start.ps1` from the project root! 🚀
