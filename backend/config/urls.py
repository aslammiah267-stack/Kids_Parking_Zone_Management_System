from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import LoginView, MeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me/", MeView.as_view(), name="auth_me"),
    path("api/guardians/", include("apps.guardians.urls")),
    path("api/children/", include("apps.children.urls")),
    path("api/vehicles/", include("apps.vehicles.urls")),
    path("api/parking-slots/", include("apps.parking.slot_urls")),
    path("api/parking-records/", include("apps.parking.record_urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/compiler/", include("apps.compiler.urls")),
    path("api/settings/", include("apps.parking.settings_urls")),
]
