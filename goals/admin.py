# goals/admin.py

from django.contrib import admin
from .models import Goal

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    # Option 1: Use existing fields from Goal model
    list_display = ('id', 'title', 'description')  # Replace with actual fields
    
    # Option 2: Create custom methods
    list_display = ('get_name', 'get_category')
    
    def get_name(self, obj):
        return obj.title  # Or whatever field contains the name
    get_name.short_description = 'Name'
    
    def get_category(self, obj):
        return obj.category.name if obj.category else None
    get_category.short_description = 'Category'