import uuid
from django.db import models
from django.conf import settings


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    industry = models.CharField(max_length=200, null=True, blank=True)
    location = models.UUIDField(null=True, blank=True)  # link later
    website_url = models.URLField(null=True, blank=True)

    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
