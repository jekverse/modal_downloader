# jobs.py
import gradio as gr
import globals
from utils import extract_filename_from_url

def jobs_to_table():
    return [[job["url"], job["filename"], job["directory"], job["status"]] for job in globals.download_jobs]

def add_job(url, filename, curr_selected_dir):
    if not url:
        return gr.update(value=jobs_to_table()), "❌ URL wajib diisi"
    if not curr_selected_dir:
        return gr.update(value=jobs_to_table()), "❌ Set download directory dulu (📌 Set Dir)"
    if not filename:
        filename = extract_filename_from_url(url)
    job = {
        "url": url.strip(),
        "filename": filename.strip(),
        "directory": curr_selected_dir.strip(),
        "status": "Pending"
    }
    globals.download_jobs.append(job)
    return gr.update(value=jobs_to_table()), f"✅ Job ditambahkan: {job['filename']} → {job['directory']}"

def clear_jobs():
    globals.download_jobs = []
    return gr.update(value=jobs_to_table()), "🗑️ Semua job dihapus"
