# answers/models.py
from django.db import models
from questions.models import Question

class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    text = models.TextField()

    def __str__(self):
        return self.text