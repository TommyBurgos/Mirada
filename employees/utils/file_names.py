import uuid
import os

def employee_face_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1] or ".jpg"
    return f"employee_faces/{uuid.uuid4().hex}{ext}"
