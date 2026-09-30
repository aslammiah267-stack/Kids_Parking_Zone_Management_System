from django.urls import path

from .views import CompilerExecuteView

urlpatterns = [
    path("execute/", CompilerExecuteView.as_view(), name="compiler-execute"),
]
