# ui.py
import gradio as gr
from utils import get_folder_contents
from explorer import *
from jobs import *
from downloader import *
import globals

initial_items, initial_path = get_folder_contents("/mnt")


def execute_action(action, current_dir, selected_item, multi_input):
    if action == "🗑️ Delete":
        return check_and_confirm_delete(current_dir, selected_item)

    elif action == "📂 Move":
        msg, dd_update = move_or_copy(current_dir, selected_item, "move")
        return msg, dd_update, gr.update(visible=False), None

    elif action == "📄 Copy":
        msg, dd_update = move_or_copy(current_dir, selected_item, "copy")
        return msg, dd_update, gr.update(visible=False), None

    elif action == "➕ Create":
        msg, dd_update = create_folder_or_rename(
            current_dir, selected_item, multi_input, "create"
        )
        return msg, dd_update, gr.update(visible=False), None

    elif action == "🔁 Rename":
        msg, dd_update = create_folder_or_rename(
            current_dir, selected_item, multi_input, "rename"
        )
        return msg, dd_update, gr.update(visible=False), None

    else:
        items, _ = get_folder_contents(current_dir)
        return (
            "❌ Pilih aksi dulu",
            gr.update(choices=items, value=None),
            gr.update(visible=False),
            None,
        )


def set_download_and_display(current_dir):
    msg, path = set_download_dir(current_dir)
    return msg, f"📌 Download Dir: {path}"


def set_target_and_display(current_dir):
    msg, path = set_target_dir(current_dir)
    return msg, f"🎯 Target Dir: {path}"


def build_ui():
    with gr.Blocks(
        title="🚀 Batch File Downloader + Explorer", theme=gr.themes.Soft()
    ) as demo:
        gr.HTML(
            "<h2 style='text-align:center'>🚀 Batch File Downloader + Folder Explorer</h2>"
        )

        with gr.Row():
            # Explorer Panel
            with gr.Column(scale=1):
                gr.Markdown("### 📁 Folder Explorer")

                explorer_status = gr.Textbox(label="📝 Explorer Status", lines=2)
                current_directory = gr.Textbox(
                    label="📂 Current Directory", value=initial_path, interactive=False
                )
                folder_dropdown = gr.Dropdown(
                    label="📂 Folders & Files", choices=initial_items
                )

                # Navigasi + Aksi (satu baris)
                with gr.Row():
                    enter_btn = gr.Button("➡️", scale=0, min_width=40)
                    refresh_btn = gr.Button("🔄", scale=0, min_width=40)

                    action_dropdown = gr.Dropdown(
                        label="📋 Aksi",
                        choices=["🗑️ Delete", "📂 Move", "📄 Copy", "➕ Create", "🔁 Rename"],
                        value=None,
                        scale=2
                    )
                    execute_btn = gr.Button("▶", scale=0, min_width=60)

                # Input tambahan untuk Create / Rename
                multi_input = gr.Textbox(label="✏️ Create / Rename", scale=3)

                # Upload Files (multi)
                upload_files_input = gr.File(
                    label="⬆️ Upload Files",
                    type="filepath",
                    file_count="multiple",   # multi-file
                    file_types=["file"]      # semua tipe file
                )
                upload_files_btn = gr.Button("🚀 Upload Files")

            # Batch Panel
            with gr.Column(scale=2):
                gr.Markdown("### 📥 Batch Jobs")
                with gr.Row():
                    url_input = gr.Textbox(label="📎 Download URL", scale=3)
                    filename_input = gr.Textbox(label="📄 Filename (optional)", scale=2)

                url_input.change(
                    update_filename_from_url,
                    inputs=[url_input],
                    outputs=[filename_input],
                )

                with gr.Row():
                    set_download_btn = gr.Button(
                        "📌 Set Download Dir", scale=0, min_width=40
                    )
                    set_target_btn = gr.Button(
                        "🎯 Set Target Dir", scale=0, min_width=40
                    )
                    selected_dir_display = gr.Textbox(
                        label="📂 Selected Directory",
                        value=f"📌 Download Dir: {globals.selected_download_dir}",
                        interactive=False,
                    )

                with gr.Row():
                    add_btn = gr.Button("➕ Add Job", size="sm")
                    clear_btn = gr.Button("🗑️ Clear All", size="sm")

                job_table = gr.Dataframe(
                    headers=["URL", "Filename", "Directory", "Status"],
                    datatype=["str", "str", "str", "str"],
                    interactive=False,
                    value=jobs_to_table(),
                    label="📋 Job Queue",
                    wrap=True,
                )

                with gr.Row():
                    start_btn = gr.Button("▶️ Start", size="sm")
                    cancel_btn = gr.Button("⏹️ Cancel", size="sm")

                batch_status = gr.Textbox(label="Batch Status", lines=4)

        # Konfirmasi hapus
        with gr.Group(visible=False) as confirm_group:
            confirm_text = gr.Markdown("⚠️ Folder ini berisi file. Yakin hapus?")
            with gr.Row():
                yes_btn = gr.Button("✅ Continue")
                no_btn = gr.Button("❌ Cancel")
            pending_delete = gr.State()

        # ====== Events ======
        # Navigasi
        enter_btn.click(
            enter_folder,
            inputs=[current_directory, folder_dropdown],
            outputs=[folder_dropdown, current_directory],
        )
        refresh_btn.click(
            refresh_folder, inputs=[current_directory], outputs=[folder_dropdown]
        )

        # Eksekusi aksi
        execute_btn.click(
            execute_action,
            inputs=[action_dropdown, current_directory, folder_dropdown, multi_input],
            outputs=[explorer_status, folder_dropdown, confirm_group, pending_delete],
        )

        # Konfirmasi hapus
        yes_btn.click(
            confirm_delete_folder,
            inputs=[pending_delete],
            outputs=[explorer_status, folder_dropdown, confirm_group],
        )
        no_btn.click(
            lambda: ("❌ Dibatalkan", gr.update(choices=[]), gr.update(visible=False)),
            outputs=[explorer_status, folder_dropdown, confirm_group],
        )

        # Upload files
        upload_files_btn.click(
            upload_file,
            inputs=[current_directory, upload_files_input],
            outputs=[explorer_status, folder_dropdown],
        )

        # Set dirs
        set_download_btn.click(
            set_download_and_display,
            inputs=[current_directory],
            outputs=[explorer_status, selected_dir_display],
        )
        set_target_btn.click(
            set_target_and_display,
            inputs=[current_directory],
            outputs=[explorer_status, selected_dir_display],
        )

        # Batch job
        add_btn.click(
            lambda url, filename: add_job(url, filename, globals.selected_download_dir),
            inputs=[url_input, filename_input],
            outputs=[job_table, batch_status],
        )
        clear_btn.click(clear_jobs, outputs=[job_table, batch_status])
        start_btn.click(start_download_queue, outputs=[job_table, batch_status])
        cancel_btn.click(cancel_all, outputs=[batch_status])

    return demo
