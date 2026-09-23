#!/bin/bash
# Database backup script

set -e

APP_DIR="/opt/rental_housing_api"
BACKUP_DIR="$APP_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "📦 Starting database backup..."

# Get database credentials from .env
source $APP_DIR/.env

# Create backup
docker-compose -f $APP_DIR/docker-compose.prod.yml exec -T db mysqldump \
    -u$DB_USER \
    -p$DB_PASSWORD \
    $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "✅ Backup completed: ${BACKUP_FILE}.gz"

# Delete backups older than 7 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "🧹 Old backups cleaned up"
