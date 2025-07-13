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

```bash
# Generate app descriptions
./run_python.sh

# Or run directly
python3 app_metadata_builder.py
```

## Output

Creates `applications.json` with app descriptions:

```json
{
  "Safari": "Web browser for macOS",
  "Chrome": "Web browser developed by Google"
}
```

## Files

- `app_metadata_builder.py` - Main script
- `run_python.sh` - Runner script
- `setup.sh` - Setup script
- `test_python.py` - Tests 