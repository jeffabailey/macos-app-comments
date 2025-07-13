# macOS Applications HTMX App

A simple HTMX-based web application for browsing and copying macOS application descriptions.

## Features

- **Browse Applications**: View all macOS applications in a clean, searchable table
- **Copy Descriptions**: Click on any description or use the copy button to copy to clipboard
- **Search**: Real-time search through applications and descriptions
- **Modern UI**: Beautiful, responsive design with smooth animations
- **Statistics**: Track how many applications you've copied

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```
   
   Or use the convenience script:
   ```bash
   ./run.sh
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:5000`

## How to Use

1. **Browse**: Scroll through the list of applications
2. **Search**: Use the search box to filter applications by name or description
3. **Copy**: Click on any description text or use the "Copy" button to copy the description to your clipboard
4. **Track**: Watch the "Copied Today" counter increase as you copy descriptions

## Technical Details

- **Backend**: Flask with Jinja2 templates
- **Frontend**: HTMX for dynamic interactions
- **Styling**: Modern CSS with gradients and smooth animations
- **Data Source**: Reads from `../applications.json`

## File Structure

```
app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── run.sh             # Convenience script to run the app
├── README.md          # This file
└── templates/
    └── index.html     # Main HTML template with HTMX
```

## Browser Compatibility

The application uses modern web APIs for clipboard functionality:
- **Modern browsers**: Uses the Clipboard API
- **Older browsers**: Falls back to document.execCommand for copying
- **HTTPS required**: Clipboard API requires secure context (HTTPS or localhost) 