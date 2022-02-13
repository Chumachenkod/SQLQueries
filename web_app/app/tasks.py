import cv2


def get_photo():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite('static/cam.png', frame)
    cap.release()


get_photo()
