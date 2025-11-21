from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_active", "is_staff")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("fullname", "phone_number")
