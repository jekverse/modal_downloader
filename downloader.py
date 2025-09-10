# downloader.py
import os, time, requests
import gradio as gr
import globals
from utils import format_bytes
from jobs import jobs_to_table

def update_filename_from_url(url):
    from utils import extract_filename_from_url
    return extract_filename_from_url(url)

def download_single(job, progress=gr.Progress()):
    url, filename, directory = job["url"], job["filename"], job["directory"]
    full_path = os.path.join(directory, filename)
    os.makedirs(directory, exist_ok=True)
    try:
        progress(0, desc=f"🔗 Connecting {filename}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        chunk_size = 1024 * 1024
        downloaded = 0
        start_time = time.time()
        with open(full_path, "wb") as f:
            for chunk in response.iter_content(chunk_size):
                if globals.stop_all:
                    return "❌ Cancelled"
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = downloaded / total_size
                        elapsed = time.time() - start_time
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        eta = (total_size - downloaded) / speed if speed > 0 else 0
                        eta_str = f"{int(eta//60)}m {int(eta%60)}s" if eta > 60 else f"{int(eta)}s"
                        progress(pct, desc=f"📥 {format_bytes(speed)}/s | ETA: {eta_str}")
        return f"✅ Done: {filename} ({format_bytes(total_size)})"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def start_download_queue(progress=gr.Progress()):
    if not globals.download_jobs:
        yield gr.update(value=jobs_to_table()), "⚠️ Job list kosong"
        return
    globals.stop_all = False
    for job in globals.download_jobs:
        if globals.stop_all:
            job["status"] = "❌ Cancelled"
            yield gr.update(value=jobs_to_table()), "⏹️ Dibatalkan"
            break
        job["status"] = "Downloading..."
        yield gr.update(value=jobs_to_table()), f"⏳ Mulai: {job['filename']}"
        result = download_single(job, progress)
        job["status"] = result
        yield gr.update(value=jobs_to_table()), result
    yield gr.update(value=jobs_to_table()), "🏁 Selesai memproses semua job"

def cancel_all():
    globals.stop_all = True
    return "⏹️ Semua job dibatalkan"
