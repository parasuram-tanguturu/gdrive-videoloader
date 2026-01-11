# Product Context

## Problem Statement
Users need to download videos from Google Drive that are marked as "view-only" (no download button available). Manual methods are cumbersome and don't work for restricted videos.

## Solution
A Python script that:
- Uses Google Drive's internal API to access video playback URLs
- Supports authentication via cookies for protected videos
- Provides both interactive and command-line interfaces
- Automates cookie extraction to simplify authentication

## User Experience Goals
- Simple: Interactive mode guides users step-by-step
- Fast: Automatic cookie extraction eliminates manual steps
- Reliable: Handles errors gracefully with helpful messages
- Flexible: Works for both public and protected videos

## Key Use Cases
1. Download public Google Drive videos
2. Download view-only videos (requires authentication)
3. Resume interrupted downloads
4. Extract cookies for reuse
