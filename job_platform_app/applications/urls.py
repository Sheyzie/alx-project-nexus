from django.urls import path

from .views import ApplyToJobView, ApplicationListView, ApplicationDetailView


urlpatterns = [
    path("", ApplicationListView.as_view(), name="application-list"),
    path("apply/", ApplyToJobView.as_view(), name="apply-to-job"),
    path("<uuid:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
]
