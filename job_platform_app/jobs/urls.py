from django.urls import path

from .views import (
    JobCategoryListCreateView, JobCategoryDetailView,
    JobListCreateView, JobDetailView
)


urlpatterns = [
    # categories
    path("categories/", JobCategoryListCreateView.as_view(), name="job-category-list"),
    path("categories/<int:pk>/", JobCategoryDetailView.as_view(), name="job-category-detail"),

    # jobs
    path("", JobListCreateView.as_view(), name="job-list"),
    path("<uuid:pk>/", JobDetailView.as_view(), name="job-detail"),
]
