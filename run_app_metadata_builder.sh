#!/bin/sh

# App Metadata Builder Runner
# Simple wrapper for app_metadata_builder.py

if [ ! -f "app_metadata_builder.py" ]; then
    echo "Error: app_metadata_builder.py not found!"
    exit 1
fi

python3 app_metadata_builder.py 