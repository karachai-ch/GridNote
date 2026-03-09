<html>
  <h1 style="font-size: 100px; font-weight: bold;">Complete Setup</h1>
<body><em>A complete guide to set up for GridNote.</em></body><br></br>
</html>

## Requirements

- Raspberry Pi Zero 2W with Raspberry Pi OS Lite (32-bit)
- Python 3.9+
- Google Cloud project with Tasks API enabled

## Setup

### 1. Flash the SD card
Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/), select **Raspberry Pi OS Lite (32-bit)**, and flash your 16GB microSD. In the settings, enable SSH and enter your WiFi credentials.

### 2. Run the setup script
SSH into your Pi, clone this repo, then run:
```bash
bash firmware/setup.sh
```

### 3. Google API credentials
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project
3. Enable the **Google Tasks API**
4. Create an **OAuth 2.0 Client ID** (Desktop App)
5. Download `credentials.json` and place it in the `firmware/` folder

### 4. First run
```bash
python3 firmware/gridnote.py
```
A browser window will open for Google login. After authorizing, `token.json` is saved and the display will update automatically every 30 minutes.

### 5. Run on boot (optional)
```bash
sudo crontab -e
```
Add this line:
```
@reboot sleep 30 && python3 /home/pi/GridNote/firmware/gridnote.py &
```

## Files

| File | Purpose |
|------|---------|
| `gridnote.py` | Main script — fetches tasks and drives the display |
| `setup.sh` | One-time installation script |
| `credentials.json` | Your Google OAuth credentials *(add this yourself, do not commit)* |
| `token.json` | Auto-generated after first login *(do not commit)* |
| `fonts/` | DejaVu fonts used for rendering |
