import cv2

from deepface import DeepFace
from django.http.response import JsonResponse
from django.shortcuts import render


def index(request):
    return JsonResponse(DeepFace.verify(
        img1_path="/home/lekarus/SQLQueries/web_app/app/static/img1.jpg",
        img2_path="/home/lekarus/SQLQueries/web_app/app/static/img2.jpg",
        model_name='ArcFace'
    ))


def camera(request):
    return render(request, 'index.html')


def opencv_camera(request):
    camera = cv2.VideoCapture(0)
    for i in range(10):
        return_value, image = camera.read()
    cv2.imwrite('img2.jpg', image)
    del(camera)
