import os
import shutil
import gradio as gr
from pathlib import Path
from utils import get_folder_contents
import globals  


def move_or_copy(current_dir, item_name, mode):
    target_dir = globals.selected_target_dir
    if not item_name or not target_dir:
        return "❌ Pilih item dan target dulu", gr.update()
    src = os.path.join(current_dir, item_name)
    dst = os.path.join(target_dir, item_name)
    try:
        if mode == "move":
            shutil.move(src, dst)
            msg = f"✅ Moved {item_name} → {target_dir}"
        elif mode == "copy":
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            msg = f"✅ Copied {item_name} → {target_dir}"
        items, _ = get_folder_contents(current_dir)
        return msg, gr.update(choices=items, value=None)
    except Exception as e:
        items, _ = get_folder_contents(current_dir)
        return f"❌ Error: {str(e)}", gr.update(choices=items, value=None)


def refresh_folder(current_dir):
    items, _ = get_folder_contents(current_dir)
    return gr.update(choices=items, value=None)


def enter_folder(current_dir, item_name):
    if item_name == ".. (Parent Directory)":
        new_dir = str(Path(current_dir).parent)
    else:
        new_dir = os.path.join(current_dir, item_name)
        if not os.path.isdir(new_dir):
            items, _ = get_folder_contents(current_dir)
            return gr.update(choices=items, value=None), current_dir
    items, path = get_folder_contents(new_dir)
    return gr.update(choices=items, value=None), path


def check_and_confirm_delete(current_dir, item_name):
    if not item_name:
        items, _ = get_folder_contents(current_dir)
        return "❌ Pilih item dulu", gr.update(choices=items, value=None), gr.update(visible=False), None

    path_to_delete = os.path.join(current_dir, item_name)
    if not os.path.exists(path_to_delete):
        items, _ = get_folder_contents(current_dir)
        return "❌ Item tidak ada", gr.update(choices=items, value=None), gr.update(visible=False), None

    if os.path.isfile(path_to_delete):
        try:
            os.remove(path_to_delete)
            items, _ = get_folder_contents(current_dir)
            return f"✅ File deleted: {item_name}", gr.update(choices=items, value=None), gr.update(visible=False), None
        except Exception as e:
            items, _ = get_folder_contents(current_dir)
            return f"❌ Error: {str(e)}", gr.update(choices=items, value=None), gr.update(visible=False), None

    elif os.path.isdir(path_to_delete):
        if not any(Path(path_to_delete).iterdir()):
            try:
                os.rmdir(path_to_delete)
                items, _ = get_folder_contents(current_dir)
                return f"✅ Folder deleted: {item_name}", gr.update(choices=items, value=None), gr.update(visible=False), None
            except Exception as e:
                items, _ = get_folder_contents(current_dir)
                return f"❌ Error: {str(e)}", gr.update(choices=items, value=None), gr.update(visible=False), None
        else:
            return f"⚠️ Folder '{item_name}' berisi file. Yakin hapus?", gr.update(choices=[]), gr.update(visible=True), (current_dir, item_name)

    return "❌ Unsupported item", gr.update(choices=[]), gr.update(visible=False), None


def confirm_delete_folder(data):
    if not data:
        return "❌ Tidak ada folder terpilih", gr.update(choices=[], value=None), gr.update(visible=False)
    current_dir, item_name = data
    path_to_delete = os.path.join(current_dir, item_name)
    try:
        shutil.rmtree(path_to_delete)
        items, _ = get_folder_contents(current_dir)
        return (
            f"✅ Folder deleted (with contents): {item_name}",
            gr.update(choices=items, value=None),
            gr.update(visible=False)
        )
    except Exception as e:
        items, _ = get_folder_contents(current_dir)
        return (
            f"❌ Error: {str(e)}",
            gr.update(choices=items, value=None),
            gr.update(visible=False)
        )


def create_folder_or_rename(current_dir, folder_dropdown, input_text, mode):
    if not input_text:
        items, _ = get_folder_contents(current_dir)
        return "❌ Nama tidak boleh kosong", gr.update(choices=items, value=None)

    if mode == "create":
        path_to_create = os.path.join(current_dir, input_text)
        try:
            os.makedirs(path_to_create, exist_ok=False)
            items, _ = get_folder_contents(current_dir)
            return f"✅ Folder created: {input_text}", gr.update(choices=items, value=None)
        except FileExistsError:
            items, _ = get_folder_contents(current_dir)
            return f"❌ Folder already exists: {input_text}", gr.update(choices=items, value=None)

    elif mode == "rename":
        if not folder_dropdown:
            items, _ = get_folder_contents(current_dir)
            return "❌ Pilih item dulu untuk rename", gr.update(choices=items, value=None)
        old_path = os.path.join(current_dir, folder_dropdown)
        new_path = os.path.join(current_dir, input_text)
        try:
            os.rename(old_path, new_path)
            items, _ = get_folder_contents(current_dir)
            return f"✅ Renamed {folder_dropdown} → {input_text}", gr.update(choices=items, value=None)
        except Exception as e:
            items, _ = get_folder_contents(current_dir)
            return f"❌ Error: {str(e)}", gr.update(choices=items, value=None)


def set_download_dir(current_dir):
    globals.selected_download_dir = current_dir
    return f"📂 Download directory set: {globals.selected_download_dir}", globals.selected_download_dir


def set_target_dir(current_dir):
    globals.selected_target_dir = current_dir
    return f"🎯 Target directory set: {globals.selected_target_dir}", globals.selected_target_dir


def upload_file(current_dir, file_obj):
    """
    Handle upload:
    - file_obj can be a single filepath (string) or list of filepaths (multi-file)
    - Copy files into current_dir
    """
    items, _ = get_folder_contents(current_dir)
    if not file_obj:
        return "❌ Tidak ada file yang diupload", gr.update(choices=items, value=None)

    # Normalize to list
    paths = file_obj if isinstance(file_obj, list) else [file_obj]
    uploaded_names = []

    try:
        for p in paths:
            if p is None:
                continue
            p = str(p)  # ensure str path

            if os.path.isfile(p):
                filename = os.path.basename(p)
                dst = os.path.join(current_dir, filename)
                shutil.copy2(p, dst)
                uploaded_names.append(filename)
            else:
                uploaded_names.append(f"[skip:{os.path.basename(p)}]")

        # refresh listing
        items, _ = get_folder_contents(current_dir)
        return f"✅ Uploaded: {', '.join(uploaded_names)}", gr.update(choices=items, value=None)

    except Exception as e:
        items, _ = get_folder_contents(current_dir)
        return f"❌ Error saat upload: {str(e)}", gr.update(choices=items, value=None)
