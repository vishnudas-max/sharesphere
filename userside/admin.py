# userside/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser,Verification,Posts,UserReports

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('phone_number', 'username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_pic', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_date')}),
        ('Relationships', {'fields': ('following', 'followers', 'blocked_users')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('phone_number', 'username', 'email', 'is_admin')
    search_fields = ('phone_number', 'username', 'email')
    ordering = ('phone_number',)
    list_filter = ('is_admin', 'is_active', 'is_verified', 'is_staff', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Verification)
admin.site.register(Posts)
admin.site.register(UserReports)