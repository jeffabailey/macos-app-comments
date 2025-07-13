#!/bin/sh

# Simple setup script for app metadata builder

set -e

# Check if Python 3 is available
command -v python3 > /dev/null 2>&1 || (echo "Python 3 not found" && exit 1)

# Create virtual environment if it doesn't exist
[ -d "venv" ] || python3 -m venv venv

echo "Setup complete. Run './run_python.sh' to start." 