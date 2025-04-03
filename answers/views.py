# answers/views.py
from rest_framework import viewsets
from .models import Answer
from .serializers import AnswerSerializer

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer