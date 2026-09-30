from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminOrReadCreateStaff, IsAdminRole
from apps.vehicles.models import Vehicle
from .models import ParkingRecord, ParkingSettings, ParkingSlot
from .serializers import ParkingRecordSerializer, ParkingSettingsSerializer, ParkingSlotSerializer
from .services import park_vehicle, process_entry, process_exit, preview_duration_and_fee


class ParkingSlotViewSet(viewsets.ModelViewSet):
    queryset = ParkingSlot.objects.all()
    serializer_class = ParkingSlotSerializer
    permission_classes = [IsAdminOrReadCreateStaff]
    lookup_field = "slot_id"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["slot_id", "status"]
    ordering_fields = ["slot_id", "status", "created_at"]
    pagination_class = None

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminRole()]
        return super().get_permissions()


class ParkingRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ParkingRecord.objects.select_related(
        "vehicle", "vehicle__child", "vehicle__child__guardian", "slot"
    ).prefetch_related("payments")
    serializer_class = ParkingRecordSerializer
    permission_classes = [IsAdminOrReadCreateStaff]
    lookup_field = "record_id"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["vehicle__vehicle_id", "slot__slot_id", "vehicle__child__child_id"]
    ordering_fields = ["record_id", "entry_time", "exit_time", "fee", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get("vehicle"):
            qs = qs.filter(vehicle_id=params["vehicle"])
        if params.get("slot"):
            qs = qs.filter(slot_id=params["slot"])
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("from"):
            qs = qs.filter(created_at__date__gte=params["from"])
        if params.get("to"):
            qs = qs.filter(created_at__date__lte=params["to"])
        return qs

    @action(detail=False, methods=["post"], url_path="entry")
    def entry(self, request):
        vehicle_id = request.data.get("vehicle_id")
        slot_id = request.data.get("slot_id")
        if not vehicle_id:
            raise ValidationError("vehicle_id is required.")
        try:
            vehicle = Vehicle.objects.select_related("child", "child__guardian").get(pk=vehicle_id)
        except Vehicle.DoesNotExist as exc:
            raise ValidationError(f"Vehicle {vehicle_id} is not registered.") from exc
        slot = None
        if slot_id:
            try:
                slot = ParkingSlot.objects.get(pk=slot_id)
            except ParkingSlot.DoesNotExist as exc:
                raise ValidationError(f"Slot {slot_id} does not exist.") from exc
        record = process_entry(vehicle, slot)
        return Response(ParkingRecordSerializer(record).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="park")
    def park(self, request):
        vehicle_id = request.data.get("vehicle_id")
        slot_id = request.data.get("slot_id")
        if not vehicle_id or not slot_id:
            raise ValidationError("vehicle_id and slot_id are required.")
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
            slot = ParkingSlot.objects.get(pk=slot_id)
        except Vehicle.DoesNotExist as exc:
            raise ValidationError(f"Vehicle {vehicle_id} is not registered.") from exc
        except ParkingSlot.DoesNotExist as exc:
            raise ValidationError(f"Slot {slot_id} does not exist.") from exc
        record = park_vehicle(vehicle, slot)
        return Response(ParkingRecordSerializer(record).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="exit")
    def exit_vehicle(self, request):
        vehicle_id = request.data.get("vehicle_id")
        if not vehicle_id:
            raise ValidationError("vehicle_id is required.")
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist as exc:
            raise ValidationError(f"Vehicle {vehicle_id} is not registered.") from exc
        record = process_exit(vehicle)
        return Response(ParkingRecordSerializer(record).data)

    @action(detail=False, methods=["get"], url_path="preview")
    def preview(self, request):
        vehicle_id = request.query_params.get("vehicle_id")
        if not vehicle_id:
            raise ValidationError("vehicle_id is required.")
        record = (
            ParkingRecord.objects.select_related("vehicle", "slot", "vehicle__child", "vehicle__child__guardian")
            .filter(vehicle_id=vehicle_id, status__in=["RESERVED", "ACTIVE"])
            .first()
        )
        if not record:
            raise ValidationError(f"No active parking record for {vehicle_id}.")
        duration, fee = preview_duration_and_fee(record)
        data = ParkingRecordSerializer(record).data
        data["live_duration_minutes"] = duration
        data["live_fee"] = fee
        return Response(data)


class ParkingSettingsView(APIView):
    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsAdminRole()]
        return [IsAdminOrReadCreateStaff()]

    def get(self, request):
        return Response(ParkingSettingsSerializer(ParkingSettings.get_solo()).data)

    def put(self, request):
        settings = ParkingSettings.get_solo()
        serializer = ParkingSettingsSerializer(settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        settings = ParkingSettings.get_solo()
        serializer = ParkingSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
