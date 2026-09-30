from rest_framework import viewsets, filters

from apps.users.permissions import IsAdminOrReadCreateStaff
from .models import Guardian
from .serializers import GuardianSerializer


class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.all().prefetch_related("children")
    serializer_class = GuardianSerializer
    permission_classes = [IsAdminOrReadCreateStaff]
    lookup_field = "guardian_id"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["guardian_id", "name", "phone"]
    ordering_fields = ["guardian_id", "name", "created_at"]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            from apps.users.permissions import IsAdminRole

            return [IsAdminRole()]
        return super().get_permissions()
