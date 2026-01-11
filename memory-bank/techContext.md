# Technical Context

## Technologies

- **Python 3.7+**: Core language
- **requests**: HTTP library for API calls and downloads
- **tqdm**: Progress bar display
- **selenium**: Browser automation for cookie extraction (optional)
- **argparse**: Command-line argument parsing

## Dependencies

```
requests
tqdm
selenium
```

## Setup

1. Create virtual environment: `python3 -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install: `pip install -r requirements.txt`

## Runtime Requirements

- Python 3.7+
- Internet connection
- Chrome browser (for automatic cookie extraction, optional)

## File Structure

```
gdrive_videoloader.py  # Main script (single file)
requirements.txt       # Dependencies
README.md             # Documentation
cookies.json          # Generated cookie file (gitignored)
venv/                 # Virtual environment (gitignored)
```

## Cookie Format

JSON file supports two formats:

- List: `[{"name": "SID", "value": "..."}, ...]`
- Dict: `{"SID": "...", "HSID": "...", ...}`
