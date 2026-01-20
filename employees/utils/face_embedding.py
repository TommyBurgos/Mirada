import cv2
import numpy as np
from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640,640))

import numpy as np

def l2_normalize(vec):
    v = np.asarray(vec, dtype=np.float32)
    n = np.linalg.norm(v)
    if n == 0 or np.isnan(n):
        return None
    return (v / n).astype(np.float32)

def cosine_similarity(a, b):
    # a y b deben venir NORMALIZADOS
    return float(np.dot(a, b))



def generate_embedding(image_input, from_bytes=False):

    if from_bytes:
        npimg = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(image_input)

    # 🔴 Si OpenCV no pudo decodificar
    if img is None:
        return None

    # 🔥 Forzamos conversión a RGB estándar
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faces = app.get(img)

    if len(faces) != 1:
        return None

    return faces[0].embedding.tolist()
