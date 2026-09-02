#!/bin/bash
set -e

# --- Load environment variables ---
set -a
source /var/www/examination/.env.deploy
set +a

# --- Config ---
REMOTE="gdrive:vps-backups"
BACKUP_DIR="/root/db_backups"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
FILENAME="${DB_NAME}_backup_${TIMESTAMP}.sql.gz"
LOCAL_PATH="${BACKUP_DIR}/${FILENAME}"
LOG_FILE="/var/log/db_backup.log"

echo "===== Backup started: $(date) =====" >> "$LOG_FILE"

mkdir -p "$BACKUP_DIR"

# --- Step 1: Dump and compress ---
echo "Dumping database..." >> "$LOG_FILE"
PGPASSWORD="$DB_PASSWORD" pg_dump -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" "$DB_NAME" | gzip > "$LOCAL_PATH"

if [ ! -s "$LOCAL_PATH" ]; then
    echo "ERROR: Backup file is empty or missing. Aborting upload." >> "$LOG_FILE"
    exit 1
fi

echo "Dump complete: $LOCAL_PATH ($(du -h "$LOCAL_PATH" | cut -f1))" >> "$LOG_FILE"

# --- Step 2: Upload to Google Drive ---
echo "Uploading to Google Drive..." >> "$LOG_FILE"
rclone copy "$LOCAL_PATH" "$REMOTE" >> "$LOG_FILE" 2>&1

# --- Step 3: Enforce retention — keep only the 3 most recent backups on Drive ---
echo "Checking retention policy..." >> "$LOG_FILE"

FILES=$(rclone lsf "$REMOTE" --format "tp" --separator "|" | sort | awk -F'|' '{print $2}')
COUNT=$(echo "$FILES" | wc -l)

if [ "$COUNT" -gt 3 ]; then
    TO_DELETE=$(echo "$FILES" | head -n $((COUNT - 3)))
    for FILE in $TO_DELETE; do
        echo "Deleting old backup: $FILE" >> "$LOG_FILE"
        rclone deletefile "${REMOTE}/${FILE}"
    done
fi

# --- Step 4: Clean up local copy ---
rm -f "$LOCAL_PATH"

echo "Backup finished successfully: $(date)" >> "$LOG_FILE"
echo "=====================================" >> "$LOG_FILE"
