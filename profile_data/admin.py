from django.contrib import admin
from .models import ProfileCategory, ProfileDomain, ProfileItem

@admin.register(ProfileCategory)
class ProfileCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile', 'template_category']
    list_filter = ['profile']

@admin.register(ProfileDomain)
class ProfileDomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile_category', 'item_count', 'acquis_percentage']
    list_filter = ['profile_category__profile']

@admin.register(ProfileItem)
class ProfileItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile_domain', 'etat', 'is_modified', 'modified_at']
    list_filter = ['profile_domain__profile_category__profile', 'etat', 'is_modified']