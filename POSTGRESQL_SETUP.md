# PostgreSQL Backend Setup Guide

## Overview
This guide will help you set up the PostgreSQL backend for the Hotel-Rag-Bot Restaurant application using pgAdmin.

---

## Prerequisites

1. **PostgreSQL** (v12 or higher)
2. **pgAdmin 4** (PostgreSQL GUI)
3. **Node.js** (v14 or higher)
4. **npm** or **yarn**

---

## Step 1: Install PostgreSQL and pgAdmin

### Windows
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. During installation:
   - Set a password for the `postgres` user (remember this!)
   - Default port: `5432`
   - pgAdmin 4 is included in the installer

### macOS
```bash
# Using Homebrew
brew install postgresql
brew install --cask pgadmin4

# Start PostgreSQL service
brew services start postgresql
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo apt install pgadmin4

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## Step 2: Create Database using pgAdmin

### Launch pgAdmin
1. Open **pgAdmin 4**
2. Connect to PostgreSQL server:
   - Right-click on "Servers" → "Register" → "Server"
   - **Name**: Local PostgreSQL
   - **Connection Tab**:
     - Host: `localhost`
     - Port: `5432`
     - Username: `postgres`
     - Password: (your postgres password)
   - Click "Save"

### Create Database
1. In pgAdmin, right-click on "Databases" → "Create" → "Database"
2. **Database name**: `hotel_restaurant_db`
3. **Owner**: `postgres`
4. Click "Save"

---

## Step 3: Setup Backend Project

### 1. Install Dependencies
```bash
cd backend
npm install
```

This will install:
- `pg` - PostgreSQL client for Node.js
- `express` - Web framework
- `socket.io` - Real-time communication
- `cors` - Cross-origin resource sharing
- `dotenv` - Environment variable management

### 2. Create Environment File
```bash
# Copy the example environment file
cp .env.example .env
```

### 3. Configure Environment Variables
Edit the `.env` file with your PostgreSQL credentials:

```env
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hotel_restaurant_db
DB_USER=postgres
DB_PASSWORD=your_actual_password

# Server Configuration
PORT=5001
NODE_ENV=development

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Step 4: Initialize Database

### Method 1: Using pgAdmin (Manual)

1. In pgAdmin, select your database (`hotel_restaurant_db`)
2. Click on "Query Tool" (or press Alt+Shift+Q)
3. Open and run the schema file:
   - Click "Open File" icon
   - Navigate to `backend/database/schema.sql`
   - Click "Execute" (F5)
4. Verify tables were created:
   - Expand "Schemas" → "public" → "Tables"
   - You should see: `menu_items`, `orders`, `order_items`
5. Seed the data:
   - Open `backend/database/seedData.sql` in Query Tool
   - Click "Execute" (F5)

### Method 2: Using Node.js Script (Automated)

```bash
# From backend directory
node database/init.js
```

This will:
- Create all tables, indexes, and triggers
- Seed menu items from seedData.js
- Display success messages

---

## Step 5: Start the Server

### Development Mode (with auto-restart)
```bash
npm run dev
```

### Production Mode
```bash
npm start
```

You should see:
```
============================================================
[APP] Restaurant Backend Server (PostgreSQL)
============================================================
[OK] Server running on http://localhost:5001
[OK] Socket.io enabled for real-time updates
[OK] Database: PostgreSQL
[OK] Host: localhost:5432
[OK] Database Name: hotel_restaurant_db
============================================================
```

---

## Step 6: Verify Installation

### 1. Test Database Connection
```bash
# In another terminal
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Restaurant Backend API (PostgreSQL)",
  "timestamp": "2025-10-23T...",
  "database": "PostgreSQL"
}
```

### 2. Test Menu API
```bash
curl http://localhost:5001/api/menu
```

Should return a list of menu items.

### 3. Using pgAdmin to View Data
1. In pgAdmin, select your database
2. Right-click on `menu_items` table → "View/Edit Data" → "All Rows"
3. You should see 22 menu items (appetizers, mains, desserts, beverages)

---

## Database Schema

### Tables

