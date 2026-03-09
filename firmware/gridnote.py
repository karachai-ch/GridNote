"""
GridNote Firmware
-----------------
Fetches tasks from Google Tasks API and renders them
on a Waveshare 7.5" tri-color e-ink display.

Hardware: Raspberry Pi Zero 2W + Waveshare 7.5inch e-Paper HAT
Author: karachai-ch
"""

import os
import time
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd7in5b_V2
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')
REFRESH_INTERVAL_MINUTES = 30
MAX_TASKS = 10

WIDTH = 800
HEIGHT = 480

FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')
def load_font(size, bold=False):
    try:
        name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds


def fetch_tasks():
    """Returns a list of dicts with 'title' and 'due' for incomplete tasks."""
    creds = get_credentials()
    service = build('tasks', 'v1', credentials=creds)

    tasklists = service.tasklists().list(maxResults=1).execute()
    if not tasklists.get('items'):
        return []
    tasklist_id = tasklists['items'][0]['id']

    result = service.tasks().list(
        tasklist=tasklist_id,
        showCompleted=False,
        maxResults=MAX_TASKS
    ).execute()

    tasks = []
    for item in result.get('items', []):
        if item.get('status') == 'needsAction':
            tasks.append({
                'title': item.get('title', '(no title)'),
                'due': item.get('due', None)
            })
    return tasks



def render_image(tasks):
    """
    Returns (black_image, red_image) as PIL Image objects.
    Waveshare (B) takes two layers: black/white and red/white.
    """
    black = Image.new('1', (WIDTH, HEIGHT), 255)  
    red   = Image.new('1', (WIDTH, HEIGHT), 255)
    draw_b = ImageDraw.Draw(black)
    draw_r = ImageDraw.Draw(red)

    font_title  = load_font(22, bold=True)
    font_task   = load_font(18)
    font_small  = load_font(14)

    draw_r.rectangle([0, 0, WIDTH, 52], fill=0)
    draw_r.text((20, 12), "GridNote", font=load_font(26, bold=True), fill=255)
    now_str = datetime.now().strftime("%a %b %-d  •  %-I:%M %p")
    draw_r.text((WIDTH - 260, 18), now_str, font=font_small, fill=255)

    count_text = f"{len(tasks)} task{'s' if len(tasks) != 1 else ''} remaining"
    draw_b.text((20, 62), count_text, font=font_small, fill=0)

    draw_b.line([20, 82, WIDTH - 20, 82], fill=0, width=1)

    y = 96
    row_height = 38
    for i, task in enumerate(tasks):
    
        if i % 2 == 0:
            draw_b.rectangle([16, y - 2, WIDTH - 16, y + row_height - 4], fill=0)
            text_color_b = 255
            text_color_r = 255
        else:
            text_color_b = 0
            text_color_r = 0

        cx, cy = 38, y + 14
        draw_b.ellipse([cx - 10, cy - 10, cx + 10, cy + 10],
                       outline=(255 if i % 2 == 0 else 0), width=2)

        title = task['title']
        if len(title) > 52:
            title = title[:49] + '…'

        if i % 2 == 0:
            draw_b.text((58, y + 6), title, font=font_task, fill=text_color_b)
        else:
            draw_b.text((58, y + 6), title, font=font_task, fill=text_color_b)

        if task['due']:
            try:
                due_dt = datetime.fromisoformat(task['due'].replace('Z', ''))
                due_str = due_dt.strftime("Due %-m/%-d")
                draw_r.text((WIDTH - 110, y + 6), due_str, font=font_small,
                            fill=(255 if i % 2 == 0 else 0))
            except Exception:
                pass

        y += row_height
        if y + row_height > HEIGHT - 30:
            break

    if not tasks:
        draw_b.text((WIDTH // 2, HEIGHT // 2), "All done! ✓",
                    font=load_font(32, bold=True), fill=0, anchor='mm')

    draw_b.line([20, HEIGHT - 24, WIDTH - 20, HEIGHT - 24], fill=0, width=1)
    draw_b.text((20, HEIGHT - 20), "GridNote • github.com/karachai-ch/GridNote",
                font=font_small, fill=0)

    return black, red

def update_display(tasks):
    epd = epd7in5b_V2.EPD()
    print("Initializing display...")
    epd.init()
    epd.Clear()

    black_img, red_img = render_image(tasks)

    print("Sending image to display...")
    epd.display(epd.getbuffer(black_img), epd.getbuffer(red_img))

    print("Putting display to sleep...")
    epd.sleep()

def main():
    print("GridNote starting up...")
    while True:
        try:
            print("Fetching tasks from Google...")
            tasks = fetch_tasks()
            print(f"Got {len(tasks)} tasks. Updating display...")
            update_display(tasks)
            print(f"Done. Sleeping {REFRESH_INTERVAL_MINUTES} minutes.")
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(REFRESH_INTERVAL_MINUTES * 60)


if __name__ == '__main__':
    main()
