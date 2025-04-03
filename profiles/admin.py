from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Explicitly list editable fields (exclude bio)
    fields = [
        'parent',
        'first_name',
        'last_name',
        'birth_date',
        'diagnosis',
        'notes',
        'is_active'
    ]

    # Or alternatively, exclude the bio field
    # exclude = ['bio']

    list_display = ['first_name', 'last_name', 'parent']