#### **menu_items**
- `id` (SERIAL PRIMARY KEY)
- `name` (VARCHAR) - Item name
- `description` (TEXT) - Item description
- `price` (DECIMAL) - Price in rupees
- `category` (VARCHAR) - appetizer, main, dessert, beverage
- `image` (VARCHAR) - Image URL
- `available` (BOOLEAN) - Availability status
- `rating` (DECIMAL) - Rating out of 5
- `prep_time` (INTEGER) - Preparation time in minutes
- `is_veg` (BOOLEAN) - Vegetarian flag
- `spice_level` (INTEGER) - Spice level 0-5
- `popular` (BOOLEAN) - Popular item flag
- `chef_special` (BOOLEAN) - Chef's special flag
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### **orders**
- `id` (SERIAL PRIMARY KEY)
- `table_no` (INTEGER) - Table number
- `total` (DECIMAL) - Total order amount
- `status` (VARCHAR) - pending, confirmed, preparing, ready, served, cancelled
- `estimated_time` (INTEGER) - Estimated time in minutes
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### **order_items**
- `id` (SERIAL PRIMARY KEY)
- `order_id` (INTEGER) - Foreign key to orders
- `name` (VARCHAR) - Item name
- `price` (DECIMAL) - Item price
- `quantity` (INTEGER) - Quantity ordered
- `category` (VARCHAR) - Item category
- `image` (VARCHAR) - Item image URL
- `prep_time` (INTEGER) - Preparation time
- `created_at` (TIMESTAMP)

---

## API Endpoints

### Menu Endpoints
- `GET /api/menu` - Get all menu items
- `GET /api/menu?category=appetizer` - Filter by category
- `GET /api/menu/:id` - Get single menu item

### Order Endpoints
- `POST /api/order` - Create new order
- `GET /api/order/:id` - Get order by ID
- `GET /api/orders` - Get all orders
- `GET /api/orders?status=pending` - Filter by status
- `PUT /api/order/:id/status` - Update order status

### Admin Endpoints
- `POST /api/init-db` - Initialize database (creates schema + seeds data)
- `POST /api/seed-menu` - Re-seed menu items

---

## Troubleshooting

### Connection Errors

**Error**: `ECONNREFUSED`
- **Solution**: Ensure PostgreSQL service is running
  - Windows: Services → PostgreSQL → Start
  - macOS: `brew services start postgresql`
  - Linux: `sudo systemctl start postgresql`

**Error**: `password authentication failed`
- **Solution**: Check your `.env` file has the correct password

**Error**: `database "hotel_restaurant_db" does not exist`
- **Solution**: Create the database in pgAdmin (Step 2)

### Port Already in Use

**Error**: `Port 5001 is already in use`
- **Solution**: Change PORT in `.env` file or kill the process using port 5001

### Schema Issues

**Error**: Tables not found
- **Solution**: Run the initialization script:
  ```bash
  node database/init.js
  ```

---

## Using pgAdmin Features

### Query Tool
- Execute custom SQL queries
- View query execution plans
- Export results to CSV/JSON

### Data Viewer
- Browse table data in grid format
- Edit data directly (double-click cells)
- Filter and sort data

### Monitoring
- View active connections: Right-click Database → "Dashboard"
- Monitor query performance
- View server logs

### Backup & Restore
1. Right-click database → "Backup"
2. Choose format (Custom, Tar, Plain)
3. Select file location
4. To restore: Right-click database → "Restore"

---

## Package.json Scripts

```json
{
  "scripts": {
    "start": "node server-postgres.js",
    "dev": "nodemon server-postgres.js",
    "init-db": "node database/init.js"
  }
}
```

---

## Production Deployment Tips

1. **Environment Variables**: Use strong passwords
2. **Connection Pooling**: Already configured (max 20 connections)
3. **SSL**: Enable SSL for production databases
4. **Indexes**: Already created for common queries
5. **Backups**: Schedule regular database backups
6. **Monitoring**: Use pgAdmin or tools like pgBadger

---

## Comparing with MongoDB Version

| Feature | MongoDB (Old) | PostgreSQL (New) |
|---------|---------------|------------------|
| Database Type | NoSQL | SQL (Relational) |
| Schema | Flexible | Strict Schema |
| Transactions | Limited | ACID Compliant |
| Queries | JavaScript-like | SQL |
| Relations | Manual | Foreign Keys |
| GUI Tool | MongoDB Compass | pgAdmin |
| Free Tier | 512 MB (Atlas) | Unlimited (Self-hosted) |

---

## Next Steps

1. **Frontend Integration**: Update frontend to use the new PostgreSQL backend
2. **Authentication**: Add user authentication and authorization
3. **Analytics**: Create views for sales reports and analytics
4. **Payment Integration**: Add payment gateway integration
5. **File Upload**: Add image upload for menu items

---

## Support

For issues or questions:
- PostgreSQL Docs: https://www.postgresql.org/docs/
- pgAdmin Docs: https://www.pgadmin.org/docs/
- Node.js pg library: https://node-postgres.com/

---

**Happy Coding!** 🚀
