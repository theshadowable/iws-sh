# 🔐 Environment Variables Reference

## Complete Guide for IndoWater Deployment

---

## 📋 Backend Environment Variables (Render)

### Required Variables

#### 1. PYTHON_VERSION
- **Value:** `3.11.0`
- **Required:** Yes
- **Description:** Python runtime version. **MUST include .0**
- **Example:** `3.11.0`
- **Note:** ⚠️ Using `3.11` without `.0` causes deployment errors

#### 2. MONGO_URL
- **Value:** MongoDB connection string
- **Required:** Yes
- **Description:** Full MongoDB Atlas connection string with credentials
- **Example:** 
  ```
  mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/indowater?retryWrites=true&w=majority
  ```
- **Important:** 
  - Passwords with special characters (@, !, $, etc) are automatically URL-encoded by the code
  - Include database name in URL or use DB_NAME variable
  - Use MongoDB Atlas FREE M0 tier for testing

#### 3. DB_NAME
- **Value:** `indowater`
- **Required:** Yes
- **Description:** MongoDB database name
- **Example:** `indowater`
- **Note:** Can be different if you prefer another name

#### 4. SECRET_KEY
- **Value:** Random 32+ character string
- **Required:** Yes
- **Description:** JWT secret key for token signing
- **Example:** `kJ8mP9nQ2wR5tY7xA3bC6dE9fG1hI4jK8mN`
- **Generate with:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **Security:** Never share or commit this key!

### Optional Variables

#### 5. CORS_ORIGINS
- **Value:** `*` or specific domain(s)
- **Required:** No
- **Default:** `*`
- **Description:** Allowed CORS origins (comma-separated for multiple)
- **Examples:**
  - Development: `*`
  - Production: `https://yourdomain.com`
  - Multiple: `https://app.yourdomain.com,https://admin.yourdomain.com`
- **Security:** Use specific domains in production

#### 6. UPLOAD_DIR
- **Value:** `/tmp/uploads`
- **Required:** No
- **Default:** `/tmp/uploads`
- **Description:** Directory for file uploads (Render-compatible)
- **Example:** `/tmp/uploads`
- **Note:** Already set in render.yaml. Do not change unless necessary.
- **Important:** Files in /tmp are temporary and lost on restart

#### 7. MIDTRANS_SERVER_KEY
- **Value:** Your Midtrans server key
- **Required:** No (optional payment gateway)
- **Description:** Midtrans payment gateway server key
- **Example:** `SB-Mid-server-xxxxxxxxxxxxx` (sandbox)
- **Get from:** https://dashboard.midtrans.com/
- **Note:** Payment features disabled if not set

#### 8. MIDTRANS_CLIENT_KEY
- **Value:** Your Midtrans client key
- **Required:** No (optional payment gateway)
- **Description:** Midtrans payment gateway client key
- **Example:** `SB-Mid-client-xxxxxxxxxxxxx` (sandbox)
- **Get from:** https://dashboard.midtrans.com/
- **Note:** Used for frontend payment integration

#### 9. XENDIT_API_KEY
- **Value:** Your Xendit API key
- **Required:** No (optional payment gateway)
- **Description:** Xendit payment gateway API key
- **Example:** `xnd_development_xxxxxxxxxxxxx`
- **Get from:** https://dashboard.xendit.co/
- **Note:** Alternative payment gateway

---

## 🎨 Frontend Environment Variables

### 1. REACT_APP_BACKEND_URL
- **Value:** Your backend URL
- **Required:** Yes
- **Description:** Full URL to backend API (must NOT end with /)
- **Examples:**
  - Local: `http://localhost:8001`
  - Render: `https://indowater-backend.onrender.com`
  - Custom: `https://api.yourdomain.com`
- **Important:** Do NOT include `/api` in the URL
- **Location:** `frontend/.env`

### 2. WDS_SOCKET_PORT
- **Value:** `443`
- **Required:** No (development only)
- **Default:** `443`
- **Description:** WebSocket port for hot reload (HTTPS)
- **Example:** `443`
- **Note:** Only needed for development with HTTPS

---

## 🚀 Setting Environment Variables

### On Render

1. Go to your service in Render Dashboard
2. Click **Environment** tab
3. Click **Add Environment Variable**
4. Enter Key and Value
5. Click **Save Changes**
6. Service will automatically redeploy

**Bulk Add:**
```bash
# Can be copy-pasted in Render UI
PYTHON_VERSION=3.11.0
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/indowater
DB_NAME=indowater
SECRET_KEY=your-random-secret-key-here
CORS_ORIGINS=*
UPLOAD_DIR=/tmp/uploads
```

### Locally (Development)

