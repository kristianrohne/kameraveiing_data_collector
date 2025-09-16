# storage.py
import os, imghdr
from datetime import datetime
from werkzeug.utils import secure_filename

UPLOAD_ROOT = os.environ.get("UPLOAD_DIR", "data/uploads")

def save_image(file_storage, weight_kg: float, pig_uid: str, picture_number: int, user_id: str) -> tuple[str, str]:
    """
    Save uploaded image with format: weight_kg_uid{pig_uid}_{picture_number}_userID{user_id}.png
    Returns (relative_path, absolute_path).
    """
    # Validation
    raw = file_storage.read()
    if len(raw) > 50 * 1024 * 1024:
        raise ValueError("Image too large (max 50MB)")
    
    if imghdr.what(None, h=raw) not in {"jpeg", "png", "webp"}:
        raise ValueError("Unsupported image type")

    # Create filename
    safe_pig_uid = secure_filename(str(pig_uid)) or "unknown"
    safe_user_id = secure_filename(str(user_id)) or "unknown"
    filename = f"{weight_kg:.2f}kg_uid{safe_pig_uid}_{picture_number}_userID{safe_user_id}.png"
    
    # Save all files in UPLOAD_ROOT
    upload_dir = os.path.abspath(UPLOAD_ROOT)
    os.makedirs(upload_dir, exist_ok=True)

    rel_path = filename
    abs_path = os.path.join(upload_dir, filename)

    with open(abs_path, "wb") as f:
        f.write(raw)

    file_storage.stream.seek(0)  # Reset stream
    return rel_path, abs_path