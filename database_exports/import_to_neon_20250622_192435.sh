#!/bin/bash
# Import script for Neon database
# Generated on 2025-06-22 19:24:35

echo "🔄 Importing data to Neon database..."

# Replace these with your actual Neon credentials
NEON_HOST="ep-cool-name-123456.us-east-2.aws.neon.tech"
NEON_PORT="5432"
NEON_DB="neondb"
NEON_USER="pecantv"
NEON_PASSWORD="your-password"

# Import the data with SSL mode required
psql "postgresql://$NEON_USER:$NEON_PASSWORD@$NEON_HOST:$NEON_PORT/$NEON_DB?sslmode=require" < database_exports/pecantv_full_20250622_192434.sql

if [ $? -eq 0 ]; then
    echo "✅ Import completed successfully!"
else
    echo "❌ Import failed. Please check your credentials and try again."
    echo ""
    echo "Common issues:"
    echo "1. Verify your Neon username and password"
    echo "2. Make sure the database exists in Neon"
    echo "3. Check that your IP is allowed in Neon's connection settings"
    echo ""
    echo "You can also try connecting manually to test:"
    echo "psql \"postgresql://$NEON_USER:****@$NEON_HOST:$NEON_PORT/$NEON_DB?sslmode=require\""
fi
