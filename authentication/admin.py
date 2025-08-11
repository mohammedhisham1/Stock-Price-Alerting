from django.contrib import admin

# Register your models here.
from .models import User

# admin.site.register(User)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'created_at', 'updated_at')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'created_at')
    ordering = ('username',)

admin.site.register(User, UserAdmin)