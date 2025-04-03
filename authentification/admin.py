from django.contrib import admin
from .models import CustomUser

admin.site.register(CustomUser)
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

if Group not in admin.site._registry:
    admin.site.register(Group, GroupAdmin)

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

admin.site.register(Permission)
