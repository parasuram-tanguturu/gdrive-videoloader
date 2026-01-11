# GDrive VideoLoader

**GDrive VideoLoader** is a Python-based tool to download videos from Google Drive effortlessly, **including those marked as _view-only_** (no download option). It supports resumable downloads, progress bars, and various customization options for video fetching and downloading.

## Features

- Download videos even if marked as *view-only* (without a download button)
- **Interactive mode** - Simple step-by-step prompts for easy use
- **Automatic cookie extraction** - Opens browser to get cookies automatically
- Supports resumable downloads (continue from where it stopped)
- Displays a progress bar for ongoing downloads
- Allows custom chunk sizes for downloading
- Optionally specify a custom output file name
- Verbose mode for detailed logs during execution
- Handles authentication for protected videos

## Installation

### Prerequisites

- Python 3.7+
- Pip (Python package manager)
- Google Chrome browser (for automatic cookie extraction - optional)

### Dependencies

Install the required Python packages using the following command:

```bash
pip install -r requirements.txt
```

**Note:** For automatic cookie extraction, you also need:
- Google Chrome browser installed
- ChromeDriver (usually auto-detected, or install manually if needed)

## Usage

### Interactive Mode (Easiest - Recommended)

Run the script without arguments for an interactive experience:

```bash
python gdrive_videoloader.py
```

The script will prompt you for:
1. Google Drive video URL (or Video ID)
2. Whether authentication is needed
3. Cookie file path (or automatic extraction)

### Command-Line Mode

#### Basic Command

To download a video by its Google Drive ID:

```bash
python gdrive_videoloader.py <video_id>
```

#### For View-Only or Protected Videos

View-only videos require authentication. Get cookies first:

```bash
# Step 1: Extract cookies automatically
python gdrive_videoloader.py --get-cookies

# Step 2: Download with cookies
python gdrive_videoloader.py <video_id> --cookie-file cookies.json
```

### Options

| Parameter                | Description                                                       | Default Value         |
|--------------------------|-------------------------------------------------------------------|-----------------------|
| `<video_id>`             | The video ID from Google Drive (optional - if omitted, interactive mode starts). | N/A                   |
| `-o`, `--output`         | Custom output file name for the downloaded video.                | Video name in GDrive  |
| `-c`, `--chunk_size`     | Chunk size (in bytes) for downloading the video.                 | 1024 bytes            |
| `-v`, `--verbose`        | Enable verbose mode for detailed logs.                           | Disabled              |
| `--cookie-file`          | Path to JSON file containing cookies for authentication.       | N/A                   |
| `--get-cookies`          | Automatically extract cookies by opening browser. Optionally specify output file. | cookies.json |
| `--version`              | Display the script version.                                      | N/A                   |
| `-h`, `--help`           | Display the help message.                                        | N/A                   |

### Examples

#### Download Public Video
```bash
python gdrive_videoloader.py abc-Qt12kjmS21kjDm2kjd
```

#### Download View-Only Video (with authentication)
```bash
# Interactive mode (easiest)
python gdrive_videoloader.py
# Follow prompts to extract cookies and download

# Or command-line mode
python gdrive_videoloader.py VIDEO_ID --cookie-file cookies.json
```

#### Extract Cookies Only
```bash
python gdrive_videoloader.py --get-cookies
# Or specify output file
python gdrive_videoloader.py --get-cookies my_cookies.json
```

#### Custom Output Filename
```bash
python gdrive_videoloader.py VIDEO_ID --output my_video.mp4
```

#### Verbose Mode
```bash
python gdrive_videoloader.py VIDEO_ID --verbose
```

## Troubleshooting

### View-Only Videos

For videos marked as "view-only" (no download button):

1. **Use interactive mode** - It will guide you through authentication:
   ```bash
   python gdrive_videoloader.py
   ```

2. **Or extract cookies manually**:
   ```bash
   python gdrive_videoloader.py --get-cookies
   python gdrive_videoloader.py VIDEO_ID --cookie-file cookies.json
   ```

### Common Issues

**"Access denied (403)" error:**
- Video requires authentication - provide cookies using `--cookie-file`
- Your account doesn't have access to the video
- Cookies may have expired - extract new cookies

**"Unable to retrieve the video URL" error:**
- Video ID is incorrect
- Video requires authentication (view-only videos need cookies)
- Your account doesn't have access to the video

**"Selenium is not installed" error:**
- Install selenium: `pip install selenium`
- Make sure Chrome browser is installed

**"Chrome browser not found" error:**
- Install Google Chrome browser
- Or install ChromeDriver manually

**Download interrupted:**
- Just run the same command again - the script automatically resumes from where it stopped

## TODO

### Features
- Add support for downloading subtitles.
- Add support for multiple downloads (list or file of video IDs).
- Allow selection of video quality.
- Implement temporary file naming during download.

### UX
- Safely handle interruptions (KeyboardInterrupt).
- Display custom error messages based on request responses.

### Performance
- Implement parallel downloads to speed up the process.

### Organization
- Modularize the project into separate files (`downloader.py`, `cli.py`, `utils.py`).
- Add logging support using the `logging` module.
- Validate output file names for compatibility with the operating system.

### Code Quality
- Create automated tests for core functions.
- Add detailed documentation using `pdoc` or `Sphinx`.

## Contributing
Contributions are always welcome! If you have suggestions for improving the script or adding new features, feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
