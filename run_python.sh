#!/bin/sh

# Simple runner for app metadata builder

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run './setup.sh' first."
    exit 1
fi

# Activate virtual environment and run script
source venv/bin/activate
python3 app_metadata_builder.py "$@" 