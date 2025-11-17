import uuid
from django.db import models
# from django.contrib.auth import get_user_model
from location_field.models.plain import PlainLocationField
from django.conf import settings

# User = get_user_model()


class JobCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ("full-time", "Full Time"),
        ("part-time", "Part Time"),
        ("contract", "Contract"),
        ("remote", "Remote"),
        ("internship", "Internship"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255)

    location = models.CharField(max_length=255)
    full_location = PlainLocationField(
        based_fields=["location"],
        zoom=7,
        blank=True,
        null=True
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)

    category = models.ForeignKey(
        JobCategory,
        related_name="jobs",
        on_delete=models.SET_NULL,
        null=True
    )

    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posted_jobs",
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["job_type"]),
            models.Index(fields=["category"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
