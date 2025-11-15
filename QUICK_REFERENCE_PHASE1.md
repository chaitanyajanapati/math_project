# Quick Reference - Phase 1 Improvements

## 🚀 Quick Start

### Start the Application
```bash
# Backend
cd mathai_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd mathai_frontend
npm run dev
```

### Run Tests
```bash
cd mathai_backend
python -m pytest tests/ -v
python verify_improvements.py
```

---

## 🔐 Authentication API

### Register New User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "grade": 8
}
```

### Login
```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com
password=password123
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "grade": 8
  }
}
```

### Get Current User
```bash
GET /api/auth/me
Authorization: Bearer <token>
```

### Protected Endpoints
Add header to any request:
```
Authorization: Bearer <your_token>
```

---

## 🗄️ Database

### Location
```
mathai_backend/data/mathai.db
```

### View Tables
```bash
cd mathai_backend/data
sqlite3 mathai.db ".tables"
```

### Query Users
```bash
sqlite3 mathai.db "SELECT * FROM users;"
```

### Initialize Database
```bash
cd mathai_backend
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
"
```

---

## ⚙️ Environment Configuration

### Backend (.env)
```bash
APP_SECRET_KEY=your-secret-key-here
APP_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
APP_LOG_LEVEL=INFO
APP_ENABLE_METRICS=true
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_ENV=development
```

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🧪 Testing Commands

### All Tests
```bash
pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/test_auth.py -v
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Verification Script
```bash
python verify_improvements.py
```

---

## 🎨 Frontend Usage

### Use Auth Context
```typescript
import { useAuth } from '../hooks/useAuth';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginForm onLogin={login} />;
  }
  
  return <div>Welcome, {user.username}!</div>;
}
```

### Error Boundary
Already wrapping the app - catches all component errors automatically.

---

## 📊 Monitoring

### View Logs
```bash
# Backend logs (structured JSON)
cd mathai_backend
tail -f backend.log

# Check for errors
grep "ERROR" backend.log
```

### Prometheus Metrics
```
http://localhost:8000/metrics
```

### Health Check
```
http://localhost:8000/health
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Database Issues
```bash
# Reset database
cd mathai_backend
rm data/mathai.db
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
```

### Authentication Issues
```bash
# Check if user exists
cd mathai_backend/data
sqlite3 mathai.db "SELECT email, username FROM users;"

# Delete test users
sqlite3 mathai.db "DELETE FROM users WHERE email LIKE '%test%';"
```

### Module Import Errors
```bash
# Reinstall dependencies
cd mathai_backend
pip install -r requirements.txt

cd mathai_frontend
npm install
```

---

## 📦 Dependencies

### Install Backend Dependencies
```bash
cd mathai_backend
pip install -r requirements.txt
```

### Install Frontend Dependencies
```bash
cd mathai_frontend
npm install
```

### Update Dependencies
```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```

---

## 🔒 Security Best Practices

### Production Deployment
1. **Change SECRET_KEY** - Generate new random key
2. **Use HTTPS** - Enable SSL/TLS
3. **Update CORS origins** - Restrict to production domains
4. **Enable rate limiting** - Already configured
5. **Use strong passwords** - Enforce minimum 8 characters
6. **Regular backups** - Backup SQLite database

### Environment Variables in Production
```bash
# Never commit .env files
# Use secrets management (AWS Secrets Manager, etc.)
# Rotate secrets regularly
```

---

## 📚 Documentation

- **Phase 1 Verification Report:** `PHASE1_VERIFICATION_REPORT.md`
- **Phase 1 Complete Summary:** `PHASE1_COMPLETE_SUMMARY.md`
- **This Quick Reference:** `QUICK_REFERENCE_PHASE1.md`

---

## 🐛 Common Issues

### "Module not found" errors
```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/mathai_backend"
```

### "Database locked" errors
```bash
# Close all connections and restart
rm data/mathai.db-journal  # If exists
```

### JWT token expired
```bash
# Token expires after 30 minutes
# Client should refresh or re-login
```

---

## 🎯 Quick Test Sequence

```bash
# 1. Start backend
cd mathai_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# 2. Wait for startup
sleep 5

# 3. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"quicktest@example.com","username":"quicktest","password":"test123","grade":8}'

# 4. Login
curl -X POST http://localhost:8000/api/auth/login \
  -F "username=quicktest@example.com" \
  -F "password=test123"

# 5. Run tests
python -m pytest tests/test_auth.py -v

# 6. Cleanup
fg  # Bring backend to foreground
# Ctrl+C to stop
```

---

## 🔗 Useful Links

- **Backend API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173
- **Prometheus Metrics:** http://localhost:8000/metrics
- **Health Check:** http://localhost:8000/health

---

**Last Updated:** November 15, 2025  
**Version:** Phase 1 Complete
