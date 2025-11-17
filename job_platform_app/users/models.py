import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    role = models.CharField(max_length=20, default="user")  # admin | user

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    social_auth_provider = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    fullname = models.CharField(max_length=255, null=True, blank=True)
    headline = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    phone_number = models.CharField(max_length=100, null=True, blank=True)

    location = models.UUIDField(null=True, blank=True)  # TODO: will link later

    resume_url = models.TextField(null=True, blank=True)

    skill = models.UUIDField(null=True, blank=True)  # TODO: will link later

    visibility = models.CharField(max_length=20, default="public")  # public/private

    def __str__(self):
        return f"Profile of {self.user.email}"

