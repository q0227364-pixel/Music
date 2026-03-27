# YouTube Authentication & Download Issues

## Problem: YouTube Anti-Bot Protection

Your bot encountered YouTube's anti-bot protection which blocked downloads. Error message:
```
❌ This video may require authentication (YouTube anti-bot protection). 
Please provide a cookies.txt file exported from your browser and configure the downloader to use it.
```

## Solution

### Step 1: Export Your YouTube Cookies

#### Option A: Using Browser Extension (Recommended)
1. Install [Export Cookie Extension](https://chrome.google.com/webstore/detail/export-cookies/eaaccfabaab6b14b5b4b02c4e5d87d7b) for Chrome/Brave
2. Open YouTube.com in your browser
3. Click the extension icon → "Export as cookies.txt"  
4. Save the file as `cookies.txt`

#### Option B: Using Python Script
1. Create a file named `extract_cookies.py`:
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
import json

driver = webdriver.Chrome()  # or Firefox()
driver.get("https://www.youtube.com")

input("After you login, press ENTER to continue...")

# Save cookies
cookies = driver.get_cookies()
with open('cookies.json', 'w') as f:
    json.dump(cookies, f)

driver.quit()

# Convert to Netscape format (cookies.txt)
with open('cookies.json', 'r') as f:
    cookies = json.load(f)

with open('cookies.txt', 'w') as f:
    f.write("# Netscape HTTP Cookie File\n")
    for cookie in cookies:
        f.write(f".youtube.com\tTRUE\t/\tTRUE\t0\t{cookie['name']}\t{cookie['value']}\n")

print("✓ cookies.txt created successfully")
```
2. Run: `python extract_cookies.py`
3. Login to YouTube when the browser opens
4. Press ENTER in the console

#### Option C: Using Browser DevTools
1. Open YouTube in Firefox
2. Press F12 → Storage → Cookies → youtube.com
3. Export using [Cookie Export Extension](https://addons.mozilla.org/firefox/addon/export-cookies/)

### Step 2: Place cookies.txt in Your Project

```bash
# Linux/Mac
cp cookies.txt /path/to/Music-main/

# Windows
copy cookies.txt C:\path\to\Music-main\
```

### Step 3: Configure yt-dlp to Use Cookies

The bot now supports automatic cookies.txt detection. Ensure the file exists in the project root:
```
Music-main/
├── cookies.txt  ← Place your cookies file here
├── config.py
├── Music/
└── ...
```

### Step 4: Verify Configuration

Check your environment or config.py:
- ✅ `EXTERNAL_SERVICES_MAX_ATTEMPT=5` or higher (default now 5)
- ✅ `cookies.txt` exists in project root
- ✅ No conflicts with VPN/Proxy

### Step 5: Restart Bot

```bash
# Local
python -m Music

# Docker/Production
docker-compose restart
# or
systemctl restart music-bot
```

## Additional Configuration

### Increase Service Fallback Attempts
To use all 13 external services (maximum safety):
```bash
export EXTERNAL_SERVICES_MAX_ATTEMPT=13
```

Or add to `.env`:
```
EXTERNAL_SERVICES_MAX_ATTEMPT=13
```

### Available External Services
The bot now tries up to 5 services by default:
1. **cobalt-audio** - Primary service
2. **mdown-youtube** - Secondary backup
3. **downloader-io** - Tertiary backup
4. **y2download-api** - Additional backup
5. **tuneto-mp3** - Additional backup
+ 8 more services available (set limit to 13 for all)

## Troubleshooting

### Issue: "Service limit reached (1/13 tried)"
**Solution:** Increase `EXTERNAL_SERVICES_MAX_ATTEMPT` in config.py or `.env`
```bash
EXTERNAL_SERVICES_MAX_ATTEMPT=8  # Default was 1, now 5
```

### Issue: "This video may require authentication"
**Solution:** 
1. Verify `cookies.txt` exists in project root
2. Ensure cookies are not expired (re-export if older than 2 weeks)
3. Make sure you're logged into YouTube

### Issue: Still failing after cookies.txt?
**Solution:** Try these steps:
1. Check YouTube login status in browser
2. Disable VPN/Proxy temporarily
3. Try with `EXTERNAL_SERVICES_MAX_ATTEMPT=13` (all services)
4. Check bot logs for specific service errors

### Issue: "Socket.send() raised exception"
This is a network/connection issue:
1. Check internet connection
2. Check if firewall is blocking connections
3. Try disabling VPN
4. Increase timeout values if needed

## Permanent Fix (Production)

For Docker/Production deployments, add to `docker-compose.yml` or `.env`:
```yaml
environment:
  - EXTERNAL_SERVICES_MAX_ATTEMPT=8
  # If using cookies
  - COOKIES_PATH=/app/cookies.txt
```

## Notes

- **Cookies expire**: Re-export cookies.txt every 2-3 weeks
- **Privacy**: Cookies.txt contains your YouTube session data - keep it private
- **Multiple accounts**: You can use different cookies.txt for different bot instances
- **Security**: Never commit cookies.txt to git (added to .gitignore by default)

## References

- [yt-dlp Cookies Guide](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- [Export Cookies Extension Chrome](https://chrome.google.com/webstore/detail/export-cookies/)
- [Export Cookies Add-on Firefox](https://addons.mozilla.org/firefox/addon/export-cookies/)

---

**Last Updated:** March 27, 2026  
**Status:** Recommended for all YouTube downloads
