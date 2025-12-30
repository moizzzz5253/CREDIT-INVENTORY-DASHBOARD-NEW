#!/bin/bash
set -e

# Ensure data directory exists and is writable
mkdir -p /app/data
chmod 777 /app/data || true

# Copy database from mounted location to writable volume on first run
if [ -f /app/backend-mount/inventory.db ] && [ ! -f /app/data/inventory.db ]; then
    echo "Copying database from mounted location to writable volume..."
    cp /app/backend-mount/inventory.db /app/data/inventory.db
    chmod 666 /app/data/inventory.db || true
    echo "Database copied successfully."
fi

# Ensure database file is writable
if [ -f /app/data/inventory.db ]; then
    chmod 666 /app/data/inventory.db || true
fi

# Copy QR codes from mounted location to writable volume on first run
if [ -d /app/backend-mount/qr_codes ] && [ -z "$(ls -A /app/qr_codes 2>/dev/null)" ]; then
    echo "Copying QR codes from mounted location to writable volume..."
    cp -r /app/backend-mount/qr_codes/* /app/qr_codes/ 2>/dev/null || true
    echo "QR codes copied successfully."
fi

# Copy uploads from mounted location to writable volume on first run
if [ -d /app/backend-mount/uploads ] && [ -z "$(ls -A /app/uploads 2>/dev/null)" ]; then
    echo "Copying uploads from mounted location to writable volume..."
    cp -r /app/backend-mount/uploads/* /app/uploads/ 2>/dev/null || true
    echo "Uploads copied successfully."
fi

# Ensure directories are writable (named volumes should already be writable)
chmod -R 777 /app/qr_codes /app/uploads /app/data 2>/dev/null || true

# Execute the main command
exec "$@"

