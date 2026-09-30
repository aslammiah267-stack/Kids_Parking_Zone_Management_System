from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.users.permissions import IsAdminOrReadCreateStaff
from apps.vehicles.models import Vehicle
from apps.parking.models import ParkingRecord
from .models import Payment
from .serializers import PaymentSerializer
from .services import collect_payment


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("vehicle", "parking_record")
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrReadCreateStaff]
    lookup_field = "payment_id"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["vehicle__vehicle_id", "parking_record__record_id"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(payment_status=status_filter)
        return qs

    def create(self, request, *args, **kwargs):
        vehicle_id = request.data.get("vehicle_id") or request.data.get("vehicle")
        record_id = request.data.get("parking_record")
        if not vehicle_id:
            raise ValidationError("vehicle_id is required.")
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist as exc:
            raise ValidationError(f"Vehicle {vehicle_id} is not registered.") from exc
        record = None
        if record_id:
            try:
                record = ParkingRecord.objects.get(pk=record_id)
            except ParkingRecord.DoesNotExist as exc:
                raise ValidationError("Parking record not found.") from exc
        payment = collect_payment(vehicle, record)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="complete")
    def complete(self, request, payment_id=None):
        payment = self.get_object()
        if payment.payment_status == Payment.Status.COMPLETED:
            raise ValidationError("Payment is already completed.")
        payment.payment_status = Payment.Status.COMPLETED
        payment.save(update_fields=["payment_status"])
        payment.parking_record.status = ParkingRecord.Status.PAID
        payment.parking_record.save(update_fields=["status"])
        return Response(PaymentSerializer(payment).data)
