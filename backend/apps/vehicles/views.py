from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsAdminOrReadCreateStaff, IsAdminRole
from apps.parking.models import ParkingRecord
from apps.parking.serializers import ParkingRecordSerializer
from .models import Vehicle
from .serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.select_related("child", "child__guardian").all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminOrReadCreateStaff]
    lookup_field = "vehicle_id"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["vehicle_id", "child__child_id", "child__name", "vehicle_type"]
    ordering_fields = ["vehicle_id", "vehicle_type", "created_at"]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAdminRole()]
        return super().get_permissions()

    @action(detail=True, methods=["get"])
    def history(self, request, vehicle_id=None):
        vehicle = self.get_object()
        records = ParkingRecord.objects.filter(vehicle=vehicle).select_related(
            "vehicle", "slot", "vehicle__child", "vehicle__child__guardian"
        )
        return Response(ParkingRecordSerializer(records, many=True).data)
