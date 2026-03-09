#!/bin/bash

set -e
echo "=== GridNote Setup ==="

echo "[1/5] Updating system..."
sudo apt update && sudo apt upgrade -y

echo "[2/5] Installing dependencies..."
sudo apt install python3-pip python3-pil git -y
pip3 install \
  google-auth \
  google-auth-oauthlib \
  google-api-python-client \
  --break-system-packages

echo "[3/5] Installing Waveshare e-ink library..."
cd ~
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
sudo pip3 install . --break-system-packages
cd ~

echo "[4/5] Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

echo "[5/5] Installing fonts..."
sudo apt install fonts-dejavu -y
mkdir -p ~/GridNote/firmware/fonts
cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf ~/GridNote/firmware/fonts/
cp /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf ~/GridNote/firmware/fonts/

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Copy your credentials.json from Google Cloud Console into firmware/"
echo "  2. Run: python3 firmware/gridnote.py"
echo "  3. Complete the Google OAuth login in your browser"
echo "  4. The display will update every 30 minutes automatically"
echo ""
echo "To run GridNote on boot:"
echo "  sudo crontab -e"
echo "  Add: @reboot sleep 30 && python3 /home/pi/GridNote/firmware/gridnote.py &"
