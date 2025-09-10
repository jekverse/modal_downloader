# utils.py
import os
from urllib.parse import urlparse, unquote
from pathlib import Path

def extract_filename_from_url(url):
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        path = unquote(parsed.path)
        filename = os.path.basename(path)
        return filename if filename else "downloaded_file"
    except:
        return "downloaded_file"

def format_bytes(bytes_val):
    if bytes_val == 0:
        return "0 B"
    for unit in ['B','KB','MB','GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"

def get_folder_contents(current_dir="/root"):
    if not os.path.exists(current_dir):
        current_dir = "/root"
    items = [".. (Parent Directory)"] if current_dir != "/" else []
    try:
        for item in sorted(Path(current_dir).iterdir()):
            if not item.name.startswith("."):
                items.append(item.name)
    except PermissionError:
        pass
    return items, current_dir
