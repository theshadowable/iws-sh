# 🎯 Checklist Deployment IndoWater

## Pre-Deployment
- [ ] Semua fitur sudah di-test local
- [ ] Database schema sudah final
- [ ] API endpoints sudah tested
- [ ] Frontend build berhasil tanpa error

---

## 1. MongoDB Atlas Setup
- [ ] Akun MongoDB Atlas created
- [ ] Cluster FREE tier created (Region: Singapore)
- [ ] Database user created dengan password kuat
- [ ] Network Access: Allow dari anywhere (0.0.0.0/0)
- [ ] Connection string didapat dan disimpan
- [ ] Test koneksi dari local berhasil

**Connection String Format:**
```
mongodb+srv://[username]:[password]@[cluster].mongodb.net/indowater_db?retryWrites=true&w=majority
```

---

## 2. GitHub Repository
- [ ] Git initialized di project
- [ ] .gitignore sudah setup (exclude .env, node_modules, etc)
- [ ] Repository created di GitHub
- [ ] Backend code pushed ke GitHub
- [ ] Frontend code pushed ke GitHub (optional)

**Commands:**
```bash
git init
git add .
git commit -m "Initial commit for deployment"
git remote add origin https://github.com/USERNAME/indowater-backend.git
git push -u origin main
```

---

## 3. Backend - Render Deployment

### A. Persiapan File
- [ ] `requirements.txt` lengkap dengan semua dependencies
- [ ] `render.yaml` created di folder backend
- [ ] `server.py` ready untuk production
- [ ] Semua import dependencies terinstall

### B. Render Setup
- [ ] Akun Render created (signup dengan GitHub)
- [ ] New Web Service created
- [ ] Repository connected
- [ ] Root Directory set to: `backend`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- [ ] Instance: FREE tier selected

### C. Environment Variables
- [ ] `MONGO_URL` = [MongoDB connection string]
- [ ] `DB_NAME` = `indowater_db`
- [ ] `SECRET_KEY` = [generate random 32+ chars]
- [ ] `CORS_ORIGINS` = [frontend domain/URL]
- [ ] `PYTHON_VERSION` = `3.11`

### D. Deployment
- [ ] Deploy button clicked
- [ ] Build logs checked (no errors)
- [ ] Deploy successful
- [ ] Backend URL accessible: `https://[app-name].onrender.com`

### E. Post-Deployment
- [ ] Test health endpoint: `/api/health`
- [ ] Seed database via Shell:
  - [ ] `python seed_demo_users.py`
  - [ ] `python seed_phase2_data.py`
  - [ ] `python seed_water_usage.py`
- [ ] Test login API dengan demo accounts
- [ ] Check Render logs untuk error

**Backend URL:** `https://______________________.onrender.com`

---

## 4. Frontend - Build & Upload

### A. Environment Setup
- [ ] `.env` file updated dengan production backend URL
- [ ] `REACT_APP_BACKEND_URL` set to Render URL
- [ ] Payment gateway keys configured (jika ada)

**File: `frontend/.env`**
```env
REACT_APP_BACKEND_URL=https://[your-render-app].onrender.com
```

### B. Build Production
- [ ] `yarn install` executed successfully
- [ ] `yarn build` completed without errors
- [ ] `build/` folder generated
- [ ] All static files present di `build/static/`

**Commands:**
```bash
cd frontend
yarn install
yarn build
# Hasil: folder build/ ready untuk upload
```

### C. Server Upload
- [ ] FTP/SFTP credentials ready
- [ ] Connect to server
- [ ] Navigate to web root (`public_html/` or `/var/www/html/`)
- [ ] Upload all files dari `build/` folder
- [ ] Verify all files uploaded

### D. Web Server Configuration

**Untuk Nginx:**
- [ ] Config file edited: `/etc/nginx/sites-available/default`
- [ ] Root directory set correctly
- [ ] SPA routing configured (`try_files`)
- [ ] API proxy setup (optional)
- [ ] Nginx restarted: `sudo systemctl restart nginx`

**Untuk Apache:**
- [ ] `.htaccess` file created di root folder
- [ ] mod_rewrite enabled
- [ ] SPA routing rules added
- [ ] Apache restarted

