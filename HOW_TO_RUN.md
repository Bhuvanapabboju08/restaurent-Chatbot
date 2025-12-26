# How to Run the Server

## ⚠️ Important: Only ONE Server Instance at a Time!

The server uses port 5001. You can only run ONE instance at a time.

---

## 🚀 Starting the Server

### Option 1: Development Mode (Recommended)
Auto-reloads when you change files.

```bash
cd backend
npm run dev
```

You should see:
```
[nodemon] starting `node server-postgres.js`
============================================================
[APP] Restaurant Backend Server (PostgreSQL)
============================================================
[OK] Server running on http://localhost:5001
```

### Option 2: Production Mode
No auto-reload.

```bash
cd backend
npm start
```

---

## 🛑 Stopping the Server

### If running in terminal (foreground):
Press **Ctrl + C**

### If running in background:
```bash
# Find the process
netstat -ano | findstr :5001

# Kill it (replace XXXX with the PID)
taskkill //F //PID XXXX
```

---

## ❌ Error: "Address already in use"

This means a server is already running!

```
Error: listen EADDRINUSE: address already in use :::5001
```

### Solution:

**Option A: Find and kill the existing process**
```bash
# Windows
netstat -ano | findstr :5001
taskkill //F //PID <process_id>
```

**Option B: Close the other terminal**
Look for another terminal/command prompt window running `npm run dev` or `npm start`

**Option C: Restart your computer**
This will kill all Node processes.

---

## ✅ Verify Server is Running

### Method 1: Check terminal output
You should see:
```
[OK] Server running on http://localhost:5001
```

### Method 2: Test in browser
Open: http://localhost:5001/health

Should show:
```json
{
  "status": "healthy",
  "message": "Restaurant Backend API (PostgreSQL)",
  "database": "PostgreSQL"
}
```

### Method 3: Test with curl
```bash
curl http://localhost:5001/health
```

---

## 🔄 Common Workflows

### 1. Start fresh
```bash
# Stop any running server (Ctrl+C or kill process)
cd backend
npm run dev
```

### 2. After code changes
If using `npm run dev` (nodemon), it auto-reloads!
No need to restart manually.

### 3. After database changes
```bash
# Reinitialize database
npm run init-db

# Server auto-reloads if using npm run dev
```

### 4. Test the API
```bash
# Health check
curl http://localhost:5001/health

# Get menu
curl http://localhost:5001/api/menu

# Create order
curl -X POST http://localhost:5001/api/order \
  -H "Content-Type: application/json" \
  -d '{"tableNo":5,"items":[{"name":"Pizza","price":349,"quantity":1}],"total":349}'
```

---

## 📝 Quick Reference

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start with auto-reload ✅ |
| `npm start` | Start production mode |
| `npm run init-db` | Setup/reset database |
| `Ctrl + C` | Stop server |
| `node test-connection.js` | Test database connection |

---

## 🐛 Troubleshooting

### Server won't start - Port in use
```bash
# Kill the process using port 5001
netstat -ano | findstr :5001
taskkill //F //PID <process_id>
```

### Database connection failed
```bash
# Check PostgreSQL is running
# Verify password in .env is: 123

# Test connection
node test-connection.js
```

### Changes not reflecting
- Using `npm start`? Stop and restart manually
- Using `npm run dev`? Should auto-reload
- Check terminal for error messages

### Multiple terminal windows
Only keep ONE terminal with the server running!
Close or stop others to avoid confusion.

---

## 💡 Best Practices

1. ✅ **Use `npm run dev` for development** - Auto-reload is convenient
2. ✅ **Keep only one terminal open** - Avoid confusion
3. ✅ **Check terminal output** - Watch for errors
4. ✅ **Test after starting** - Visit http://localhost:5001/health
5. ✅ **Stop before closing terminal** - Press Ctrl+C first

---

## 🎯 Current Status

**Your server configuration:**
- Port: 5001
- Database: hotel_restaurant_db
- Password: 123
- Auto-reload: Enabled with `npm run dev`

**To start right now:**
```bash
cd backend
npm run dev
```

**Then test:**
http://localhost:5001/health

---

**That's it! Simple and straightforward.** 🚀
