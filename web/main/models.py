from django.db import models


class Person(models.Model):
    username = models.CharField(max_length=150)
    teacher = models.BooleanField(default=False)
    pupil = models.BooleanField(default=False)
    user_id = models.IntegerField()

    def __str__(self):
        return '<Person:{}:{}>'.format(
            self.username,
            'Teacher' if self.teacher else 'Pupil'
        )
