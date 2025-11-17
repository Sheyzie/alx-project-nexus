import uuid
from django.db import models
from django.conf import settings
# from django.contrib.auth import get_user_model
from jobs.models import Job

# User = get_user_model()


class Application(models.Model):
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("reviewed", "Reviewed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="applications", on_delete=models.CASCADE)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="applications", on_delete=models.CASCADE)

    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("job", "applicant")  # Prevent duplicate applications
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["job"]),
            models.Index(fields=["applicant"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.applicant.email} → {self.job.title}"
