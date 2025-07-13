#!/bin/sh

# Simple test runner for App Metadata Builder

set -e

echo "Running tests..."

# Check required files
for file in "app_metadata_builder.py" "setup.sh" "README.md"; do
    if [ ! -f "$file" ]; then
        echo "Missing: $file"
        exit 1
    fi
done

# Setup virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    ./setup.sh
fi

# Activate virtual environment
# shellcheck disable=SC1091
. venv/bin/activate

# Run Python tests if test file exists
if [ -f "test_python.py" ]; then
    echo "Running Python tests..."
    python test_python.py
fi

# Run Python linter
echo "Running Python linter..."
pip install flake8 >/dev/null 2>&1 || true
flake8 ./*.py --max-line-length=90 --ignore=E203,W503 --extend-ignore=E501 || echo "Linting issues found"

# Basic functionality test
echo "Testing basic functionality..."
python -c "
import app_metadata_builder
import os
from unittest.mock import patch

with patch('os.listdir', return_value=['Safari.app', 'Chrome.app']):
    with patch('os.path.isdir', return_value=True):
        with patch('app_metadata_builder.get_app_details') as mock_details:
            def mock_details_side_effect(app_path, app_name):
                return {
                    'name': app_name,
                    'path': f'/Applications/{app_name}.app',
                    'description': 'Test app',
                    'version': '1.0',
                    'bundle_identifier': f'com.test.{app_name.lower()}'
                }
            
            mock_details.side_effect = mock_details_side_effect
            apps = app_metadata_builder.get_applications()
            assert len(apps) == 2
print('Basic functionality test passed')
"

# Check for required Python modules
python -c "import plistlib, json, subprocess, jinja2; print('Required modules available')"

echo "All tests completed!" 