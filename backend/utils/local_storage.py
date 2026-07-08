import os
import uuid

BASE_DIR = "uploads/attachments"

def save_file_local(file_bytes: bytes, filename: str, user_id: int) -> str:
    user_dir = os.path.join(BASE_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    ext = filename.split(".")[-1]
    file_id = f"{uuid.uuid4()}.{ext}"

    file_path = os.path.join(user_dir, file_id)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return file_path