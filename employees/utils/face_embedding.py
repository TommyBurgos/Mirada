import cv2
import numpy as np
from insightface.app import FaceAnalysis

# 🔥 Singleton del modelo en memoria (por proceso)

_face_app = None

def get_face_app():
    global _face_app

    if _face_app is None:
        _face_app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            allowed_modules=["detection", "recognition"],  # 🔥 CLAVE
        )
        _face_app.prepare(ctx_id=0, det_size=(640, 640))

    return _face_app


def l2_normalize(vec):
    v = np.asarray(vec, dtype=np.float32)
    n = np.linalg.norm(v)
    if n == 0 or np.isnan(n):
        return None
    return (v / n).astype(np.float32)


def cosine_similarity(a, b):
    # ambos vectores deben venir normalizados
    return float(np.dot(a, b))


def generate_embedding(image_input, from_bytes=False):
    if from_bytes:
        npimg = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(image_input)

    if img is None:
        return None

    # 🔥 OpenCV -> RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    app = get_face_app()  # ✅ aquí ya NUNCA será None
    faces = app.get(img)

    # Solo aceptamos UNA cara
    if len(faces) != 1:
        return None

    return faces[0].embedding.tolist()
