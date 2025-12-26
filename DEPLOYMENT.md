# Deployment Guide - Restaurant QR Code Ordering System

## 🚀 Deploying to Vercel (Frontend) and Render (Backend)

### Prerequisites
- GitHub repository: `aklogiqgen/restaurant-qr`
- Vercel account
- Render account
- PostgreSQL database on Render

---

## 📦 Backend Deployment (Render)

### Step 1: Create PostgreSQL Database
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **PostgreSQL**
3. Configure:
   - **Name**: `restaurant-db`
   - **Database**: `hotel_restaurant_db`
   - **User**: (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: Free
4. Click **"Create Database"**
5. **Copy the connection details** (you'll need these)

### Step 2: Deploy Backend Web Service
1. Click **"New +"** → **Web Service**
2. Connect your GitHub repository: `aklogiqgen/restaurant-qr`
3. Configure:
   - **Name**: `restaurant-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Node
   - **Build Command**: `npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Free

4. **Add Environment Variables**:
   ```
   DB_HOST=<your-postgres-host-from-step-1>
   DB_PORT=5432
   DB_NAME=hotel_restaurant_db
   DB_USER=<your-postgres-user-from-step-1>
   DB_PASSWORD=<your-postgres-password-from-step-1>
   PORT=10000
   NODE_ENV=production
   ```

5. Click **"Create Web Service"**
6. Wait for deployment to complete
7. **Copy your backend URL** (e.g., `https://restaurant-backend.onrender.com`)

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Deploy to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **Project**
3. Import your GitHub repository: `aklogiqgen/restaurant-qr`
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run vercel-build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 2: Add Environment Variable
1. Go to **Project Settings** → **Environment Variables**
2. Add:
   ```
   Name: VITE_API_URL
   Value: <your-backend-url-from-render>
   ```
   Example: `https://restaurant-backend.onrender.com`

3. Click **"Save"**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click **"..."** on latest deployment
3. Click **"Redeploy"**
4. Your frontend URL: `https://restaurant-qr.vercel.app`

---

## ✅ Verify Deployment

### Test Backend:
```bash
curl https://restaurant-backend.onrender.com/health
```
Should return: `{"status":"healthy",...}`

### Test Frontend:
1. Visit: `https://restaurant-qr.vercel.app/menu?table=1`
2. Visit: `https://restaurant-qr.vercel.app/chef`
3. Visit: `https://restaurant-qr.vercel.app/qr-codes`

---

## 🔧 Troubleshooting

### Frontend shows blank page:
- Check browser console for errors
- Verify `VITE_API_URL` is set in Vercel
- Make sure backend URL doesn't end with `/`

### QR Codes/Chef Portal not loading:
- Check if backend is running: visit `/health` endpoint
- Verify environment variables are set correctly
- Check Render logs for backend errors

### Database connection errors:
- Verify all DB environment variables are correct
- Check PostgreSQL database is running on Render
- Ensure database name matches exactly: `hotel_restaurant_db`

---

## 📝 Environment Variables Summary

### Backend (Render):
```env
DB_HOST=<from-render-postgres>
DB_PORT=5432
DB_NAME=hotel_restaurant_db
DB_USER=<from-render-postgres>
DB_PASSWORD=<from-render-postgres>
PORT=10000
NODE_ENV=production
```

### Frontend (Vercel):
```env
VITE_API_URL=<your-backend-url>
```

---

## 🎯 Features Available

- `/menu?table=X` - Customer menu and ordering
- `/chef` - Chef portal for order management
- `/qr-codes` - Generate and download QR codes
- `/order-status` - Real-time order tracking
- `/chat` - AI chatbot (requires additional setup)

---

## 🔄 Updating Your Deployment

Any push to the `main` branch will automatically trigger:
- Vercel redeploy (frontend)
- Render redeploy (backend)

---

## 📞 Support

For issues, check:
1. Vercel deployment logs
2. Render deployment logs
3. Browser developer console
4. GitHub repository: https://github.com/aklogiqgen/restaurant-qr
