from django.urls import path

from .views import DashboardReportView, SummaryReportView

urlpatterns = [
    path("dashboard/", DashboardReportView.as_view(), name="reports-dashboard"),
    path("summary/", SummaryReportView.as_view(), name="reports-summary"),
]
