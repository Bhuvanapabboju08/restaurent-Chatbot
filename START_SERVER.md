# How to Start Your Server (Simple Guide)

## ✅ Port 5001 is NOW FREE!

I just killed the background server. You can now start your own.

---

## 🚀 Start Your Server (Right Now!)

**In your terminal** (backend folder):

```bash
npm run dev
```

That's it! You should see:
```
[OK] Server running on http://localhost:5001
```

---

## ⚠️ If You Still Get "Port in Use" Error

This means there's STILL a process on port 5001.

### Quick Fix (Copy-Paste These Commands):

```bash
# Step 1: Find what's using port 5001
netstat -ano | findstr :5001

# Step 2: Kill it (replace XXXX with the PID from above)
taskkill //F //PID XXXX

# Step 3: Start your server
npm run dev
```

---

## 💡 Understanding the Problem

**What happened:**
1. I started a server in the background (to help you)
2. You tried to start ANOTHER server in YOUR terminal
3. Both tried to use port 5001 → Error!

**Solution:**
- Only ONE server can use port 5001 at a time
- I killed my background server
- Now YOU can run yours

---

## ✅ Verify Server is Running

After running `npm run dev`, check:

1. **Terminal shows:**
   ```
   [OK] Server running on http://localhost:5001
   ```

2. **Test in browser:**
   ```
   http://localhost:5001/health
   ```

3. **Test API:**
   ```bash
   curl http://localhost:5001/health
   ```

---

## 🎯 Simple Rule

**ONE TERMINAL = ONE SERVER**

Don't run `npm run dev` in multiple terminals!

---

## 🛑 Stop Your Server

When you want to stop:
```
Press Ctrl + C in the terminal
```

---

## 🔄 Restart Server

If you need to restart:
```bash
# Stop with Ctrl + C, then:
npm run dev
```

---

**That's all! Port is free, just run `npm run dev` now!** 🚀
