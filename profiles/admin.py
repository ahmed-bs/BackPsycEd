from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = [
        'parent',
        'category',
        'first_name',
        'last_name',
        'birth_date',
        'diagnosis',
        'notes',
        'evaluation_score',
        'objectives',
        'progress',
        'recommended_strategies',
        'image_url',
        'is_active'
    ]
    list_display = ['first_name', 'last_name', 'parent', 'is_active']

# @admin.register(ProfileShare)
# class ProfileShareAdmin(admin.ModelAdmin):
#     list_display = ['profile', 'shared_with', 'can_read', 'can_write', 'can_update', 'can_delete']