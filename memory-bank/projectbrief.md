# Project Brief

## Purpose

Python script to download videos from Google Drive, including view-only videos that don't have a download button.

## Core Requirements

- Download videos from Google Drive using video ID or URL
- Support view-only videos (bypass download restrictions)
- Handle authentication via cookies for protected videos
- Interactive mode for easy use
- Automatic cookie extraction via browser automation
- Resumable downloads
- Progress bar display

## Key Constraints

- Must work with Google Drive's internal API (`get_video_info`)
- Requires cookies for authenticated videos
- Needs Chrome browser for automatic cookie extraction (optional)

## Success Criteria

- Successfully downloads public videos
- Successfully downloads view-only videos with authentication
- Provides clear error messages and guidance
- Easy to use for non-technical users
