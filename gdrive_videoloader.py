from urllib.parse import unquote, urlparse, parse_qs
import requests
from requests.adapters import HTTPAdapter
try:
    from urllib3.util.retry import Retry
except ImportError:
    from requests.packages.urllib3.util.retry import Retry
import argparse
import sys
from tqdm import tqdm
import os
import json
import re
import time

def extract_video_id(url: str) -> str:
    """Extract video ID from Google Drive URL or return as-is if already an ID."""
    # If it's already just an ID (no slashes or dots), return it
    if '/' not in url and '.' not in url:
        return url
    
    # Pattern for /file/d/VIDEO_ID/view or /file/d/VIDEO_ID/
    match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    
    # Pattern for ?id=VIDEO_ID
    parsed = urlparse(url)
    if 'id' in parse_qs(parsed.query):
        return parse_qs(parsed.query)['id'][0]
    
    # If no pattern matches, return the input (might be malformed, but let main() handle it)
    return url

def get_cookies_automatically(output_file: str = "cookies.json") -> str:
    """Automatically get cookies by opening a browser and waiting for user to log in."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("\n[ERROR] Selenium is not installed.")
        print("Please install it using: pip install selenium")
        print("Also make sure you have Chrome browser installed.")
        return None
    
    print("\n" + "="*60)
    print("AUTOMATIC COOKIE EXTRACTION")
    print("="*60)
    print("\nA browser window will open. Please:")
    print("  1. Log in to your Google account if prompted")
    print("  2. Navigate to Google Drive")
    print("  3. Wait for the script to detect you're logged in")
    print("  4. The browser will close automatically\n")
    input("Press Enter to open browser...")
    
    driver = None
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Try to create driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"\n[ERROR] Could not start Chrome browser: {e}")
            print("Make sure Chrome is installed and chromedriver is available.")
            print("You can install chromedriver manually or use webdriver-manager:")
            print("  pip install webdriver-manager")
            return None
        
        # Navigate to Google Drive
        print("\nOpening Google Drive...")
        driver.get("https://drive.google.com")
        
        # Wait for user to log in (check for drive.google.com domain and some indicator of being logged in)
        print("\nWaiting for you to log in...")
        print("(The script will continue once it detects you're logged in)")
        
        # Wait up to 5 minutes for login
        max_wait = 300  # 5 minutes
        start_time = time.time()
        logged_in = False
        
        while time.time() - start_time < max_wait:
            try:
                # Check if we're on drive.google.com and page has loaded
                current_url = driver.current_url
                if "drive.google.com" in current_url:
                    # Check for elements that indicate logged in state
                    page_source = driver.page_source.lower()
                    # Look for indicators of being logged in
                    if any(indicator in page_source for indicator in ["my drive", "new", "upload", "shared with me"]):
                        # Give a few seconds for cookies to be set
                        time.sleep(3)
                        logged_in = True
                        break
            except Exception:
                pass
            time.sleep(2)
        
        if not logged_in:
            print("\n[WARNING] Login detection timeout. Extracting cookies anyway...")
        
        # Extract cookies
        print("\nExtracting cookies...")
        cookies = driver.get_cookies()
        
        # Filter cookies for google.com and drive.google.com domains
        relevant_cookies = []
        for cookie in cookies:
            domain = cookie.get('domain', '')
            if 'google.com' in domain or 'drive.google.com' in domain:
                relevant_cookies.append({
                    'name': cookie['name'],
                    'value': cookie['value']
                })
        
        if not relevant_cookies:
            print("[WARNING] No relevant cookies found. You may need to log in again.")
            driver.quit()
            return None
        
        # Save cookies to file
        with open(output_file, 'w') as f:
            json.dump(relevant_cookies, f, indent=2)
        
        print(f"\n[SUCCESS] Cookies saved to: {output_file}")
        print(f"Found {len(relevant_cookies)} cookies.")
        
        return output_file
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

# Cookie information dictionary with comprehensive explanations
COOKIE_INFO = {
    "SID": {
        "name": "SID",
        "what": "Primary session identifier for your Google account",
        "why": "Google uses this to verify you're logged in and authorized",
        "how": "DevTools → Application → Cookies → google.com → Copy 'Value' of SID",
        "when": "Sent with every API request to authenticate your session"
    },
    "HSID": {
        "name": "HSID",
        "what": "Hashed version of session ID for additional security",
        "why": "Provides extra security layer for session validation",
        "how": "Same location as SID, look for 'HSID' cookie",
        "when": "Used alongside SID for secure authentication"
    },
    "SSID": {
        "name": "SSID",
        "what": "Secure session identifier for HTTPS connections",
        "why": "Ensures secure communication with Google servers",
        "how": "Found in same cookies list, look for 'SSID'",
        "when": "Used for secure API calls over HTTPS"
    },
    "APISID": {
        "name": "APISID",
        "what": "Session ID specifically for Google API requests",
        "why": "Required for accessing Google Drive API endpoints",
        "how": "Look for 'APISID' in google.com cookies",
        "when": "Used when calling get_video_info API"
    },
    "SAPISID": {
        "name": "SAPISID",
        "what": "Secure version of APISID for API authentication",
        "why": "Provides secure authentication for API calls",
        "how": "Found alongside APISID, look for 'SAPISID'",
        "when": "Used for secure API authentication"
    },
    "__Secure-1PSID": {
        "name": "__Secure-1PSID",
        "what": "Secure first-party session ID",
        "why": "Modern security cookie for enhanced protection",
        "how": "Look for cookies starting with '__Secure-' prefix",
        "when": "Used for enhanced security in modern browsers"
    },
    "__Secure-3PSID": {
        "name": "__Secure-3PSID",
        "what": "Secure third-party session ID",
        "why": "Modern security cookie for cross-site protection",
        "how": "Look for cookies starting with '__Secure-' prefix",
        "when": "Used for enhanced security in modern browsers"
    }
}

def show_cookie_extraction_guidelines() -> None:
    """Display step-by-step instructions for finding cookies in browser DevTools."""
    print("\n" + "="*60)
    print("HOW TO FIND COOKIES IN YOUR BROWSER")
    print("="*60)
    print("\nStep-by-step guide:\n")
    print("1. Open Google Drive in your browser (drive.google.com)")
    print("2. Make sure you're logged in to your Google account")
    print("3. Open Developer Tools:")
    print("   - Chrome/Edge: Press F12 or Right-click → Inspect")
    print("   - Firefox: Press F12 or Right-click → Inspect Element")
    print("4. Navigate to Cookies:")
    print("   - Chrome/Edge: Click 'Application' tab → Left sidebar → 'Cookies' → 'https://www.google.com'")
    print("   - Firefox: Click 'Storage' tab → Left sidebar → 'Cookies' → 'https://www.google.com'")
    print("5. Look for the cookies listed below")
    print("6. Copy the 'Value' column for each cookie")
    print("\nYou'll need cookies from:")
    print("  - google.com (most important)")
    print("  - drive.google.com (if available)")
    print("\n" + "="*60 + "\n")

def prompt_cookie_value(cookie_info: dict, required: bool = False) -> str:
    """Prompt for individual cookie value with comprehensive explanation."""
    name = cookie_info["name"]
    what = cookie_info["what"]
    why = cookie_info["why"]
    how = cookie_info["how"]
    when = cookie_info["when"]
    
    status = "REQUIRED" if required else "OPTIONAL"
    
    # Create display name
    display_name = name.replace("__Secure-", "Secure ").replace("SID", "Session ID")
    
    print("\n" + "="*60)
    print(f"{name} ({display_name}) - {status}")
    print("="*60)
    print(f"WHAT: {what}")
    print(f"WHY:  {why}")
    print(f"HOW:  {how}")
    print(f"WHEN: {when}")
    print("="*60)
    
    if required:
        while True:
            value = input(f"\nEnter {name} value: ").strip()
            if value:
                return value
            print(f"{name} is required. Please enter a value.\n")
    else:
        value = input(f"\nEnter {name} value (press Enter to skip): ").strip()
        return value if value else None

def manual_cookie_entry(output_file: str = "cookies.json") -> str:
    """Guide user through manual cookie entry step-by-step with detailed explanations."""
    print("\n" + "="*60)
    print("MANUAL COOKIE ENTRY")
    print("="*60)
    print("\nYou'll be prompted for each cookie individually.")
    print("Each prompt will explain what the cookie is, why it's needed,")
    print("how to find it, and when it's used.\n")
    
    # Show initial guidelines
    show_cookie_extraction_guidelines()
    
    input("Press Enter when you have DevTools open and are ready to enter cookies...")
    
    cookies = {}
    
    # Required cookies
    print("\n" + "="*60)
    print("REQUIRED COOKIES")
    print("="*60)
    
    sid_value = prompt_cookie_value(COOKIE_INFO["SID"], required=True)
    cookies["SID"] = sid_value
    
    hsid_value = prompt_cookie_value(COOKIE_INFO["HSID"], required=True)
    cookies["HSID"] = hsid_value
    
    # Optional but recommended cookies
    print("\n" + "="*60)
    print("OPTIONAL COOKIES (Recommended)")
    print("="*60)
    print("These cookies improve authentication reliability but can be skipped.\n")
    
    optional_cookies = ["SSID", "APISID", "SAPISID"]
    for cookie_name in optional_cookies:
        if cookie_name in COOKIE_INFO:
            value = prompt_cookie_value(COOKIE_INFO[cookie_name], required=False)
            if value:
                cookies[cookie_name] = value
    
    # Ask for secure cookies
    print("\n" + "="*60)
    print("ADDITIONAL SECURE COOKIES (Optional)")
    print("="*60)
    print("Modern browsers use these secure cookies. Add them if available.\n")
    
    secure_cookies = ["__Secure-1PSID", "__Secure-3PSID"]
    for cookie_name in secure_cookies:
        if cookie_name in COOKIE_INFO:
            value = prompt_cookie_value(COOKIE_INFO[cookie_name], required=False)
            if value:
                cookies[cookie_name] = value
    
    # Option to add custom cookies
    while True:
        add_more = input("\nAdd more custom cookies? (y/n): ").strip().lower()
        if add_more in ['y', 'yes']:
            cookie_name = input("Enter cookie name (or press Enter to finish): ").strip()
            if not cookie_name:
                break
            cookie_value = input(f"Enter {cookie_name} value: ").strip()
            if cookie_value:
                cookies[cookie_name] = cookie_value
        elif add_more in ['n', 'no']:
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")
    
    # Validate required cookies
    if not cookies.get("SID") or not cookies.get("HSID"):
        print("\n[ERROR] Required cookies (SID and HSID) must be provided.")
        return None
    
    # Convert to list format for JSON
    cookie_list = [{"name": name, "value": value} for name, value in cookies.items()]
    
    # Save cookies to file
    try:
        with open(output_file, 'w') as f:
            json.dump(cookie_list, f, indent=2)
        print(f"\n[SUCCESS] Cookies saved to: {output_file}")
        print(f"Saved {len(cookie_list)} cookies.")
        return output_file
    except Exception as e:
        print(f"\n[ERROR] Failed to save cookies: {e}")
        return None

def show_cookie_instructions() -> None:
    """Display instructions on how to get cookies for authentication."""
    print("\n" + "="*60)
    print("COOKIE INSTRUCTIONS")
    print("="*60)
    print("\nWhy cookies are needed:")
    print("  Some Google Drive videos require login to view/download.")
    print("  Cookies authenticate your browser session with Google.\n")
    print("How to get cookies:")
    print("  1. Automatic (Recommended):")
    print("     - The script can open a browser and extract cookies automatically")
    print("     - Just log in when prompted\n")
    print("  2. Manual Entry:")
    print("     - Use the interactive manual entry mode")
    print("     - Follow step-by-step prompts with detailed explanations")
    print("     - Copy cookies from browser DevTools\n")
    print("  3. Manual File Method:")
    print("     - Install a browser extension:")
    print("       * Chrome/Edge: 'Get cookies.txt LOCALLY' or 'Cookie-Editor'")
    print("       * Firefox: 'Cookie-Editor'")
    print("     - Log in to Google Drive in your browser")
    print("     - Open the extension and export cookies for:")
    print("       * google.com")
    print("       * drive.google.com")
    print("     - Save as JSON format\n")
    print("Cookie file format (JSON):")
    print('  [{"name": "SID", "value": "your-value"}, ...]')
    print('  OR')
    print('  {"SID": "your-value", "HSID": "your-value", ...}')
    print("\n" + "="*60 + "\n")

def interactive_mode() -> None:
    """Interactive mode that prompts user for video URL and authentication."""
    print("\n" + "="*60)
    print("Google Drive Video Downloader - Interactive Mode")
    print("="*60 + "\n")
    
    # Step 1: Get video URL
    while True:
        video_input = input("Enter Google Drive Video URL (or Video ID): ").strip()
        if video_input:
            video_id = extract_video_id(video_input)
            break
        print("Please enter a valid URL or Video ID.\n")
    
    # Step 2: Ask about authentication
    while True:
        need_auth = input("Do you need authentication? (y/n): ").strip().lower()
        if need_auth in ['y', 'yes', 'n', 'no']:
            break
        print("Please enter 'y' for yes or 'n' for no.\n")
    
    cookie_file = None
    if need_auth in ['y', 'yes']:
        # Step 3: Ask cookie method (auto or manual)
        while True:
            cookie_method = input("Cookie method: (a)uto or (m)anual? ").strip().lower()
            if cookie_method in ['a', 'auto', 'm', 'manual']:
                break
            print("Please enter 'a' for auto or 'm' for manual.\n")
        
        default_cookie_file = "cookies.json"
        
        if cookie_method in ['a', 'auto']:
            # Automatic cookie extraction
            cookie_file_path = input(f"Cookie file path (default: {default_cookie_file}): ").strip()
            if not cookie_file_path:
                cookie_file_path = default_cookie_file
            
            cookie_file = get_cookies_automatically(cookie_file_path)
            if not cookie_file:
                print("\nAutomatic cookie extraction failed.")
                retry_manual = input("Try manual entry? (y/n): ").strip().lower()
                if retry_manual in ['y', 'yes']:
                    cookie_file = manual_cookie_entry(default_cookie_file)
                else:
                    print("Continuing without cookies. Download may fail if authentication is required.\n")
        else:
            # Manual cookie entry
            cookie_file_path = input(f"Cookie file path (default: {default_cookie_file}): ").strip()
            if not cookie_file_path:
                cookie_file_path = default_cookie_file
            
            cookie_file = manual_cookie_entry(cookie_file_path)
            
            # If manual entry failed or cancelled, offer file input as fallback
            if not cookie_file:
                print("\nManual cookie entry cancelled or failed.")
                use_file = input("Do you have a cookie file to use instead? (y/n): ").strip().lower()
                if use_file in ['y', 'yes']:
                    show_cookie_instructions()
                    while True:
                        cookie_path = input("Enter cookie file path: ").strip()
                        if not cookie_path:
                            print("Cookie file path cannot be empty. Please enter a valid path.\n")
                            continue
                        
                        if os.path.exists(cookie_path):
                            cookie_file = cookie_path
                            break
                        else:
                            retry = input(f"File '{cookie_path}' not found. Show instructions again? (y/n): ").strip().lower()
                            if retry in ['y', 'yes']:
                                show_cookie_instructions()
                            else:
                                print("Continuing without cookies. Download may fail if authentication is required.\n")
                                break
                else:
                    print("Continuing without cookies. Download may fail if authentication is required.\n")
    
    # Start download
    print("\nStarting download...\n")
    main(video_id, None, 65536, False, cookie_file)

def load_cookies(cookie_file: str) -> dict:
    """Load cookies from a JSON file and convert to a dictionary."""
    try:
        with open(cookie_file, 'r') as f:
            data = json.load(f)

        # If the data is a list, convert to a dictionary
        if isinstance(data, list):
            cookies = {item['name']: item['value'] for item in data if 'name' in item and 'value' in item}
        else:
            cookies = data  # Assume it's already a dictionary
        return cookies
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return {}

def get_video_url(page_content: str, verbose: bool) -> tuple[str, str]:
    """Extracts the video playback URL and title from the page content."""
    if verbose:
        print("[INFO] Parsing video playback URL and title.")
    contentList = page_content.split("&")
    video, title = None, None
    for content in contentList:
        if content.startswith('title=') and not title:
            title = unquote(content.split('=')[-1])
        elif "videoplayback" in content and not video:
            video = unquote(content).split("|")[-1]
        if video and title:
            break

    if verbose:
        print(f"[INFO] Video URL: {video}")
        print(f"[INFO] Video Title: {title}")
    return video, title

def get_optimal_chunk_size(file_size: int, user_chunk_size: int = None) -> int:
    """Determine optimal chunk size based on file size."""
    if user_chunk_size:
        return user_chunk_size
    if file_size < 10 * 1024 * 1024:  # < 10MB
        return 16 * 1024  # 16KB
    elif file_size < 100 * 1024 * 1024:  # < 100MB
        return 64 * 1024  # 64KB
    elif file_size < 500 * 1024 * 1024:  # < 500MB
        return 256 * 1024  # 256KB
    else:  # >= 500MB
        return 1024 * 1024  # 1MB

def download_file(url: str, cookies: dict, filename: str, chunk_size: int, verbose: bool) -> None:
    """Downloads the file from the given URL with provided cookies, supports resuming."""
    # Validate filename
    if not filename:
        print("\n[ERROR] Filename is required for download.")
        return
    
    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    file_mode = 'wb'

    downloaded_size = 0
    if os.path.exists(filename):
        downloaded_size = os.path.getsize(filename)
        headers['Range'] = f"bytes={downloaded_size}-"
        file_mode = 'ab'

    if verbose:
        print(f"[INFO] Starting download from {url}")
        if downloaded_size > 0:
            print(f"[INFO] Resuming download from byte {downloaded_size}")

    # Create session with retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = session.get(url, stream=True, cookies=cookies, headers=headers, timeout=60)
            
            if response.status_code in (200, 206):  # 200 for new downloads, 206 for partial content
                total_size = int(response.headers.get('content-length', 0)) + downloaded_size
                
                # Use adaptive chunk sizing by default
                # If chunk_size is the default (65536), use adaptive; otherwise use user's custom size
                DEFAULT_CHUNK_SIZE = 65536
                if chunk_size == DEFAULT_CHUNK_SIZE:
                    # Use adaptive sizing
                    optimal_chunk_size = get_optimal_chunk_size(total_size)
                    if verbose:
                        print(f"[INFO] Using adaptive chunk size: {optimal_chunk_size // 1024}KB (file size: {total_size / (1024*1024):.1f}MB)")
                else:
                    # User specified custom chunk size, use it
                    optimal_chunk_size = chunk_size
                    if verbose:
                        print(f"[INFO] Using custom chunk size: {optimal_chunk_size // 1024}KB")
                
                with open(filename, file_mode) as file:
                    with tqdm(
                        total=total_size,
                        initial=downloaded_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=filename,
                        file=sys.stdout,
                        bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=optimal_chunk_size):
                            if chunk:
                                file.write(chunk)
                                pbar.update(len(chunk))
                
                print(f"\n{filename} downloaded successfully.")
                return  # Success, exit retry loop
                
            elif response.status_code == 403:
                print(f"\n[ERROR] Access denied (403) while downloading {filename}.")
                print("  - Video may require authentication")
                print("  - Cookies may have expired")
                print("  - Your account may not have download permission")
                return
            elif response.status_code == 404:
                print(f"\n[ERROR] Video not found (404). The download URL may have expired.")
                return
            else:
                print(f"\n[ERROR] Failed to download {filename}, status code: {response.status_code}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    print(f"Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    return
                    
        except requests.exceptions.Timeout:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                print(f"\n[WARNING] Download timeout. Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"\n[ERROR] Download timeout after {max_retries} attempts.")
                print("  - Check your internet connection")
                print("  - Try again later")
                return
        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                print(f"\n[WARNING] Network error: {e}")
                print(f"Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"\n[ERROR] Network error after {max_retries} attempts: {e}")
                print("  - Check your internet connection")
                print("  - Verify the video URL is accessible")
                return
        finally:
            session.close()

def main(video_id: str, output_file: str = None, chunk_size: int = 65536, verbose: bool = False, cookie_file: str = None) -> None:
    """Main function to process video ID and download the video file."""
    drive_url = f'https://drive.google.com/u/0/get_video_info?docid={video_id}&drive_originator_app=303'

    # Load cookies from file if provided, else use empty dict
    cookies = load_cookies(cookie_file) if cookie_file else {}

    if verbose:
        print(f"[INFO] Accessing {drive_url}")
        if cookies:
            print(f"[INFO] Using provided cookies: {list(cookies.keys())}")

    response = requests.get(drive_url, cookies=cookies)
    
    # Check for authentication/access errors
    if response.status_code == 403:
        print("\n[ERROR] Access denied (403). Possible reasons:")
        print("  - Video requires authentication - provide cookies using --cookie-file")
        print("  - Your account doesn't have access to this video")
        print("  - Cookies may have expired - try extracting new cookies")
        if not cookie_file:
            print("\n  Tip: Use interactive mode or --get-cookies to extract cookies automatically")
        return
    
    if response.status_code != 200:
        print(f"\n[ERROR] Failed to access video info. Status code: {response.status_code}")
        print("  - Check if video ID is correct")
        print("  - Verify you have access to the video")
        if response.status_code == 404:
            print("  - Video may not exist or has been deleted")
        return
    
    page_content = response.text
    response_cookies = response.cookies.get_dict()
    # Merge response cookies with provided cookies (response cookies take precedence)
    cookies.update(response_cookies)

    video, title = get_video_url(page_content, verbose)

    # Ensure filename has an extension
    # Use output_file if provided, otherwise use title (if not None/empty)
    filename = output_file if output_file else (title if title and title.strip() else None)
    # Generate default filename if both output_file and title are None/empty/whitespace
    if not filename or (isinstance(filename, str) and not filename.strip()):
        filename = f"video_{video_id}.mp4"
        if verbose:
            print(f"[INFO] No title found, using default filename: {filename}")
    else:
        # Clean up filename (strip whitespace)
        filename = filename.strip()
        if not os.path.splitext(filename)[1]:
            filename += '.mp4'  # Default to .mp4 if no extension

    if video:
        if verbose:
            print(f"[INFO] Video found. Starting download...")
        download_file(video, cookies, filename, chunk_size, verbose)
    else:
        print("\n[ERROR] Unable to retrieve the video URL.")
        print("Possible reasons:")
        print("  - Video ID is incorrect")
        print("  - Video requires authentication (view-only videos need cookies)")
        print("  - Your account doesn't have access to this video")
        if not cookie_file:
            print("\n  Tip: For view-only videos, use:")
            print("    python gdrive_videoloader.py --get-cookies")
            print("    python gdrive_videoloader.py VIDEO_ID --cookie-file cookies.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to download videos from Google Drive.")
    parser.add_argument("video_id", type=str, nargs='?', help="The video ID from Google Drive (e.g., 'abc-Qt12kjmS21kjDm2kjd'). If not provided, interactive mode will start.")
    parser.add_argument("-o", "--output", type=str, help="Optional output file name for the downloaded video (default: video name in gdrive).")
    parser.add_argument("-c", "--chunk_size", type=int, default=65536, help="Optional chunk size (in bytes) for downloading the video. Default is 65536 bytes (64KB). Adaptive sizing is used for default value.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode.")
    parser.add_argument("--cookie-file", type=str, help="Path to JSON file containing cookies for authentication.")
    parser.add_argument("--get-cookies", type=str, nargs='?', const="cookies.json", help="Automatically get cookies by opening browser. Optionally specify output file (default: cookies.json).")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")

    args = parser.parse_args()
    
    # Handle --get-cookies flag (standalone cookie extraction)
    if args.get_cookies is not None:
        cookie_file = get_cookies_automatically(args.get_cookies)
        if cookie_file:
            print(f"\nCookies saved successfully to: {cookie_file}")
            print("You can now use this file with --cookie-file option.")
        sys.exit(0)
    
    # If no video_id provided, start interactive mode
    if args.video_id is None:
        interactive_mode()
    else:
        main(args.video_id, args.output, args.chunk_size, args.verbose, args.cookie_file)