### E. Domain & SSL
- [ ] Domain DNS configured (A record)
- [ ] Domain accessible via browser
- [ ] SSL certificate installed (Let's Encrypt/Certbot)
- [ ] HTTPS working
- [ ] HTTP to HTTPS redirect configured

**Frontend URL:** `https://______________________`

---

## 5. Testing Production

### Backend Testing
- [ ] Health check: `GET /api/health`
- [ ] Login admin: `POST /api/auth/login`
- [ ] Get dashboard stats: `GET /api/dashboard/stats`
- [ ] List vouchers: `GET /api/vouchers`
- [ ] List customers: `GET /api/customers`
- [ ] Analytics data: `GET /api/analytics/usage`

### Frontend Testing
- [ ] Homepage loads correctly
- [ ] Login page accessible
- [ ] Login dengan admin account works
- [ ] Login dengan technician account works
- [ ] Login dengan customer account works
- [ ] Dashboard loads dan shows data
- [ ] Navigation menu works
- [ ] Analytics page displays charts
- [ ] Payment pages accessible
- [ ] Voucher management loads
- [ ] Customer management loads
- [ ] Real-time monitoring animation works
- [ ] Mobile responsive tested

### Cross-Browser Testing
- [ ] Chrome/Edge tested
- [ ] Firefox tested
- [ ] Safari tested (Mac/iOS)
- [ ] Mobile browsers tested

---

## 6. Monitoring & Maintenance

### Uptime Monitoring
- [ ] UptimeRobot account created
- [ ] Backend monitor added
- [ ] Frontend monitor added
- [ ] Alert email configured
- [ ] Monitoring interval: 5 minutes

### Error Tracking (Optional)
- [ ] Sentry account created
- [ ] Sentry SDK integrated
- [ ] Error alerts configured

### Backup
- [ ] MongoDB Atlas auto backup enabled
- [ ] Manual backup tested
- [ ] Backup schedule documented

---

## 7. Documentation

- [ ] `DEPLOYMENT_RENDER_GUIDE.md` reviewed
- [ ] Environment variables documented
- [ ] Demo accounts credentials documented
- [ ] API documentation updated
- [ ] User guide created (optional)

---

## 8. Security Checklist

- [ ] SECRET_KEY is strong and random
- [ ] Database password is strong
- [ ] CORS configured correctly (not wildcard in production)
- [ ] API rate limiting considered
- [ ] Environment variables tidak hardcoded
- [ ] Sensitive data tidak di-commit ke Git
- [ ] SSL/HTTPS enabled
- [ ] Security headers configured

---

## 9. Performance Optimization

- [ ] Frontend static assets cached
- [ ] Images optimized
- [ ] Lazy loading implemented
- [ ] API response times checked
- [ ] Database indexes verified
- [ ] CDN considered (optional)

---

## 10. Launch Checklist

### Pre-Launch
- [ ] All tests passed
- [ ] No console errors
- [ ] No broken links
- [ ] Mobile responsive verified
- [ ] Loading states working
- [ ] Error handling working

### Launch Day
- [ ] Final backup taken
- [ ] Monitoring enabled
- [ ] Support email ready
- [ ] User documentation ready
- [ ] Demo credentials shared

### Post-Launch
- [ ] Monitor errors for 24 hours
- [ ] Check server resources
- [ ] Review user feedback
- [ ] Plan next iteration

---

## 📊 Deployment Info

**Deployment Date:** __________________

**URLs:**
- Backend API: https://______________________.onrender.com
- Frontend Web: https://______________________
- MongoDB: mongodb+srv://...

**Demo Accounts:**
```
Admin:
  Email: admin@indowater.com
  Password: admin123

Technician:
  Email: technician@indowater.com
  Password: tech123

Customer:
  Email: customer@indowater.com
  Password: customer123
```

**Team:**
- Developer: __________________
- Tester: __________________
- Client: __________________

---

## 🚨 Emergency Contacts

**Render Support:** https://render.com/docs
**MongoDB Support:** https://www.mongodb.com/docs/atlas/
**Your Email:** __________________

---

## ✅ Final Sign-Off

- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] Database configured and seeded
- [ ] All features tested and working
- [ ] Monitoring active
- [ ] Documentation complete
- [ ] Client/Stakeholder approved

**Signed by:** __________________ 
**Date:** __________________

---

**Status: Ready for Production! 🚀**
