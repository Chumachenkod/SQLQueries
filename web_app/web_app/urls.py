from django.contrib import admin
from django.urls import path

from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home),
    path('my_grades/', views.my_grades),
    path('login/', views.LoginView.as_view()),
    path('logout/', views.logout_view),
    path('', views.start_page),
    path('theme/<int:theme_id>/', views.ThemeView.as_view()),
    path('task_group/<int:task_group_id>/', views.TaskGroupView.as_view()),
    path('task/', views.TaskView.as_view()),
    path('verify_image/', views.VerifyImage.as_view()),
    path('get_image/', views.GetImage.as_view()),
    path('check_syntax/', views.CheckSyntaxOfTask.as_view()),
    path('grade_task/', views.GradeTask.as_view()),
    path('grade_theme/<int:theme_id>/', views.GradeTheme.as_view(), name="grade_theme"),
    path('finish_theme/', views.FinishTheme.as_view()),
]
