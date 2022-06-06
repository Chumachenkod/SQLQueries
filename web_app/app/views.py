import ast
import json

import cv2
from deepface import DeepFace
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import connections
from django.db.utils import ProgrammingError
from django.http import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.autoreload import logger
from django.views import View
from django.views.decorators.http import require_http_methods

from app.models import User, Theme, Task, TaskGroup, Grade
from app.utils import dictfetchall


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(request.GET.get("next", '/home/'))
        return render(request, 'login.html', context={"head": "Login, please!"})

    def post(self, request):
        user = User.objects.filter(email=request.POST["email"], password=request.POST["password"]).first()
        if user:
            login(request, user)
            return redirect(request.GET.get("next", '/home/'))
        return render(request, 'login.html', context={"head": "user not found"})


@require_http_methods(["GET"])
def start_page(request):
    return redirect("/login/")


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def home(request):
    themes = Theme.objects.filter(user=request.user)
    themes_list = list()
    for theme in themes:
        if not theme.taskgroup_set.all():
            continue
        task_group = theme.taskgroup_set.all()[0]
        themes_list.append(
            {
                "description": theme.description,
                "time": sum([task.time for task in task_group.task_set.all()]),
                "max_grade": sum([task.coefficient for task in task_group.task_set.all()]),
                "is_complete": bool(Grade.objects.filter(task__in=task_group.task_set.all())),
                "id": theme.id
            }
        )
    return render(request, 'home.html', context={
        "themes": themes_list
    })


@require_http_methods(["GET"])
@login_required(login_url='/login/')
def my_grades(request):
    themes = Theme.objects.filter(user=request.user)
    themes_list = list()
    for theme in themes:
        grades = Grade.theme_is_passed(theme, request.user)
        if not theme.taskgroup_set.all() or not grades:
            continue
        task_group = theme.taskgroup_set.all()[0]
        themes_list.append(
            {
                "description": theme.description,
                "my_grade": sum([grade.final_score for grade in grades]),
                "max_grade": sum([task.coefficient for task in task_group.task_set.all()]),
                "id": theme.id
            }
        )
    return render(request, 'grades.html', context={
        "themes": themes_list
    })


class CustomAuthMixin(UserPassesTestMixin):
    login_url = '/login/'


