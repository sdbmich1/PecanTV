# Database Export Script Usage

This script automates the export of your PecanTV database from the Docker container.

## Quick Start

Export the full database (schema + data) with import script:
```bash
python scripts/export_database.py --type full --create-import-script
```

## Available Options

### Export Types

- `--type full` - Export complete database (schema + data) - **Default**
- `--type data` - Export only data (no table structures)
- `--type schema` - Export only schema (no data)
- `--type csv` - Export each table as separate CSV files
- `--type all` - Export all types (full, data, schema, and CSV)

### Import Script Generation

- `--create-import-script` - Generate an import script for easy restoration
- `--target neon` - Create import script for Neon database (default)
- `--target postgres` - Create import script for PostgreSQL database

## Examples

### Basic Usage
```bash
# Export full database
python scripts/export_database.py

# Export only data
python scripts/export_database.py --type data

# Export schema only
python scripts/export_database.py --type schema
```

### With Import Scripts
```bash
# Export full database with Neon import script
python scripts/export_database.py --type full --create-import-script

# Export full database with PostgreSQL import script
python scripts/export_database.py --type full --create-import-script --target postgres

# Export all types with import script
python scripts/export_database.py --type all --create-import-script
```

### CSV Export
```bash
# Export all tables as CSV files
python scripts/export_database.py --type csv
```

## Output

The script creates a `database_exports/` directory with:

- **SQL files**: Database dumps (`.sql`)
- **CSV files**: Individual table exports (if using `--type csv`)
- **Import scripts**: Shell scripts for easy restoration (if using `--create-import-script`)
- **README**: Instructions and documentation

## Importing to Neon

1. Get your Neon connection string from the Neon console
2. Edit the generated import script and update the credentials:
   ```bash
   NEON_HOST="your-neon-host"
   NEON_PORT="5432"
   NEON_DB="your-db-name"
   NEON_USER="your-username"
   NEON_PASSWORD="your-password"
   ```
3. Run the import script:
   ```bash
   ./database_exports/import_to_neon_*.sh
   ```

## Importing to Local PostgreSQL

1. Edit the generated import script and update the credentials
2. Run the import script:
   ```bash
   ./database_exports/import_to_postgres_*.sh
   ```

## Manual Import

You can also import manually using psql:
```bash
psql "postgresql://USER:PASSWORD@HOST:PORT/DBNAME" < database_exports/pecantv_full_*.sql
```

## Prerequisites

- Docker containers must be running (`docker-compose up -d`)
- The `pecantv_db` container must be healthy
- Python 3.6+ with standard library modules

## Troubleshooting

### Container Not Running
If you get "Container not running" error:
```bash
docker-compose up -d
```

### Permission Issues
Make sure the script is executable:
```bash
chmod +x scripts/export_database.py
```

### Database Connection Issues
Check if the database container is healthy:
```bash
docker ps --filter name=pecantv_db
``` 