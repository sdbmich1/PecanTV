# Neon Database Import Guide

## Option 1: Using Neon Web Interface (Recommended)

### Step 1: Set Up Neon Project
1. Go to [https://console.neon.tech/](https://console.neon.tech/)
2. Create a new project (if you haven't already)
3. Set up a database user with a password

### Step 2: Import via Web Interface
1. In your Neon project, look for **"Import Data"** option
2. Choose **"From a file"** or **"From a database dump"**
3. Upload the file: `database_exports/pecantv_full_20250622_192434.sql`
4. Follow the prompts to complete the import

### Step 3: Get Connection String
1. After import, go to **Connection Details**
2. Copy the connection string for your app

---

## Option 2: Using Command Line Script

### Step 1: Get Connection String from Neon
1. In your Neon project, go to **Connection Details**
2. Copy the connection string (looks like):
   ```
   postgresql://username:password@host:port/database?sslmode=require
   ```

### Step 2: Update the Import Script
1. Open: `database_exports/import_to_neon_simple.sh`
2. Replace the placeholder with your actual connection string
3. Save the file

### Step 3: Run the Import
```bash
./database_exports/import_to_neon_simple.sh
```

---

## Option 3: Manual Import

### Step 1: Get Connection Details
From Neon console, note:
- **Host**: `ep-cool-name-123456.us-east-2.aws.neon.tech`
- **Port**: `5432`
- **Database**: `neondb` (or your database name)
- **Username**: Your Neon username
- **Password**: Your Neon password

### Step 2: Run Import Command
```bash
psql "postgresql://username:password@host:port/database?sslmode=require" < database_exports/pecantv_full_20250622_192434.sql
```

---

## After Import: Update Your App

Once data is imported, update your app's database configuration:

### For FastAPI (api/database.py)
```python
# Replace the DATABASE_URL with your Neon connection string
DATABASE_URL = "postgresql://username:password@host:port/database?sslmode=require"
```

### For iOS App
Update the API base URL if needed (should still be `localhost:8000` for local development)

---

## Troubleshooting

### Connection Issues
- Make sure you've created a database user with a password
- Verify the connection string format
- Check that your IP is allowed in Neon's settings

### Import Issues
- Ensure the SQL file exists: `database_exports/pecantv_full_20250622_192434.sql`
- Check file permissions: `chmod +x database_exports/import_to_neon_simple.sh`
- Verify the database exists in Neon

### SSL Issues
- Neon requires SSL: always include `?sslmode=require` in connection strings

---

## Files Available for Import

- **Full Database**: `pecantv_full_20250622_192434.sql` (56KB) - **Recommended**
- **Data Only**: `pecantv_data_20250622_192458.sql` (41KB) - Use if schema already exists
- **Import Script**: `import_to_neon_simple.sh` - Command line import 