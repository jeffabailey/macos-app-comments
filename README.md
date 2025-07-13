# macOS App Comments

Generate descriptions for macOS applications using Goose CLI.

## Setup

```bash
# Install Goose CLI
brew install goose

# Setup Python environment
./setup.sh
```

## Usage

### Command Line

```bash
# Generate app descriptions
python3 app_metadata_builder.py
```

### Web Interface

The project includes a web application for browsing and copying app descriptions:

```bash
# Navigate to the app directory
cd app

# Install web app dependencies
pip install -r requirements.txt

# Run the web application
python app.py
```

Then open your browser to `http://localhost:1337`

## Output

Creates `applications.json` with app descriptions:

```json
{
  "Safari": "Web browser for macOS",
  "Chrome": "Web browser developed by Google"
}
```

## Files

- `app_metadata_builder.py` - Main script for generating app descriptions
- `setup.sh` - Setup script for Python environment
- `test_python.py` - Tests
- `./app/` - Web interface for browsing and copying app descriptions
  - `app.py` - Flask web application
  - `templates/` - HTML templates
  - `static/` - CSS and JavaScript files
