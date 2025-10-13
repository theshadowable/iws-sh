# IndoWater Deployment Guide

Complete guide to deploy the IndoWater full-stack application to production.

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [Railway + Vercel Deployment (Recommended)](#railway--vercel-deployment-recommended)
3. [Alternative Full-Stack Platforms](#alternative-full-stack-platforms)
4. [Environment Variables](#environment-variables)
5. [Post-Deployment Steps](#post-deployment-steps)

---

## Deployment Options

### Option 1: Railway (Backend) + Vercel (Frontend) ⭐ Recommended
- **Backend:** FastAPI on Railway
- **Frontend:** React on Vercel
- **Database:** MongoDB Atlas (free tier available)
- **Cost:** Railway free tier + Vercel free tier

### Option 2: Single Platform Deployment
- **Render:** Full-stack deployment
- **Heroku:** Full-stack deployment (paid)
- **DigitalOcean App Platform:** Full-stack deployment
- **AWS/GCP:** More complex but scalable

---

## Railway + Vercel Deployment (Recommended)

This is the most cost-effective and easiest deployment option.

### Prerequisites
- GitHub account
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- MongoDB Atlas account (https://www.mongodb.com/cloud/atlas)

---

### Step 1: Setup MongoDB Atlas (Cloud Database)

1. **Create MongoDB Atlas Account**
   - Go to https://www.mongodb.com/cloud/atlas/register
   - Sign up for free account

2. **Create a New Cluster**
   ```
   - Choose FREE tier (M0)
   - Select your preferred region (closest to your users)
   - Cluster name: indowater-cluster
   ```

3. **Create Database User**
   ```
   - Go to Database Access
   - Click "Add New Database User"
   - Username: indowater_admin
   - Password: [generate strong password]
   - User Privileges: Read and write to any database
   - Click "Add User"
   ```

4. **Configure Network Access**
   ```
   - Go to Network Access
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"
   ```

5. **Get Connection String**
   ```
   - Go to Database → Connect
   - Choose "Connect your application"
   - Driver: Python 3.11 or later
   - Copy the connection string:
     mongodb+srv://indowater_admin:<password>@indowater-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   
   - Replace <password> with your actual password
   - Save this as MONGO_URL
   ```

---

### Step 2: Deploy Backend to Railway

#### 2.1 Prepare Backend for Railway

1. **Create `railway.json` in /backend directory:**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Create `Procfile` in /backend directory:**

```
web: uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
```

3. **Ensure `requirements.txt` is complete:**

```bash
cd /app/backend
pip freeze > requirements.txt
```

4. **Create `.dockerignore` in /backend directory:**

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
.git
.gitignore
*.log
*.pot
*.mo
.pytest_cache
.coverage
htmlcov/
dist/
build/
*.egg-info/
```

#### 2.2 Deploy to Railway

1. **Push Code to GitHub**
   ```bash
   # If not already a git repository
   cd /app
   git init
   git add .
   git commit -m "Initial commit"
   
   # Create new GitHub repository and push
   git remote add origin https://github.com/your-username/indowater.git
   git branch -M main
   git push -u origin main
   ```

2. **Connect Railway to GitHub**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select your `indowater` repository
   - Select `/backend` as the root directory

3. **Configure Environment Variables in Railway**
   
   Click on your project → Variables tab → Add all these variables:

   ```env
   # Database
   MONGO_URL=mongodb+srv://indowater_admin:YOUR_PASSWORD@indowater-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=indowater_db

   # JWT Authentication
   SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # CORS (Update after you get Vercel URL)
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

   # Payment Gateways (Optional - use sandbox keys for testing)
   MIDTRANS_SERVER_KEY=your-midtrans-server-key
   MIDTRANS_CLIENT_KEY=your-midtrans-client-key
   MIDTRANS_IS_PRODUCTION=false

   XENDIT_API_KEY=your-xendit-api-key
   XENDIT_WEBHOOK_TOKEN=your-xendit-webhook-token

   # Python Environment
   PYTHON_VERSION=3.11

   # Port (Railway sets this automatically)
   PORT=8001
   ```

4. **Deploy Backend**
   - Railway will automatically detect Python and install dependencies
   - Wait for deployment to complete
   - You'll get a URL like: `https://indowater-backend.railway.app`
   - **Save this URL - you'll need it for frontend!**

5. **Test Backend**
   ```bash
   # Test health endpoint
   curl https://indowater-backend.railway.app/health
   
   # Should return: {"status": "healthy"}
   ```

---

### Step 3: Deploy Frontend to Vercel

#### 3.1 Prepare Frontend for Vercel

1. **Create `vercel.json` in /frontend directory:**

```json
{
  "buildCommand": "yarn build",
  "outputDirectory": "build",
  "devCommand": "yarn start",
  "installCommand": "yarn install",
  "framework": "create-react-app",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

2. **Update Frontend Environment Variables**

   Create/update `/frontend/.env.production`:

   ```env
   REACT_APP_BACKEND_URL=https://indowater-backend.railway.app
   ```

3. **Ensure `package.json` has correct build script:**

   ```json
   {
     "scripts": {
       "start": "react-scripts start",
       "build": "react-scripts build",
       "test": "react-scripts test",
       "eject": "react-scripts eject"
     }
   }
   ```

#### 3.2 Deploy to Vercel

**Option A: Vercel CLI (Recommended for first deployment)**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy from frontend directory:**
   ```bash
   cd /app/frontend
   vercel
   ```

4. **Follow the prompts:**
   ```
   ? Set up and deploy "~/app/frontend"? Yes
   ? Which scope? Your username
   ? Link to existing project? No
   ? What's your project's name? indowater
   ? In which directory is your code located? ./
   ? Want to override the settings? No
   ```

5. **Set Production Environment Variables:**
   ```bash
   vercel env add REACT_APP_BACKEND_URL production
   # When prompted, enter: https://indowater-backend.railway.app
   ```

6. **Deploy to Production:**
   ```bash
   vercel --prod
   ```

**Option B: Vercel Dashboard**

1. **Go to https://vercel.com**
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Framework Preset: Create React App
   - Root Directory: `frontend`

2. **Configure Build Settings:**
   ```
   Build Command: yarn build
   Output Directory: build
   Install Command: yarn install
   Development Command: yarn start
   ```

3. **Add Environment Variables:**
   ```
   Name: REACT_APP_BACKEND_URL
   Value: https://indowater-backend.railway.app
   Environment: Production
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete
   - You'll get URL like: `https://indowater.vercel.app`

---

### Step 4: Update CORS in Backend

After getting your Vercel URL, update Railway backend environment variables:

1. **Go to Railway Dashboard**
2. **Update `CORS_ORIGINS` variable:**
   ```
   CORS_ORIGINS=https://indowater.vercel.app,http://localhost:3000
   ```
3. **Railway will automatically redeploy**

---

### Step 5: Seed Database

After successful deployment, seed the database with initial data:

1. **SSH into Railway (or use Railway CLI):**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Link to your project
   railway link
   
   # Run seed command
   railway run python seed_demo_users.py
   ```

   Or manually run via Railway Dashboard → Deployments → Console

2. **Seed Scripts to Run:**
   ```bash
   # Required
   python seed_demo_users.py
   
   # Optional (for testing)
   python seed_water_usage.py
   ```

---

### Step 6: Test Deployment

1. **Test Frontend:**
   - Go to your Vercel URL: `https://indowater.vercel.app`
   - Try logging in with demo credentials:
     - Admin: `admin@indowater.com` / `admin123`
     - Technician: `technician@indowater.com` / `tech123`
     - Customer: `customer@indowater.com` / `customer123`

2. **Test Backend API:**
   ```bash
   # Test health
   curl https://indowater-backend.railway.app/health
   
   # Test login
   curl -X POST https://indowater-backend.railway.app/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@indowater.com", "password": "admin123"}'
   ```

---

## Alternative Full-Stack Platforms

### Option 2: Render (Full-Stack Deployment)

**Pros:**
- Deploy both frontend and backend on same platform
- Free tier available
- Easy setup

**Cons:**
- Free tier has cold starts
- Limited resources on free tier

**Steps:**

1. **Create Render Account:** https://render.com

2. **Create Web Service for Backend:**
   ```
   - New → Web Service
   - Connect GitHub repository
   - Name: indowater-backend
   - Environment: Python 3
   - Build Command: pip install -r backend/requirements.txt
   - Start Command: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
   - Add Environment Variables (same as Railway)
   ```

3. **Create Static Site for Frontend:**
   ```
   - New → Static Site
   - Connect GitHub repository
   - Name: indowater-frontend
   - Build Command: cd frontend && yarn install && yarn build
   - Publish Directory: frontend/build
   - Add Environment Variable: REACT_APP_BACKEND_URL
   ```

---

### Option 3: DigitalOcean App Platform

**Pros:**
- More control than PaaS
- Better performance
- $5/month basic tier

**Cons:**
- Not free
- Slightly more complex

**Steps:**

1. **Create DigitalOcean Account**

2. **Create New App:**
   - Apps → Create App
   - Connect GitHub
   - Select repository

3. **Configure Components:**
   ```
   Backend:
   - Type: Web Service
   - Build Command: pip install -r requirements.txt
   - Run Command: uvicorn server:app --host 0.0.0.0 --port 8080
   - HTTP Port: 8080
   
   Frontend:
   - Type: Static Site
   - Build Command: yarn build
   - Output Directory: build
   ```

4. **Add Environment Variables**
5. **Deploy**

---

### Option 4: Full Railway Deployment (Backend + Frontend)

Railway can also host React apps. To deploy both:

1. **Create Two Railway Services from same repo:**
   - Service 1: Backend (root: `/backend`)
   - Service 2: Frontend (root: `/frontend`)

2. **Configure Frontend Service:**
   ```
   Build Command: yarn install && yarn build
   Start Command: npx serve -s build -l $PORT
   ```

3. **Add environment variables to both**

---

## Environment Variables

### Backend Environment Variables (.env)

```env
# Required
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=indowater_db
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend.vercel.app

# Optional - Payment Gateways
MIDTRANS_SERVER_KEY=
MIDTRANS_CLIENT_KEY=
MIDTRANS_IS_PRODUCTION=false
XENDIT_API_KEY=
XENDIT_WEBHOOK_TOKEN=

# Optional - Features
ENABLE_CHATBOT=false
ENABLE_OCR=false
```

### Frontend Environment Variables (.env.production)

```env
REACT_APP_BACKEND_URL=https://your-backend.railway.app
```

---

## Post-Deployment Steps

### 1. Custom Domain (Optional)

**For Vercel:**
```
1. Go to Project Settings → Domains
2. Add your custom domain (e.g., indowater.com)
3. Configure DNS records as shown
```

**For Railway:**
```
1. Go to Project Settings → Domains
2. Click "Generate Domain" or add custom domain
3. Configure DNS records
```

### 2. SSL Certificates

Both Vercel and Railway automatically provide SSL certificates for HTTPS.

### 3. Monitoring and Logs

**Railway:**
- View logs: Dashboard → Deployments → Logs
- Metrics: Dashboard → Metrics

**Vercel:**
- View logs: Dashboard → Deployments → Function Logs
- Analytics: Dashboard → Analytics

### 4. Continuous Deployment

Both platforms support automatic deployments from GitHub:
- Push to `main` branch → Automatic production deployment
- Push to other branches → Preview deployments

### 5. Database Backups

**MongoDB Atlas:**
```
1. Go to Clusters → [...] → Backup
2. Enable Cloud Backup (free on M10+ clusters)
3. Or use manual backups:
   mongodump --uri="your-mongodb-atlas-uri"
```

---

## Troubleshooting

### Backend Issues

**Issue:** Backend not starting
```
Solution:
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Check requirements.txt includes all dependencies
4. Verify Python version is 3.11
```

**Issue:** Database connection fails
```
Solution:
1. Verify MONGO_URL is correct
2. Check MongoDB Atlas network access (allow 0.0.0.0/0)
3. Verify database user credentials
4. Check if database exists
```

**Issue:** CORS errors
```
Solution:
1. Verify CORS_ORIGINS includes your Vercel URL
2. Make sure URL has no trailing slash
3. Redeploy backend after updating CORS_ORIGINS
```

### Frontend Issues

**Issue:** Frontend can't connect to backend
```
Solution:
1. Verify REACT_APP_BACKEND_URL is correct
2. Check backend is running (curl backend URL)
3. Verify backend has correct CORS settings
4. Rebuild frontend after changing env variables
```

**Issue:** Build fails on Vercel
```
Solution:
1. Check package.json for correct dependencies
2. Verify Node version compatibility
3. Check build logs for specific errors
4. Try running `yarn build` locally first
```

**Issue:** Routes not working (404 on refresh)
```
Solution:
1. Verify vercel.json includes rewrites configuration
2. Check React Router is configured correctly
```

---

## Cost Estimation

### Free Tier (Development/Small Scale)
```
- Railway: Free tier (500 hours/month, 512MB RAM)
- Vercel: Free tier (unlimited, 100GB bandwidth)
- MongoDB Atlas: Free tier (M0, 512MB storage)
Total: $0/month
```

### Paid Tier (Production)
```
- Railway: $5-20/month (depending on usage)
- Vercel: $20/month (Pro plan, more bandwidth)
- MongoDB Atlas: $9-57/month (M10-M20 cluster)
Total: $34-97/month
```

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong passwords for database
- [ ] Enable MongoDB Atlas network access restrictions
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS (automatic on Vercel/Railway)
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

---

## Performance Optimization

1. **Backend:**
   - Enable Redis caching (Railway addon)
   - Optimize database queries with indexes
   - Use connection pooling

2. **Frontend:**
   - Enable CDN (automatic on Vercel)
   - Code splitting
   - Image optimization
   - Lazy loading components

---

## Support and Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **MongoDB Atlas Docs:** https://docs.atlas.mongodb.com
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev

---

**Last Updated:** October 13, 2025
**Version:** 1.0
