import cv2
import numpy as np
from insightface.app import FaceAnalysis

_app = None  # singleton en memoria


def get_face_app():
    global _app
    if _app is None:
        _app = FaceAnalysis(name="buffalo_l",providers=["CPUExecutionProvider"]  # 🔴 FORZAMOS CPU
    )
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app


def l2_normalize(vec):
    v = np.asarray(vec, dtype=np.float32)
    n = np.linalg.norm(v)
    if n == 0 or np.isnan(n):
        return None
    return (v / n).astype(np.float32)


def cosine_similarity(a, b):
    return float(np.dot(a, b))


def generate_embedding(image_input, from_bytes=False):
    if from_bytes:
        npimg = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(image_input)

    if img is None:
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    app = get_face_app()  # 🔥 AQUÍ se carga el modelo (si aún no existe)

    faces = app.get(img)

    if len(faces) != 1:
        return None

    return faces[0].embedding.tolist()
