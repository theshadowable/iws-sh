# 🚀 Panduan Deploy IndoWater ke Render

## 📋 Daftar Isi
1. [Setup MongoDB Atlas (Database)](#1-setup-mongodb-atlas)
2. [Deploy Backend ke Render](#2-deploy-backend-ke-render)
3. [Build Frontend untuk Server Sendiri](#3-build-frontend-untuk-server-sendiri)
4. [Testing & Troubleshooting](#4-testing--troubleshooting)

---

## 1. Setup MongoDB Atlas (Database) 🗄️

### Step 1.1: Buat Akun MongoDB Atlas
1. Buka https://www.mongodb.com/cloud/atlas/register
2. Sign up dengan email atau Google account
3. Pilih **FREE** tier (M0 Sandbox - 512MB storage)
4. Pilih region terdekat: **Singapore** atau **Mumbai**

### Step 1.2: Buat Database Cluster
1. Setelah login, klik **"Build a Database"**
2. Pilih **FREE** tier (M0)
3. Pilih **Cloud Provider**: AWS
4. Pilih **Region**: Singapore (ap-southeast-1) atau Mumbai
5. Cluster Name: biarkan default atau ganti dengan `indowater-cluster`
6. Klik **"Create Cluster"** (tunggu 3-5 menit)

### Step 1.3: Setup Database Access
1. Di sidebar, klik **"Database Access"**
2. Klik **"Add New Database User"**
3. Pilih **Password Authentication**
4. Username: `indowater_admin`
5. Password: Generate atau buat password kuat (SIMPAN PASSWORD INI!)
6. Database User Privileges: **Read and write to any database**
7. Klik **"Add User"**

### Step 1.4: Setup Network Access
1. Di sidebar, klik **"Network Access"**
2. Klik **"Add IP Address"**
3. Pilih **"Allow Access from Anywhere"** (0.0.0.0/0)
   > ⚠️ Untuk production, sebaiknya batasi IP specific
4. Klik **"Confirm"**

### Step 1.5: Dapatkan Connection String
1. Kembali ke **"Database"** di sidebar
2. Klik tombol **"Connect"** pada cluster Anda
3. Pilih **"Connect your application"**
4. Driver: **Python**, Version: **3.6 or later**
5. Copy connection string:
   ```
   mongodb+srv://indowater_admin:<password>@indowater-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Ganti `<password>` dengan password yang Anda buat tadi
7. **SIMPAN CONNECTION STRING INI** - akan digunakan di Render!

**Contoh Connection String Lengkap:**
```
mongodb+srv://indowater_admin:YourPassword123@indowater-cluster.abc12.mongodb.net/indowater_db?retryWrites=true&w=majority
```

---

## 2. Deploy Backend ke Render 🎯

### Step 2.1: Persiapan File Backend

Pastikan file-file ini ada di folder `backend/`:

**✅ File yang Sudah Ada:**
- ✅ `requirements.txt` - daftar Python dependencies
- ✅ `server.py` - main FastAPI application
- ✅ Semua file routes, models, dan services

**📝 File Baru yang Perlu Dibuat:**

#### 2.1.1: Buat `backend/render.yaml`
```yaml
services:
  - type: web
    name: indowater-backend
    env: python
    region: singapore
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn server:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: SECRET_KEY
        generateValue: true
      - key: MONGO_URL
        sync: false
      - key: DB_NAME
        value: indowater_db
      - key: CORS_ORIGINS
        value: "*"
```

#### 2.1.2: Update `backend/requirements.txt`
Pastikan semua dependencies tercantum:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pymongo==4.6.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
bcrypt==4.1.1
pydantic==2.5.0
pydantic-settings==2.1.0
PyJWT==2.8.0
email-validator==2.1.0
reportlab==4.0.7
openpyxl==3.1.2
et_xmlfile==1.1.0
Pillow==10.1.0
pytesseract==0.3.10
gunicorn==21.2.0
```

### Step 2.2: Push ke GitHub

1. **Inisialisasi Git** (jika belum):
   ```bash
   cd /app
   git init
   git add .
   git commit -m "Initial commit - IndoWater backend"
   ```

2. **Buat Repository di GitHub**:
   - Buka https://github.com/new
   - Repository name: `indowater-backend`
   - Visibility: Public atau Private
   - Klik **"Create repository"**

3. **Push ke GitHub**:
   ```bash
   git remote add origin https://github.com/USERNAME/indowater-backend.git
   git branch -M main
   git push -u origin main
   ```

### Step 2.3: Deploy di Render

#### A. Buat Akun Render
1. Buka https://render.com
2. Sign up dengan GitHub account
3. Authorize Render untuk akses repository

#### B. Buat Web Service Baru
1. Dari dashboard Render, klik **"New +"** → **"Web Service"**
2. Connect repository: Pilih `indowater-backend`
3. Configure service:

**Basic Settings:**
- **Name**: `indowater-backend`
- **Region**: Singapore
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: Python 3

**Build & Deploy Settings:**
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  uvicorn server:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Pilih **Free** ($0/month)
- CPU: 0.5 CPU
- RAM: 512 MB

#### C. Setup Environment Variables
Klik **"Advanced"** → **"Add Environment Variable"**

Tambahkan variables berikut:

| Key | Value | Catatan |
|-----|-------|---------|
| `MONGO_URL` | `mongodb+srv://indowater_admin:password@...` | Dari MongoDB Atlas Step 1.5 |
| `DB_NAME` | `indowater_db` | Nama database |
| `SECRET_KEY` | `your-secret-key-min-32-characters-long` | Generate random string |
| `CORS_ORIGINS` | `https://yourdomain.com,https://www.yourdomain.com` | Ganti dengan domain frontend Anda |
| `PYTHON_VERSION` | `3.11` | Versi Python |

**Generate SECRET_KEY:**
```python
# Gunakan ini untuk generate SECRET_KEY
import secrets
print(secrets.token_urlsafe(32))
# Output: wXpH4n5x8v-LqK9mF3rT6yU2zC7dE0aB1g4hW9iN8jM
```

#### D. Deploy!
1. Klik **"Create Web Service"**
2. Render akan mulai build dan deploy (tunggu 5-10 menit)
3. Anda akan mendapat URL: `https://indowater-backend.onrender.com`

### Step 2.4: Seed Database
Setelah backend berhasil deploy:

1. Buka **Shell** di Render Dashboard
2. Jalankan seed scripts:
```bash
python seed_demo_users.py
python seed_phase2_data.py
python seed_water_usage.py
```

**Atau via API:**
Buat endpoint seed di `server.py` (untuk kemudahan):
```python
@api_router.post("/admin/seed-database")
async def seed_database(current_user: User = Depends(require_role(["admin"]))):
    """Seed database with demo data (admin only)"""
    # Run seed scripts
    import subprocess
    subprocess.run(["python", "seed_demo_users.py"])
    subprocess.run(["python", "seed_phase2_data.py"])
    subprocess.run(["python", "seed_water_usage.py"])
    return {"message": "Database seeded successfully"}
```

---

## 3. Build Frontend untuk Server Sendiri 📦

### Step 3.1: Update Environment Variables

Edit file `frontend/.env`:
```env
# PRODUCTION BACKEND URL - ganti dengan URL Render Anda
REACT_APP_BACKEND_URL=https://indowater-backend.onrender.com

# Jika ada payment gateway
REACT_APP_MIDTRANS_CLIENT_KEY=your-midtrans-client-key
```

### Step 3.2: Build Production

Jalankan command berikut di folder `frontend/`:

```bash
# Install dependencies
yarn install

# Build untuk production
yarn build
```

Proses build akan menghasilkan folder **`build/`** yang berisi:
- `index.html` - HTML file utama
- `static/` - folder berisi CSS, JS, dan assets

### Step 3.3: File yang Akan Di-Upload

Setelah build selesai, Anda akan upload folder `build/` ke server Anda:

```
frontend/build/
├── index.html
├── asset-manifest.json
├── favicon.ico
├── logo192.png
├── logo512.png
├── manifest.json
├── robots.txt
└── static/
    ├── css/
    │   └── main.xxxxxxxx.css
    ├── js/
    │   ├── main.xxxxxxxx.js
    │   └── runtime-main.xxxxxxxx.js
    └── media/
        └── [images and fonts]
```

### Step 3.4: Upload ke Server Anda

**Untuk cPanel/DirectAdmin:**
1. Login ke cPanel
2. Buka **File Manager**
3. Navigate ke `public_html/` atau `www/`
4. Upload semua isi folder `build/`
5. Extract jika dalam bentuk ZIP

**Untuk VPS (via FTP/SFTP):**
```bash
# Dari local machine
scp -r build/* user@your-server.com:/var/www/html/
```

**Untuk VPS (via SSH):**
```bash
# Login ke VPS
ssh user@your-server.com

# Clone repo dan build
git clone https://github.com/USERNAME/indowater-frontend.git
cd indowater-frontend/frontend
yarn install
yarn build

# Copy ke web directory
cp -r build/* /var/www/html/
```

### Step 3.5: Setup Nginx/Apache

**Untuk Nginx:**
Edit `/etc/nginx/sites-available/default`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass https://indowater-backend.onrender.com;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Cache static assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

**Untuk Apache:**
Create `.htaccess` di folder `build/`:
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-l
  RewriteRule . /index.html [L]
</IfModule>
```

---

## 4. Testing & Troubleshooting 🧪

### Step 4.1: Test Backend
```bash
# Test health endpoint
curl https://indowater-backend.onrender.com/api/health

# Test login
curl -X POST https://indowater-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@indowater.com","password":"admin123"}'
```

### Step 4.2: Test Frontend
1. Buka browser: `https://yourdomain.com`
2. Test login dengan demo accounts:
   - Admin: `admin@indowater.com` / `admin123`
   - Technician: `technician@indowater.com` / `tech123`
   - Customer: `customer@indowater.com` / `customer123`

### Common Issues & Solutions

**❌ Backend Error: "Application startup failed"**
- ✅ Check MongoDB connection string di Environment Variables
- ✅ Pastikan MongoDB Atlas Network Access allow 0.0.0.0/0
- ✅ Check logs di Render Dashboard → Logs tab

**❌ Frontend: "Network Error" atau "Failed to fetch"**
- ✅ Check `REACT_APP_BACKEND_URL` di `.env`
- ✅ Rebuild frontend: `yarn build`
- ✅ Check CORS settings di backend

**❌ Render Free Tier Sleep (after 15 minutes inactive)**
- ✅ Free tier sleep setelah 15 menit tidak ada request
- ✅ First request akan lambat (cold start ~30 detik)
- ✅ Setup ping service: https://uptimerobot.com (free)

**❌ MongoDB Connection Failed**
- ✅ Check username/password benar
- ✅ Check database name match dengan `DB_NAME`
- ✅ Check whitelist IP di MongoDB Atlas

---

## 5. Monitoring & Maintenance 📊

### Setup Uptime Monitoring (Optional)
1. Daftar di https://uptimerobot.com (FREE)
2. Add New Monitor:
   - Monitor Type: HTTP(s)
   - Friendly Name: IndoWater Backend
   - URL: `https://indowater-backend.onrender.com/api/health`
   - Monitoring Interval: 5 minutes

### Backup Database
MongoDB Atlas automatic backup included in FREE tier!

**Manual Backup:**
```bash
# Install mongodump
mongodump --uri="mongodb+srv://username:password@cluster.mongodb.net/indowater_db"

# Restore
mongorestore --uri="mongodb+srv://username:password@cluster.mongodb.net/indowater_db" dump/
```

### Update Application
```bash
# Update backend
git add .
git commit -m "Update backend"
git push origin main
# Render auto-deploy on push!

# Update frontend
yarn build
# Upload build/ folder ke server
```

---

## 6. Production Checklist ✅

**Backend (Render):**
- [ ] MongoDB Atlas cluster created
- [ ] Database user with password created
- [ ] Network access configured (0.0.0.0/0)
- [ ] Connection string obtained
- [ ] Repository pushed to GitHub
- [ ] Render web service created
- [ ] Environment variables configured
- [ ] Database seeded with demo data
- [ ] Backend URL accessible

**Frontend:**
- [ ] `.env` updated with production backend URL
- [ ] `yarn build` executed successfully
- [ ] Build files uploaded to server
- [ ] Domain/subdomain configured
- [ ] Nginx/Apache configured
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] Frontend accessible via browser
- [ ] API calls working (no CORS errors)

**Testing:**
- [ ] Login works for all 3 demo accounts
- [ ] Dashboard loads correctly
- [ ] Analytics page shows data
- [ ] Payment pages accessible
- [ ] Voucher management works
- [ ] Customer management works
- [ ] Mobile responsive tested

---

## 7. Biaya Estimasi 💰

**Gratis (FREE Tier):**
- MongoDB Atlas: FREE (512MB)
- Render Backend: FREE (512MB RAM, sleeps after 15min)
- Total: **Rp 0/bulan** ✅

**Upgrade Options (Jika Diperlukan):**
- MongoDB Atlas M2: $9/month (2GB)
- Render Starter: $7/month (512MB, no sleep)
- Total: **~Rp 250.000/bulan**

---

## 8. Next Steps 🎯

1. **Setup Custom Domain:**
   - Buy domain dari Niagahoster/Namecheap
   - Point A record ke server IP
   - Install SSL certificate (Let's Encrypt)

2. **Add Payment Gateway:**
   - Daftar Midtrans/Xendit
   - Dapat API keys
   - Add ke environment variables
   - Test payment flow

3. **Email Notifications:**
   - Setup SendGrid/Mailgun
   - Configure SMTP settings
   - Test alert emails

4. **Analytics:**
   - Google Analytics
   - Sentry for error tracking
   - LogRocket for session replay

---

## 📞 Support

Jika ada masalah saat deployment:
1. Check Render logs: Dashboard → Logs
2. Check MongoDB Atlas logs: Monitoring → Logs
3. Check browser console (F12) untuk frontend errors
4. Test API dengan Postman/cURL

**Selamat Deploy! 🚀**