class SuperUserAuthMixin(CustomAuthMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class ThemeView(CustomAuthMixin, View):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        allow_themes = list(Theme.objects.filter(user=self.request.user).values_list('id', flat=True))
        theme_id = self.request.build_absolute_uri().split('/')[-2]
        return int(theme_id) in allow_themes

    def get(self, request, theme_id):
        theme = Theme.objects.get(pk=theme_id)
        task_group = TaskGroup.objects.filter(theme=theme).first()
        grades = Grade.theme_is_passed(theme, request.user)
        return render(request, "theme.html", context={
            "description": theme.description,
            "time": sum([task.time for task in task_group.task_set.all()]),
            "start_link": task_group.id,
            "button_desc": "Результати" if grades else "Почати",
            "subject_title": task_group.subject_area.title,
            "subject_image": task_group.subject_area.schema
        })


class TaskGroupView(CustomAuthMixin, View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, args, kwargs)
        self.task_group = TaskGroup.objects.filter(pk=kwargs["task_group_id"]).first()

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        theme = Theme.objects.filter(user=self.request.user)
        self.task_groupes = TaskGroup.objects.filter(theme__in=theme).values_list('id', flat=True)

        allow_task_group = list(self.task_groupes)
        task_group_id = self.request.build_absolute_uri().split('/')[-2]
        return int(task_group_id) in allow_task_group

    def get(self, request, task_group_id):
        # if Grade.objects.filter(task__in=Task.objects.filter(task_group=self.task_group)):
        #     return redirect(f'/grade_theme/{self.task_group.theme.id}', self.request)
        tasks = [
            {
                "id": task.id,
                "description": task.description,
            } for task in Task.objects.filter(task_group=self.task_group)
        ]
        return render(request, 'task.html', context={
            "tasks": tasks,
            "id": tasks[0]["id"],
            "subject_title": self.task_group.subject_area.title,
            "subject_img": self.task_group.subject_area.schema
        })

    def post(self, request, task_group_id):
        tasks = [
            {
                "id": task.id,
                "description": task.description,
            } for task in Task.objects.filter(task_group=self.task_group)
        ]
        return JsonResponse({"tasks": tasks})


@require_http_methods(["GET"])
def logout_view(request):
    logout(request)
    return redirect('/login', request)


class VerifyImage(SuperUserAuthMixin, View):
    def post(self, request: HttpRequest):
        img = bytes(request.POST["img"][22:], 'utf-8')
        with open("app/avatars/current_image.jpg", "wb") as fh:
            import base64
            fh.write(base64.decodebytes(img))

        try:
            data = DeepFace.verify(
                img1_path="app/avatars/current_image.jpg",
                img2_path=request.user.avatar,
                model_name='ArcFace'
            )
        except ValueError as e:
            print(e)
            data = dict()
            data["verified"] = False

        if data["verified"]:
            return HttpResponse('verified', status=200)
        return HttpResponse('not verified', status=400)


class GetImage(SuperUserAuthMixin, View):
    def get(self, request):
        camera = cv2.VideoCapture(0)
        import os
        try:
            os.remove("app/avatars/img_from_opencv.jpg")
        except:
            pass
        for i in range(10):
            return_value, image = camera.read()
            if return_value:
                cv2.imwrite('app/avatars/img_from_opencv.jpg', image)
        del camera
        cv2.destroyAllWindows()
        return HttpResponse('Image successfully saved on app/avatars/img_from_opencv.jpg')


class CheckSyntaxOfTask(View):
    def post(self, request):
        user_cursor = connections['postgres_trade'].cursor()
        try:
            user_cursor.execute(request.POST['script'])
            dictfetchall(user_cursor)
            return JsonResponse({"msg": "OK"})
        except ProgrammingError as ex:
            logger.error(f'DB Error: {ex}')
            return JsonResponse({'error': str(ex)}, status=400)


class TaskView(CustomAuthMixin, View):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        theme = Task.objects.get(pk=self.request.POST["task_id"]).task_group.theme
        return self.request.user in theme.user.all()

    def post(self, request):
        task = Task.objects.get(pk=self.request.POST["task_id"])
        return JsonResponse(
            {
                "description": task.description
            }
        )


class GradeTask(CustomAuthMixin, View):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.method == 'POST':
            theme = Task.objects.get(pk=self.request.POST["task"]).task_group.theme
        else:
            theme = Task.objects.get(pk=self.request.GET["task_id"]).task_group.theme
        return self.request.user in theme.user.all()

    def get(self, request):
        grade = Grade.objects.get(task_id=request.GET["task_id"], user=request.user)
        return JsonResponse({
            "description": grade.task.description,
            "user_script": grade.user_script,
            "grade": grade.get_grade_json()
        })

    def post(self, request):
        user_cursor = connections['postgres_trade'].cursor()
        correct_cursor = connections['postgres_trade'].cursor()
        task = Task.objects.get(pk=self.request.POST["task"])
        grade = Grade.find_or_create(user=self.request.user, task=task)
        user_script = request.POST['script']

        correct_cursor.execute(task.correct_script)
        correct_result = dictfetchall(correct_cursor)

        try:
            user_cursor.execute(user_script)

            user_result = dictfetchall(user_cursor)

            grade.user_script = user_script

            for keyword in task.key_words.all():
                if user_script.find(keyword.word) == -1:
                    grade.keywords_are_used = False
                    break

            if len(user_result) == len(correct_result):
                grade.is_same_count_of_lines = True
            if user_result == correct_result:
                grade.is_same_output = True

        except ProgrammingError as e:
            print(e)
            grade.is_work = False
            grade.keywords_are_used = False

        grade.set_final_score()

        return JsonResponse({"msg": "OK"})


class FinishTheme(CustomAuthMixin, View):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        theme = TaskGroup.objects.get(pk=self.request.POST["task_group"]).theme
        return self.request.user in theme.user.all()

    def post(self, request):
        tasks = TaskGroup.objects.get(pk=self.request.POST["task_group"]).task_set.all()
        for task in tasks:
            grade = Grade.find_or_create(request.user, task)
            if not grade.user_script:
                grade.set_not_done()
        return JsonResponse({"msg": "OK"})


class GradeTheme(CustomAuthMixin, View):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        allow_themes = list(Theme.objects.filter(user=self.request.user).values_list('id', flat=True))
        theme_id = self.request.build_absolute_uri().split('/')[-2]
        return int(theme_id) in allow_themes

    def get(self, request, theme_id):
        theme = Theme.objects.get(pk=theme_id)
        task_group = TaskGroup.objects.filter(theme=theme).first()
        grades = Grade.theme_is_passed(theme, request.user)
        if grades:
            return render(request, "theme_passed.html", context={
                "tasks": [
                    {
                        "id": task.id,
                        "description": task.description,
                        "grade": Grade.objects.get(task=task, user=request.user).final_score
                    } for task in task_group.task_set.all()
                ],
                "current_grade": sum([grade.final_score for grade in grades]),
                "max_grade": len(grades),
                "complete": sum([grade.final_score for grade in grades]) > len(grades) / 0.6
            })
        return render(request, "theme.html", context={
            "description": theme.description,
            "time": sum([task.time for task in task_group.task_set.all()]),
            "start_link": task_group.id,
            "subject_title": task_group.subject_area.title,
            "subject_image": task_group.subject_area.schema
        })

