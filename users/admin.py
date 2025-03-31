from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ('phone_number', 'street_address', 'zip_code', 'state', 'profile_picture')

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'user_type')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)