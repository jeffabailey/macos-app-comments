#!/bin/sh

# Simple test runner for App Metadata Builder

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Running tests..."

# Check required files
for file in "app_metadata_builder.py" "run_python.sh" "setup.sh" "README.md"; do
    if [ ! -f "$file" ]; then
        echo "${RED}Missing: $file${NC}"
        exit 1
    fi
done

# Run Python tests if venv exists
if [ -d "venv" ] && [ -f "test_python.py" ]; then
    echo "Running Python tests..."
    source venv/bin/activate && python test_python.py
    if [ $? -eq 0 ]; then
        echo "${GREEN}Python tests passed!${NC}"
    else
        echo "${RED}Python tests failed!${NC}"
        exit 1
    fi
else
    echo "${YELLOW}Skipping Python tests (venv or test file not found)${NC}"
fi

# Run Python linter if venv exists
if [ -d "venv" ]; then
    echo "Running Python linter..."
    source venv/bin/activate
    
    # Check if flake8 is installed
    if python -c "import flake8" 2>/dev/null; then
        # Run flake8 on all Python files
        flake8 *.py --max-line-length=90 --ignore=E203,W503 --extend-ignore=E501
        if [ $? -eq 0 ]; then
            echo "${GREEN}Python linting passed!${NC}"
        else
            echo "${RED}Python linting failed!${NC}"
            exit 1
        fi
    else
        echo "${YELLOW}flake8 not found. Installing flake8...${NC}"
        pip install flake8
        if [ $? -eq 0 ]; then
            echo "Running Python linter..."
            flake8 *.py --max-line-length=90 --ignore=E203,W503 --extend-ignore=E501
            if [ $? -eq 0 ]; then
                echo "${GREEN}Python linting passed!${NC}"
            else
                echo "${RED}Python linting failed!${NC}"
                exit 1
            fi
        else
            echo "${RED}Failed to install flake8${NC}"
            exit 1
        fi
    fi
else
    echo "${YELLOW}Skipping Python linting (venv not found)${NC}"
fi

# Basic integration tests
echo "Running integration tests..."

# Check if scripts are executable
[ -x "run_python.sh" ] || (echo "${RED}run_python.sh not executable${NC}" && exit 1)

# Check required commands
for cmd in "python3" "sh"; do
    command -v "$cmd" > /dev/null 2>&1 || (echo "${RED}$cmd not found${NC}" && exit 1)
done

# Check /Applications exists
[ -d "/Applications" ] || (echo "${RED}/Applications not found${NC}" && exit 1)

# Test Python help
if [ -d "venv" ]; then
    source venv/bin/activate && python app_metadata_builder.py --help > /dev/null 2>&1 || (echo "${RED}Python help failed${NC}" && exit 1)
fi

# Test Goose CLI
if command -v goose > /dev/null 2>&1; then
    goose --version > /dev/null 2>&1 || (echo "${RED}Goose CLI not working${NC}" && exit 1)
    echo "${GREEN}Goose CLI found and working${NC}"
else
    echo "${YELLOW}Goose CLI not found (install with: brew install goose)${NC}"
fi

# Test new functionality
echo "Testing new functionality..."

# Test that the script can create prompt file
if [ -d "venv" ]; then
    source venv/bin/activate
    
    # Test basic functionality without running full process
    python -c "
import app_metadata_builder
import os
from unittest.mock import patch, MagicMock

# Mock os.listdir to return test apps
with patch('os.listdir', return_value=['Safari.app', 'Chrome.app']):
    with patch('os.path.isdir', return_value=True):
        with patch('app_metadata_builder.get_app_details') as mock_details:
            def mock_details_side_effect(app_path, app_name):
                if app_name == 'Safari':
                    return {
                        'name': 'Safari',
                        'path': '/Applications/Safari.app',
                        'description': 'Test browser',
                        'version': '1.0',
                        'bundle_identifier': 'com.test.safari'
                    }
                elif app_name == 'Chrome':
                    return {
                        'name': 'Chrome',
                        'path': '/Applications/Chrome.app',
                        'description': 'Test browser',
                        'version': '1.0',
                        'bundle_identifier': 'com.test.chrome'
                    }
                return {'name': app_name, 'path': app_path, 'description': '', 'version': '', 'bundle_identifier': ''}
            
            mock_details.side_effect = mock_details_side_effect
            apps = app_metadata_builder.get_applications()
            assert len(apps) == 2
            assert apps[0]['name'] == 'Chrome'  # Alphabetically sorted
            assert apps[1]['name'] == 'Safari'
print('Basic functionality test passed')
"
    if [ $? -eq 0 ]; then
        echo "${GREEN}Basic functionality test passed!${NC}"
    else
        echo "${RED}Basic functionality test failed!${NC}"
        exit 1
    fi
fi

# Check for required Python modules
if [ -d "venv" ]; then
    source venv/bin/activate
    python -c "import plistlib; import json; import subprocess; import jinja2; print('Required modules available')" 2>/dev/null || (echo "${RED}Missing required Python modules (install with: pip install jinja2)${NC}" && exit 1)
fi

echo "${GREEN}All tests passed!${NC}" 