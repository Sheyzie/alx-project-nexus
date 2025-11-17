from django.urls import path
from .views import (
    CountryListCreateView, CountryDetailView,
    StateListCreateView, StateDetailView,
    CityListCreateView, CityDetailView,
)

urlpatterns = [
    # country view
    path("countries/", CountryListCreateView.as_view(), name="country-list"),
    path("countries/<uuid:pk>/", CountryDetailView.as_view(), name="country-detail"),

    # state view
    path("states/", StateListCreateView.as_view(), name="state-list"),
    path("states/<uuid:pk>/", StateDetailView.as_view(), name="state-detail"),

    # cities view
    path("cities/", CityListCreateView.as_view(), name="city-list"),
    path("cities/<uuid:pk>/", CityDetailView.as_view(), name="city-detail"),
]
