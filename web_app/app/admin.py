from django.contrib import admin
from .models import Grade, KeyWord, SubjectArea, TaskGroup, Task, Theme, User

admin.site.register(Grade)
admin.site.register(KeyWord)
admin.site.register(SubjectArea)
admin.site.register(TaskGroup)
admin.site.register(Task)
admin.site.register(Theme)
admin.site.register(User)

