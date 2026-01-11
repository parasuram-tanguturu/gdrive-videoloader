# System Patterns

## Architecture

Single-file Python script with modular functions. Two modes: interactive (prompt-based) and CLI (argument-based).

## Key Components

### Entry Point

- `if __name__ == "__main__"`: Parses arguments, routes to interactive or CLI mode
- `--get-cookies` flag: Standalone cookie extraction

### Core Functions

- `extract_video_id()`: Parses URLs to extract video ID
- `get_cookies_automatically()`: Browser automation for cookie extraction
- `interactive_mode()`: Step-by-step user prompts
- `main()`: Core download logic
- `get_video_url()`: Extracts playback URL from API response
- `download_file()`: Streams download with progress bar

## Design Patterns

### Flow Control

1. Check for `--get-cookies` → standalone cookie extraction
2. Check for `video_id` argument → CLI mode
3. No arguments → interactive mode

### Authentication Flow

- Interactive: Ask if auth needed → automatic or manual cookie extraction
- CLI: Use `--cookie-file` if provided

### Error Handling

- HTTP status codes: 403 (access denied), 404 (not found)
- Network errors: timeout, connection issues
- Clear error messages with troubleshooting tips

## API Usage

- Endpoint: `https://drive.google.com/u/0/get_video_info?docid={video_id}&drive_originator_app=303`
- Extracts `videoplayback` URL from response
- Uses cookies for authenticated requests
