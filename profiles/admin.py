from django.contrib import admin
from .models import Profile, SharedProfilePermission

class SharedProfilePermissionInline(admin.TabularInline):
    model = SharedProfilePermission
    extra = 1
    fields = ['shared_with', 'permissions']
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = [
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
        'is_active',
        'gender',  # Added gender field to match the updated Profile model
    ]
    list_display = ['first_name', 'last_name', 'get_associated_users', 'is_active']

    def get_associated_users(self, obj):
        """Display all users associated with this profile via SharedProfilePermission."""
        users = obj.associated_users
        return ", ".join(user.username for user in users) if users.exists() else "-"

    get_associated_users.short_description = "Associated Users"


@admin.register(SharedProfilePermission)
class SharedProfilePermissionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'shared_with', 'permissions']
    list_filter = ['permissions']
    search_fields = ['profile__first_name', 'profile__last_name', 'shared_with__username']