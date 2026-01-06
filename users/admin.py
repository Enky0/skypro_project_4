from django.contrib import admin
from .models import BaseUser


# Register your models here.

@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'country', 'is_blocked', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_blocked', 'is_staff', 'is_superuser', 'country', 'date_joined')
    search_fields = ('email', 'phone')
    ordering = ('-date_joined',)
