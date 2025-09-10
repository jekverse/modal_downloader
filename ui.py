# ui.py
import gradio as gr
from utils import get_folder_contents
from explorer import *
from jobs import *
from downloader import *
import globals

initial_items, initial_path = get_folder_contents("/root")

def build_ui():
    with gr.Blocks(title="🚀 Batch File Downloader + Explorer", theme=gr.themes.Soft()) as demo:
        gr.HTML("<h2 style='text-align:center'>🚀 Batch File Downloader + Folder Explorer</h2>")

        with gr.Row():
            # Explorer Panel
            with gr.Column(scale=1):
                gr.Markdown("### 📁 Folder Explorer")
                current_directory = gr.Textbox(label="📂 Current Directory", value=initial_path, interactive=False)
                explorer_status = gr.Textbox(label="📝 Explorer Status", lines=2)
                folder_dropdown = gr.Dropdown(label="📂 Folders & Files", choices=initial_items)

                with gr.Row():
                    enter_btn = gr.Button("➡️", scale=0, min_width=40)
                    parent_btn = gr.Button("⬅️", scale=0, min_width=40)
                    refresh_btn = gr.Button("🔄", scale=0, min_width=40)
                    delete_btn = gr.Button("🗑️", scale=0, min_width=40)
                    set_dir_btn = gr.Button("📌", scale=0, min_width=40)

                with gr.Row():
                    multi_input = gr.Textbox(label="✏️ Create / Rename", scale=3)
                    create_btn = gr.Button("➕", scale=0, min_width=40)
                    rename_btn = gr.Button("🔁", scale=0, min_width=40)

            # Batch Panel
            with gr.Column(scale=2):
                gr.Markdown("### 📥 Batch Jobs")
                with gr.Row():
                    url_input = gr.Textbox(label="📎 Download URL", scale=3)
                    filename_input = gr.Textbox(label="📄 Filename (optional)", scale=2)
                    selected_dir_display = gr.Textbox(label="📌 Selected Download Dir", value=globals.selected_download_dir, interactive=False)

                url_input.change(update_filename_from_url, inputs=[url_input], outputs=[filename_input])

                with gr.Row():
                    add_btn = gr.Button("➕ Add Job", size="sm")
                    clear_btn = gr.Button("🗑️ Clear All", size="sm")

                job_table = gr.Dataframe(
                    headers=["URL", "Filename", "Directory", "Status"],
                    datatype=["str", "str", "str", "str"],
                    interactive=False,
                    value=jobs_to_table(),
                    label="📋 Job Queue",
                    wrap=True
                )

                with gr.Row():
                    start_btn = gr.Button("▶️ Start", size="sm")
                    cancel_btn = gr.Button("⏹️ Cancel", size="sm")

                batch_status = gr.Textbox(label="Batch Status", lines=4)

        # --- Konfirmasi hapus (hidden group)
        with gr.Group(visible=False) as confirm_group:
            confirm_text = gr.Markdown("⚠️ Folder ini berisi file. Yakin hapus?")
            with gr.Row():
                yes_btn = gr.Button("✅ Continue")
                no_btn = gr.Button("❌ Cancel")
            pending_delete = gr.State()

        # ====== Events
        enter_btn.click(enter_folder, inputs=[current_directory, folder_dropdown], outputs=[folder_dropdown, current_directory])
        parent_btn.click(lambda c: enter_folder(c, ".. (Parent Directory)"), inputs=[current_directory], outputs=[folder_dropdown, current_directory])
        refresh_btn.click(refresh_folder, inputs=[current_directory], outputs=[folder_dropdown])

        delete_btn.click(
            check_and_confirm_delete,
            inputs=[current_directory, folder_dropdown],
            outputs=[explorer_status, confirm_group, pending_delete]
        )
        yes_btn.click(
            confirm_delete_folder,
            inputs=[pending_delete],
            outputs=[explorer_status, folder_dropdown, confirm_group]
        )
        no_btn.click(lambda: ("❌ Dibatalkan", gr.update(visible=False)), outputs=[explorer_status, confirm_group])

        # Create / Rename / Set Dir
        create_btn.click(create_folder_or_rename, inputs=[current_directory, folder_dropdown, multi_input, gr.State("create")], outputs=[explorer_status, folder_dropdown])
        rename_btn.click(create_folder_or_rename, inputs=[current_directory, folder_dropdown, multi_input, gr.State("rename")], outputs=[explorer_status, folder_dropdown])
        set_dir_btn.click(lambda c: set_download_dir(c), inputs=[current_directory], outputs=[explorer_status, selected_dir_display])

        # Batch job
        add_btn.click(add_job, inputs=[url_input, filename_input, selected_dir_display], outputs=[job_table, batch_status])
        clear_btn.click(clear_jobs, outputs=[job_table, batch_status])
        start_btn.click(start_download_queue, outputs=[job_table, batch_status])
        cancel_btn.click(cancel_all, outputs=[batch_status])

    return demo
