# 🚀 Panduan Deployment Production - IndoWater Solution

## 📋 Status Deployment Saat Ini

✅ **Backend**: Deployed di Render (https://indowater.onrender.com)  
✅ **Frontend**: Deployed di Domain Custom (https://indowatersolution.co-id.id)  
✅ **Database**: MongoDB Atlas (Cluster0)  
❌ **Problem**: Login gagal karena database masih kosong

---

## 🔧 Langkah-langkah Perbaikan

### 1️⃣ **Seed Demo Users ke Production Database**

Backend sekarang memiliki API endpoint khusus untuk populate database dengan demo users.

#### **Option A: Via Browser (Paling Mudah)**

Buka URL berikut di browser:

```
https://indowater.onrender.com/api/seed/demo-users?key=indowater-seed-2025-secure
```

#### **Option B: Via curl (Terminal/Command Line)**

```bash
curl -X POST https://indowater.onrender.com/api/seed/demo-users \
     -H "x-seed-key: indowater-seed-2025-secure"
```

#### **Response yang Diharapkan:**

```json
{
  "success": true,
  "message": "Demo users seeded successfully",
  "summary": {
    "existing_users_before": 0,
    "created": 3,
    "already_existed": 0,
    "total_users_now": 3
  },
  "credentials": {
    "admin": {
      "email": "admin@indowater.com",
      "password": "admin123"
    },
    "technician": {
      "email": "technician@indowater.com",
      "password": "tech123"
    },
    "customer": {
      "email": "customer@indowater.com",
      "password": "customer123"
    }
  }
}
```

---

### 2️⃣ **Verifikasi Demo Users di MongoDB Atlas**

1. Login ke MongoDB Atlas: https://cloud.mongodb.com
2. Klik **Browse Collections** pada Cluster0
3. Pilih database **indowater**
4. Buka collection **users**
5. Seharusnya muncul 3 users: admin, technician, customer

---

### 3️⃣ **Test Login di Frontend**

Setelah seeding berhasil, coba login di https://indowatersolution.co-id.id dengan credentials:

**Admin Account:**
- Email: `admin@indowater.com`
- Password: `admin123`

**Technician Account:**
- Email: `technician@indowater.com`
- Password: `tech123`

**Customer Account:**
- Email: `customer@indowater.com`
- Password: `customer123`

---

### 4️⃣ **Seed Sample Water Usage Data (Optional)**

Untuk testing analytics dan dashboard, seed sample water usage data:

```bash
curl -X POST https://indowater.onrender.com/api/seed/water-usage \
     -H "x-seed-key: indowater-seed-2025-secure"
```

Atau via browser:
```
https://indowater.onrender.com/api/seed/water-usage?key=indowater-seed-2025-secure
```

---

### 5️⃣ **⚠️ SECURITY: Disable Seed Endpoint Setelah Seeding**

Setelah demo users berhasil dibuat, **PENTING untuk disable seed endpoint** agar tidak disalahgunakan:

#### **Di Render Dashboard:**

1. Go to: https://dashboard.render.com
2. Pilih service **indowater**
3. Go to **Environment** tab
4. Tambah environment variable baru:
   - Key: `DISABLE_SEED_ROUTES`
   - Value: `true`
5. Klik **Save Changes** (backend akan auto-restart)

#### **Atau Edit Code (Lebih Permanen):**

Di file `/app/backend/server.py`, comment atau hapus baris ini:

```python
# api_router.include_router(seed_router)  # ✅ DISABLED after seeding
```

Push ke GitHub, Render akan auto-deploy.

---

## 🔍 Troubleshooting

### ❌ **Error: "404 Not Found" di Render logs**

**Penyebab:** Backend tidak punya route `/` (root endpoint)

**Solusi:** Ini normal! Backend FastAPI hanya punya routes dengan prefix `/api`. 
Akses docs di: https://indowater.onrender.com/docs

---

### ❌ **Login masih gagal setelah seeding**

**Checklist:**

1. ✅ Pastikan seeding berhasil (dapat response `"success": true`)
2. ✅ Cek MongoDB Atlas - users collection harus ada 3 users
3. ✅ Cek environment variables di Render:
   - `MONGO_URL` harus berisi connection string yang benar (dengan password yang benar, bukan `<db_password>`)
   - `CORS_ORIGINS` harus ada: `https://indowatersolution.co-id.id`
4. ✅ Cek frontend `.env` - harus ada: `REACT_APP_BACKEND_URL=https://indowater.onrender.com`

---

### ❌ **Error: "Invalid seed key"**

**Penyebab:** Security key tidak cocok

**Solusi:** Pastikan menggunakan key yang benar: `indowater-seed-2025-secure`

Atau set custom key di Render environment variables:
- Key: `SEED_SECRET_KEY`
- Value: `your-custom-secret-key`

---

### ❌ **Error: MongoDB connection failed**

**Penyebab:** Connection string salah atau password tidak ter-encode

**Solusi:**

1. Pastikan password di `MONGO_URL` sudah benar (bukan `<db_password>`)
2. Jika password ada karakter khusus (@, !, $, etc), backend akan auto-encode
3. Format yang benar:
   ```
   mongodb+srv://indowater:PASSWORD_ANDA@cluster0.9v4ford.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   ```

---

## 📊 Monitoring & Logs

### **Cek Backend Logs di Render:**

1. Go to: https://dashboard.render.com
2. Pilih service **indowater**
3. Klik tab **Logs**
4. Cari message: `"Application startup complete"` - jika ada, backend running

### **Cek Frontend Network di Browser:**

1. Buka https://indowatersolution.co-id.id
2. Buka Developer Tools (F12)
3. Tab **Network**
4. Coba login, lihat request ke `/api/auth/login`
5. Jika status 401/400 - credentials salah atau database kosong
6. Jika status 500 - backend error
7. Jika status 0 (failed) - CORS issue atau backend down

---

## 🎯 Summary Checklist

- [ ] Seed demo users via API endpoint
- [ ] Verifikasi users ada di MongoDB Atlas
- [ ] Test login dengan 3 demo accounts
- [ ] (Optional) Seed water usage data untuk testing
- [ ] Disable seed endpoint setelah selesai
- [ ] Monitoring backend logs dan frontend console

---

## 📞 Support

Jika masih ada masalah setelah mengikuti panduan ini, check:

1. **Render Logs**: https://dashboard.render.com → indowater → Logs
2. **MongoDB Atlas**: https://cloud.mongodb.com → Browse Collections
3. **Frontend Console**: F12 → Console tab di browser

---

**Created:** 2025  
**Last Updated:** 2025-01-XX  
**Version:** 1.0