Create `backend/.env` file:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=indowater
CORS_ORIGINS=*
SECRET_KEY=dev-secret-key-change-in-production
```

Create `frontend/.env` file:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🔒 Security Best Practices

### 1. Never Commit .env Files
Add to `.gitignore`:
```
.env
.env.local
.env.production
*.env
```

### 2. Use Strong SECRET_KEY
- Minimum 32 characters
- Use random alphanumeric characters
- Generate new key for each environment
- Never reuse keys across projects

### 3. Restrict CORS_ORIGINS in Production
```env
# ❌ DON'T in production
CORS_ORIGINS=*

# ✅ DO in production
CORS_ORIGINS=https://yourdomain.com
```

### 4. Use Environment-Specific Keys

**Development:**
```env
MIDTRANS_SERVER_KEY=SB-Mid-server-xxxxx (sandbox)
XENDIT_API_KEY=xnd_development_xxxxx
```

**Production:**
```env
MIDTRANS_SERVER_KEY=Mid-server-xxxxx (production)
XENDIT_API_KEY=xnd_production_xxxxx
```

### 5. Rotate Secrets Regularly
- Change SECRET_KEY every 90 days
- Update after team member departure
- Rotate after security incident

---

## 📝 Environment Variable Templates

### Minimal Setup (Free Tier)
```env
# Required only
PYTHON_VERSION=3.11.0
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/indowater
DB_NAME=indowater
SECRET_KEY=generate-random-32-char-string
CORS_ORIGINS=*
```

### Full Production Setup
```env
# Core
PYTHON_VERSION=3.11.0
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/indowater
DB_NAME=indowater
SECRET_KEY=production-secret-key-32-chars-min
CORS_ORIGINS=https://app.yourdomain.com

# File Uploads
UPLOAD_DIR=/tmp/uploads

# Payment Gateways
MIDTRANS_SERVER_KEY=Mid-server-production-key
MIDTRANS_CLIENT_KEY=Mid-client-production-key
XENDIT_API_KEY=xnd_production_key
```

---

## 🧪 Testing Environment Variables

### Check if variables are loaded:

**Backend:**
```bash
# In Render Shell or locally
python -c "import os; print('MONGO_URL:', os.environ.get('MONGO_URL')[:20] + '...')"
python -c "import os; print('DB_NAME:', os.environ.get('DB_NAME'))"
python -c "import os; print('SECRET_KEY set:', bool(os.environ.get('SECRET_KEY')))"
```

**Frontend:**
```javascript
// In browser console
console.log('Backend URL:', process.env.REACT_APP_BACKEND_URL);
```

### Verify MongoDB Connection:
```bash
# Run in Render Shell
python seed_demo_users.py
# If successful, MongoDB connection works!
```

---

## ❓ Troubleshooting

### Problem: "InvalidURI: Username and password must be escaped"

**Solution:** Password contains special characters
```bash
# Encode password manually
python -c "from urllib.parse import quote_plus; print(quote_plus('MyP@ssw0rd!'))"
# Output: MyP%40ssw0rd%21

# Use in MONGO_URL:
mongodb+srv://user:MyP%40ssw0rd%21@cluster.mongodb.net/db
```

**Note:** The code auto-encodes, but if it fails, use pre-encoded password.

### Problem: "Application startup failed"

**Check:**
1. MONGO_URL is correct and accessible
2. SECRET_KEY is set and not empty
3. PYTHON_VERSION is exactly `3.11.0` (with .0)
4. No typos in variable names

### Problem: Frontend can't connect to backend

**Check:**
1. REACT_APP_BACKEND_URL is correct
2. Backend URL is accessible (test with curl)
3. CORS_ORIGINS includes frontend domain
4. Backend is actually running (check Render logs)

### Problem: Environment variable not updating

**Solution:**
1. Delete old variable
2. Add new variable
3. **Manual Deploy → Clear build cache & deploy**
4. Check logs to verify new value

---

## 📚 Additional Resources

- **Generate SECRET_KEY:** https://randomkeygen.com/
- **MongoDB Atlas:** https://cloud.mongodb.com/
- **Render Docs:** https://render.com/docs/environment-variables
- **Midtrans Dashboard:** https://dashboard.midtrans.com/
- **Xendit Dashboard:** https://dashboard.xendit.co/

---

## ✅ Quick Checklist

Before deploying, ensure:

- [ ] `PYTHON_VERSION=3.11.0` (with .0)
- [ ] `MONGO_URL` is valid and tested
- [ ] `DB_NAME` is set correctly
- [ ] `SECRET_KEY` is random and 32+ characters
- [ ] `CORS_ORIGINS` configured appropriately
- [ ] `REACT_APP_BACKEND_URL` points to correct backend
- [ ] Payment gateway keys added (if using payments)
- [ ] All variables saved in Render Dashboard
- [ ] Service redeployed after changes

---

**Last Updated:** January 2025  
**For:** IndoWater Management System  
**Platform:** Render + MongoDB Atlas
