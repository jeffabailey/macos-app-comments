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

# Check for unused imports
echo "Checking for unused imports..."
python -c "
import ast
import os
import sys

def check_unused_imports(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    # Get all imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    
    # Get all names used in the file
    used_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            # Handle cases like Template.render()
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
    
    # Check for unused imports
    unused = []
    for imp in imports:
        if imp not in used_names:
            # Skip if it's a test file importing the main module
            if file_path.endswith('test_python.py') and imp == 'app_metadata_builder':
                continue
            if file_path.endswith('debug_test.py') and imp == 'app_metadata_builder':
                continue
            unused.append(imp)
    
    if unused:
        print(f'Unused imports in {file_path}: {unused}')
        return False
    return True

all_good = True
for py_file in [f for f in os.listdir('.') if f.endswith('.py')]:
    if not check_unused_imports(py_file):
        all_good = False

if not all_good:
    print('Unused imports found!')
    exit(1)
else:
    print('No unused imports found.')
"

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