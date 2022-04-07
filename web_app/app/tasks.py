import cv2
from celery import shared_task


@shared_task
def get_photo():
    cap = cv2.VideoCapture(0)
    while True:
        prime, frame = cap.read()
        cv2.imshow('frame', frame)
        cv2.imwrite('app/static/cam.png', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
