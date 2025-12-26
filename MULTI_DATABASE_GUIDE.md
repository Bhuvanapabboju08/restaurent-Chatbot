# Managing Multiple Databases in PostgreSQL

## Overview
PostgreSQL can host multiple databases on the same server. Each database is isolated from others, perfect for different company projects.

---

## Your PostgreSQL Setup

```
PostgreSQL Server (localhost:5432)
├── postgres user (one password for everything)
├── Database 1: company1_project
├── Database 2: company2_project
├── Database 3: company3_project
└── Database 4: hotel_restaurant_db (NEW - this project)
```

**Important:** All databases use the **same postgres user and password**.

---

## Step-by-Step Setup

### Step 1: Find Your PostgreSQL Password

You already have 3 databases running, so you know the password! Check:

1. **Other project .env files** - Look in your other 3 projects:
   ```bash
   # Look for files like:
   .env
   config.js
   database.config.js
   ```

2. **pgAdmin saved password** - Open pgAdmin 4:
   - If it opens without asking password → saved
   - If it asks → that's your password

3. **Try common passwords:**
   - `postgres`
   - `admin`
   - `123456`
   - `root`

### Step 2: Open pgAdmin and Create New Database

1. **Launch pgAdmin 4** (Windows search → pgAdmin 4)

2. **Connect to PostgreSQL server**
   - Click on "PostgreSQL [version]"
   - Enter your password if prompted
   - You should see your 3 existing databases

3. **Create New Database**
   - Right-click "Databases" → "Create" → "Database"
   - **Database name**: `hotel_restaurant_db`
   - **Owner**: `postgres`
   - Click "Save"

4. **Verify Creation**
   - You should now see 4 databases:
     - Your 3 existing ones
     - hotel_restaurant_db (NEW)

### Step 3: Update .env File

Edit `backend/.env` with your PostgreSQL password:

```env
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hotel_restaurant_db
DB_USER=postgres
DB_PASSWORD=your_actual_password_here  # ← CHANGE THIS

# Server Configuration
PORT=5001
NODE_ENV=development
```

**Important:** Replace `your_actual_password_here` with the same password you use for your other 3 databases.

### Step 4: Initialize Database

Run these commands in the backend folder:

```bash
# Test connection first
node test-connection.js

# If successful, initialize database
npm run init-db

# Start the server
npm run dev
```

---

## Common Questions

### Q: Will this affect my other 3 databases?
**A: NO!** Each database is completely isolated. Creating `hotel_restaurant_db` won't touch your other projects.

### Q: Do I need different passwords for each database?
**A: NO!** All databases on the same PostgreSQL server use the same `postgres` user password.

### Q: Can I use a different port?
**A: YES**, but it's not necessary. PostgreSQL can handle multiple databases on port 5432.

### Q: How do I switch between databases?
**A: In code**, just change the `DB_NAME` in your `.env` file.
**A: In pgAdmin**, just click on different databases in the left sidebar.

### Q: What if I want different users per project?
**A: Advanced** - You can create separate PostgreSQL users:
```sql
-- In pgAdmin Query Tool
CREATE USER hotel_user WITH PASSWORD 'hotel_password';
GRANT ALL PRIVILEGES ON DATABASE hotel_restaurant_db TO hotel_user;
```

---

## Troubleshooting

### "Password authentication failed"
- You entered the wrong password in `.env`
- Check your other project config files for the correct password
- Try opening pgAdmin - use the password that works there

### "Database does not exist"
- You forgot to create the database in pgAdmin
- Go back to Step 2 and create `hotel_restaurant_db`

### "Connection refused"
- PostgreSQL service is not running
- **Windows**: services.msc → PostgreSQL → Start
- **Or**: Restart your computer (PostgreSQL usually auto-starts)

### "Port 5432 in use"
- This is normal! All your databases share port 5432
- Don't change the port unless necessary

---

## Example: Multiple Project Structure

```
Your Computer
│
├── PostgreSQL Server (localhost:5432)
│   ├── company1_db (Project 1)
│   ├── company2_db (Project 2)
│   ├── company3_db (Project 3)
│   └── hotel_restaurant_db (Project 4 - NEW)
│
├── Project 1 Folder
│   └── .env (DB_NAME=company1_db)
│
├── Project 2 Folder
│   └── .env (DB_NAME=company2_db)
│
├── Project 3 Folder
│   └── .env (DB_NAME=company3_db)
│
└── Hotel-Rag-Bot (This project)
    └── backend/.env (DB_NAME=hotel_restaurant_db)
```

**All .env files use the SAME DB_PASSWORD!**

---

## Quick Commands Reference

```bash
# Test connection
node test-connection.js

# Initialize database (creates tables + seeds data)
npm run init-db

# Start development server
npm run dev

# View database in pgAdmin
# Just open pgAdmin → expand Databases → hotel_restaurant_db
```

---

## Best Practices

1. ✅ **Use descriptive database names** - `hotel_restaurant_db` not `db1`
2. ✅ **One database per project** - Don't mix company data
3. ✅ **Keep .env files secure** - Add to .gitignore
4. ✅ **Backup databases regularly** - Right-click database → Backup
5. ✅ **Document your databases** - Keep notes on what each database is for

---

## Need Help?

If you still can't find your password:

1. **Check other projects** - Look in their .env or config files
2. **Try pgAdmin** - The password that opens it is the one you need
3. **Reset password** - Open CMD as admin:
   ```bash
   psql -U postgres
   ALTER USER postgres WITH PASSWORD 'newpassword123';
   ```
4. **Contact me** - I can help you troubleshoot further

---

**Remember:** You're just adding a 4th database to your existing PostgreSQL setup. Nothing complicated! 🚀
