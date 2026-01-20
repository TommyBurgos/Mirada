import cv2
import numpy as np
from PIL import Image
import io

# Cargar el clasificador Haar
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def detect_and_crop_face(image_input, from_bytes=False):

    if from_bytes:
        npimg = np.frombuffer(image_input, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(image_input)

    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) != 1:
        return None

    x, y, w, h = faces[0]
    face_img = img[y:y+h, x:x+w]
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

    return Image.fromarray(face_img)
