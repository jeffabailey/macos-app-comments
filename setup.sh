#!/bin/sh

# Simple setup script for app metadata builder

set -e

# Check if Python 3 is available
command -v python3 > /dev/null 2>&1 || (echo "Python 3 not found" && exit 1)

# Create virtual environment if it doesn't exist
[ -d "venv" ] || python3 -m venv venv

# Activate virtual environment and install requirements
# shellcheck disable=SC1091
. venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "Setup complete. Run 'python3 app_metadata_builder.py' to start." 