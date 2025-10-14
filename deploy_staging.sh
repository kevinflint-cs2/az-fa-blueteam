#!/bin/bash
# Script to create a clean zip for Azure Functions deployment, excluding local.settings.json and dev files.

set -e

STAGING_DIR="deploy_staging"
ZIP_NAME="az_fa_blueteam.zip"

# Clean up any previous staging
rm -rf "$STAGING_DIR" "$ZIP_NAME"

# Create staging directory
mkdir -p "$STAGING_DIR"

# Copy necessary files and folders
cp function_app.py host.json requirements.txt "$STAGING_DIR"/
cp -r functions "$STAGING_DIR"/

# (Optional) Copy other needed files here
# cp -r static "$STAGING_DIR"/
# cp proxies.json "$STAGING_DIR"/


# Remove __pycache__ and *.pyc files from staging before zipping
find "$STAGING_DIR" -type d -name '__pycache__' -exec rm -rf {} +
find "$STAGING_DIR" -name '*.pyc' -delete

# Create the zip from inside the staging directory
cd "$STAGING_DIR"
zip -r "../$ZIP_NAME" .
cd ..

# Clean up staging directory
rm -rf "$STAGING_DIR"

echo "Created $ZIP_NAME for deployment."
