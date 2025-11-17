"""
URL configuration for job_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static




schema_view = get_schema_view(
    openapi.Info(
        title="Job Board API",
        default_version="v1",
        description="API documentation for the Job Board Platform",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# base API url
base_url = 'api/v1'


urlpatterns = [
    path(f'{base_url}/admin/', admin.site.urls),

    # API routes
    path(f'{base_url}/users/', include('users.urls')),
    # path(f'{base_url}/jobs/', include('jobs.urls')),
    path(f'{base_url}/companies/', include('companies.urls')),
    # path(f'{base_url}/applications/', include('applications.urls')),
    path(f'{base_url}/locations/', include('locations.urls')),

    # Swagger docs
    path(f'{base_url}/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
    path(f'{base_url}/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-docs'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

