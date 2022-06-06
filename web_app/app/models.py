from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.URLField()


class Theme(models.Model):
    description = models.TextField()
    user = models.ManyToManyField(User)


class SubjectArea(models.Model):
    title = models.CharField(max_length=50)
    schema = models.URLField()


class TaskGroup(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.DO_NOTHING)
    subject_area = models.ForeignKey(SubjectArea, on_delete=models.DO_NOTHING)


class KeyWord(models.Model):
    word = models.CharField(max_length=32, primary_key=True)


class Task(models.Model):
    description = models.TextField()
    correct_script = models.TextField()
    time = models.PositiveSmallIntegerField()
    coefficient = models.PositiveSmallIntegerField()
    task_group = models.ForeignKey(TaskGroup, on_delete=models.DO_NOTHING)
    key_words = models.ManyToManyField(KeyWord)


class Grade(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING)
    is_work = models.BooleanField(null=True)
    is_same_count_of_lines = models.BooleanField(null=True)
    is_same_output = models.BooleanField(null=True)
    keywords_are_used = models.BooleanField(null=True)
    final_score = models.FloatField(default=0)
    user_script = models.TextField()
    user_output = models.TextField()

    def set_final_score(self):
        if not self.is_work:
            return
        self.final_score = self.final_score + 0.25
        if self.is_same_count_of_lines:
            self.final_score = self.final_score + 0.25
        if self.is_same_output:
            self.final_score = self.final_score + 0.25
        if self.keywords_are_used:
            self.final_score = self.final_score + 0.25
        self.save()

    @classmethod
    def find_or_create(cls, user, task):
        try:
            obj = cls.objects.get(user=user, task=task)
        except cls.DoesNotExist:
            obj = cls(user=user, task=task)
        obj.is_work = True
        obj.is_same_output = False
        obj.is_same_count_of_lines = False
        obj.keywords_are_used = True
        obj.final_score = 0
        return obj

    @classmethod
    def theme_is_passed(cls, theme: Theme, user: User):
        return cls.objects.filter(
            task__in=Task.objects.filter(task_group__in=TaskGroup.objects.filter(theme=theme)),
            user=user
        )

    def get_grade_json(self):
        return {
            "is_work": self.is_work*0.25,
            "count_of_lines": self.is_same_count_of_lines * 0.25,
            "output": self.is_same_output * 0.25,
            "keywords": self.keywords_are_used * 0.25,
        }

    def set_not_done(self):
        self.is_work = False
        self.is_same_output = False
        self.is_same_count_of_lines = False
        self.keywords_are_used = False
        self.set_final_score()
        self.save()
