from rest_framework import viewsets, filters

from apps.users.permissions import IsAdminOrReadCreateStaff, IsAdminRole
from .models import Child
from .serializers import ChildSerializer


class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.select_related("guardian").all()
    serializer_class = ChildSerializer
    permission_classes = [IsAdminOrReadCreateStaff]
    lookup_field = "child_id"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["child_id", "name", "guardian__name", "guardian__guardian_id"]
    ordering_fields = ["child_id", "name", "age", "created_at"]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAdminRole()]
        return super().get_permissions()
