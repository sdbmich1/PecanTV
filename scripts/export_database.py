#!/usr/bin/env python3
"""
Database Export Script for PecanTV
Exports data from the Docker PostgreSQL container and prepares it for import.
"""

import os
import subprocess
import sys
import json
from datetime import datetime
import argparse

# Configuration
CONTAINER_NAME = "pecantv_db"
DB_NAME = "pecantv"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
EXPORT_DIR = "database_exports"

def run_command(command, check=True, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def create_export_directory():
    """Create the export directory if it doesn't exist."""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        print(f"📁 Created export directory: {EXPORT_DIR}")

def get_timestamp():
    """Get current timestamp for file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def export_full_database():
    """Export the entire database using pg_dump."""
    timestamp = get_timestamp()
    filename = f"{EXPORT_DIR}/pecantv_full_{timestamp}.sql"
    
    print(f"🔄 Exporting full database to {filename}...")
    
    command = f"docker exec -t {CONTAINER_NAME} pg_dump -U {DB_USER} -d {DB_NAME} > {filename}"
    result = run_command(command, capture_output=False)
    
    if result is not None:
        print(f"✅ Full database exported to: {filename}")
        return filename
    else:
        print("❌ Failed to export full database")
        return None

def export_data_only():
    """Export only data (no schema) using pg_dump."""
    timestamp = get_timestamp()
    filename = f"{EXPORT_DIR}/pecantv_data_{timestamp}.sql"
    
    print(f"🔄 Exporting data only to {filename}...")
    
    command = f"docker exec -t {CONTAINER_NAME} pg_dump -U {DB_USER} -d {DB_NAME} --data-only > {filename}"
    result = run_command(command, capture_output=False)
    
    if result is not None:
        print(f"✅ Data exported to: {filename}")
        return filename
    else:
        print("❌ Failed to export data")
        return None

def export_schema_only():
    """Export only schema (no data) using pg_dump."""
    timestamp = get_timestamp()
    filename = f"{EXPORT_DIR}/pecantv_schema_{timestamp}.sql"
    
    print(f"🔄 Exporting schema only to {filename}...")
    
    command = f"docker exec -t {CONTAINER_NAME} pg_dump -U {DB_USER} -d {DB_NAME} --schema-only > {filename}"
    result = run_command(command, capture_output=False)
    
    if result is not None:
        print(f"✅ Schema exported to: {filename}")
        return filename
    else:
        print("❌ Failed to export schema")
        return None

def export_csv_data():
    """Export data as CSV files for each table."""
    timestamp = get_timestamp()
    csv_dir = f"{EXPORT_DIR}/csv_{timestamp}"
    
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    
    print(f"🔄 Exporting CSV data to {csv_dir}...")
    
    # Get list of tables
    command = f"docker exec -t {CONTAINER_NAME} psql -U {DB_USER} -d {DB_NAME} -t -c \"SELECT tablename FROM pg_tables WHERE schemaname = 'public';\""
    result = run_command(command)
    
    if result is None:
        print("❌ Failed to get table list")
        return None
    
    tables = [line.strip() for line in result.stdout.split('\n') if line.strip()]
    
    exported_files = []
    for table in tables:
        csv_file = f"{csv_dir}/{table}.csv"
        command = f"docker exec -t {CONTAINER_NAME} psql -U {DB_USER} -d {DB_NAME} -c \"\\COPY {table} TO STDOUT WITH CSV HEADER\" > {csv_file}"
        
        result = run_command(command, capture_output=False)
        if result is not None:
            print(f"✅ Exported {table} to {csv_file}")
            exported_files.append(csv_file)
        else:
            print(f"❌ Failed to export {table}")
    
    return csv_dir if exported_files else None

def create_import_script(export_file, target_type="neon"):
    """Create an import script for the exported data."""
    timestamp = get_timestamp()
    script_name = f"{EXPORT_DIR}/import_to_{target_type}_{timestamp}.sh"
    
    if target_type == "neon":
        template = f"""#!/bin/bash
# Import script for Neon database
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🔄 Importing data to Neon database..."

# Replace these with your actual Neon credentials
NEON_HOST="your-neon-host"
NEON_PORT="5432"
NEON_DB="your-db-name"
NEON_USER="your-username"
NEON_PASSWORD="your-password"

# Import the data
psql "postgresql://$NEON_USER:$NEON_PASSWORD@$NEON_HOST:$NEON_PORT/$NEON_DB" < {export_file}

echo "✅ Import completed!"
"""
    else:
        template = f"""#!/bin/bash
# Import script for PostgreSQL database
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🔄 Importing data to PostgreSQL database..."

# Replace these with your actual database credentials
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="pecantv"
DB_USER="postgres"
DB_PASSWORD="your-password"

# Import the data
psql "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" < {export_file}

echo "✅ Import completed!"
"""
    
    with open(script_name, 'w') as f:
        f.write(template)
    
    # Make the script executable
    os.chmod(script_name, 0o755)
    
    print(f"✅ Created import script: {script_name}")
    return script_name

def create_readme(exported_files):
    """Create a README file with instructions."""
    timestamp = get_timestamp()
    readme_file = f"{EXPORT_DIR}/README_{timestamp}.md"
    
    content = f"""# Database Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This directory contains exported data from the PecanTV database.

## Files Exported:

"""
    
    for file_info in exported_files:
        content += f"- **{file_info['type']}**: `{file_info['path']}`\n"
    
    content += """
## Import Instructions:

### For Neon Database:
1. Get your Neon connection string from the Neon console
2. Update the credentials in the import script
3. Run: `./import_to_neon_*.sh`

### For Local PostgreSQL:
1. Update the database credentials in the import script
2. Run: `./import_to_postgres_*.sh`

### Manual Import:
```bash
psql "postgresql://USER:PASSWORD@HOST:PORT/DBNAME" < your_export_file.sql
```

## Notes:
- Full database exports include both schema and data
- Data-only exports contain only the data (no table structures)
- Schema-only exports contain only table structures (no data)
- CSV exports are useful for data analysis or importing into other systems
"""
    
    with open(readme_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Created README: {readme_file}")
    return readme_file

def main():
    parser = argparse.ArgumentParser(description="Export PecanTV database from Docker container")
    parser.add_argument("--type", choices=["full", "data", "schema", "csv", "all"], 
                       default="full", help="Type of export to perform")
    parser.add_argument("--create-import-script", action="store_true", 
                       help="Create import script for Neon")
    parser.add_argument("--target", choices=["neon", "postgres"], 
                       default="neon", help="Target database type for import script")
    
    args = parser.parse_args()
    
    print("🚀 Starting database export...")
    
    # Check if container is running
    check_command = f"docker ps --filter name={CONTAINER_NAME} --format '{{{{.Names}}}}'"
    result = run_command(check_command)
    
    if result is None or CONTAINER_NAME not in result.stdout:
        print(f"❌ Container {CONTAINER_NAME} is not running!")
        print("Please start your Docker containers first:")
        print("docker-compose up -d")
        sys.exit(1)
    
    print(f"✅ Found running container: {CONTAINER_NAME}")
    
    # Create export directory
    create_export_directory()
    
    exported_files = []
    
    # Perform exports based on type
    if args.type in ["full", "all"]:
        file_path = export_full_database()
        if file_path:
            exported_files.append({"type": "Full Database", "path": file_path})
    
    if args.type in ["data", "all"]:
        file_path = export_data_only()
        if file_path:
            exported_files.append({"type": "Data Only", "path": file_path})
    
    if args.type in ["schema", "all"]:
        file_path = export_schema_only()
        if file_path:
            exported_files.append({"type": "Schema Only", "path": file_path})
    
    if args.type in ["csv", "all"]:
        dir_path = export_csv_data()
        if dir_path:
            exported_files.append({"type": "CSV Data", "path": dir_path})
    
    # Create import script if requested
    if args.create_import_script and exported_files:
        # Use the first exported file for the import script
        first_file = exported_files[0]["path"]
        if first_file.endswith('.sql'):
            create_import_script(first_file, args.target)
    
    # Create README
    if exported_files:
        create_readme(exported_files)
    
    print("\n🎉 Export completed successfully!")
    print(f"📁 Check the '{EXPORT_DIR}' directory for exported files.")
    
    if args.create_import_script:
        print("\n📝 Next steps:")
        print("1. Update the credentials in the import script")
        print("2. Run the import script to restore your data")

if __name__ == "__main__":
    main() 