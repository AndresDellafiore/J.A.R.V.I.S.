import cv2
import mediapipe as mp

class ARSystem:
    def __init__(self):
        self.mp_hands = mp.solutions.hands.Hands()

    def start_ar(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Procesamiento AR aquí
            cv2.imshow('J.A.R.V.I.S. AR', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()