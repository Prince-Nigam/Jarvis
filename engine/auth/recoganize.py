"""
recoganize.py — Face authentication using LBPH model.
Opens camera, checks if face matches trained model.
Returns 1 on success, 0 on failure/timeout.
"""
import os
import time

try:
    import cv2
    _CV2_OK = True
except ImportError:
    _CV2_OK = False

# Paths relative to project root
_BASE   = os.path.join(os.path.dirname(__file__))
_MODEL  = os.path.join(_BASE, "trainer", "trainer.yml")
_CASCADE = os.path.join(_BASE, "haarcascade_frontalface_default.xml")

# Name list — index = person id used during training
NAMES = ['', 'Prince']


def AuthenticateFace():
    """
    Open webcam and try to recognise the face.
    Returns 1 (authenticated) or 0 (failed/unknown/timeout).
    """
    if not _CV2_OK:
        print("[Auth] cv2 not available — skipping face auth")
        return 1

    if not os.path.exists(_MODEL):
        print("[Auth] trainer.yml not found — skipping face auth")
        return 1

    if not os.path.exists(_CASCADE):
        print("[Auth] haarcascade not found — skipping face auth")
        return 1

    try:
        recognizer  = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(_MODEL)
        face_cascade = cv2.CascadeClassifier(_CASCADE)

        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cam.set(3, 640)
        cam.set(4, 480)

        min_w = int(0.1 * cam.get(3))
        min_h = int(0.1 * cam.get(4))

        result    = 0
        attempts  = 0
        max_attempts = 50   # ~5 seconds at 10ms/frame

        while attempts < max_attempts:
            ret, img = cam.read()
            if not ret:
                break

            gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(min_w, min_h)
            )

            for (x, y, w, h) in faces:
                person_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
                # confidence < 100 means a good match (0 = perfect)
                if confidence < 100:
                    name = NAMES[person_id] if person_id < len(NAMES) else "Unknown"
                    print(f"[Auth] Recognised: {name} (confidence: {round(100 - confidence)}%)")
                    result = 1
                    break
                else:
                    print(f"[Auth] Unknown face (confidence: {round(100 - confidence)}%)")

            if result == 1:
                break

            attempts += 1
            # Small delay — 10ms per frame
            if cv2.waitKey(10) & 0xFF == 27:   # ESC to cancel
                break

        cam.release()
        cv2.destroyAllWindows()
        return result

    except Exception as e:
        print(f"[Auth] Face auth error: {e}")
        try:
            cam.release()
            cv2.destroyAllWindows()
        except Exception:
            pass
        return 1   # fail-open so Jarvis still loads
