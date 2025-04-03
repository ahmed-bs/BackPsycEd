# answers/admin.py
from django.contrib import admin
from .models import Answer

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question')