import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_image(file):
    """Save uploaded image and return filename."""
    if not file or file.filename == "":
        return None
    if not allowed_file(file.filename):
        raise ValueError("File type is not allowed. Allowed: png, jpg, jpeg, gif, webp")

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    safe_name = secure_filename(unique_name)
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, safe_name))
    return safe_name


def delete_image(filename):
    """Remove image file from disk."""
    if not filename:
        return

    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        os.remove(path)
