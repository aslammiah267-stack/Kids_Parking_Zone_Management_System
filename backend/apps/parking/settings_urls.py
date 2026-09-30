from django.urls import path

from .views import ParkingSettingsView

urlpatterns = [
    path("parking/", ParkingSettingsView.as_view(), name="parking-settings"),
]
