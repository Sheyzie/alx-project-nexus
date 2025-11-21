from django.contrib import admin

from .models import Job, JobCategory

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "created_at")


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
