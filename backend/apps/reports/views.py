from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.children.models import Child
from apps.guardians.models import Guardian
from apps.parking.models import ParkingRecord, ParkingSlot
from apps.payments.models import Payment
from apps.vehicles.models import Vehicle


class DashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        slots = ParkingSlot.objects.all()
        available = slots.filter(status=ParkingSlot.Status.AVAILABLE).count()
        occupied = slots.filter(status=ParkingSlot.Status.OCCUPIED).count()

        today_revenue = (
            Payment.objects.filter(
                payment_status=Payment.Status.COMPLETED, payment_time__date=today
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        vehicle_types = [
            {"name": row["vehicle_type"], "value": row["value"]}
            for row in Vehicle.objects.values("vehicle_type")
            .annotate(value=Count("vehicle_id"))
            .order_by("vehicle_type")
        ]

        daily = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            daily.append(
                {
                    "date": day.isoformat(),
                    "entries": ParkingRecord.objects.filter(entry_time__date=day).count(),
                    "exits": ParkingRecord.objects.filter(exit_time__date=day).count(),
                    "revenue": float(
                        Payment.objects.filter(
                            payment_status=Payment.Status.COMPLETED, payment_time__date=day
                        ).aggregate(total=Sum("amount"))["total"]
                        or 0
                    ),
                }
            )

        return Response(
            {
                "total_slots": slots.count(),
                "available_slots": available,
                "occupied_slots": occupied,
                "total_children": Child.objects.count(),
                "total_guardians": Guardian.objects.count(),
                "total_vehicles": Vehicle.objects.count(),
                "today_entries": ParkingRecord.objects.filter(entry_time__date=today).count(),
                "today_exits": ParkingRecord.objects.filter(exit_time__date=today).count(),
                "today_revenue": today_revenue,
                "occupancy": [
                    {"name": "Available", "value": available},
                    {"name": "Occupied", "value": occupied},
                ],
                "vehicle_types": vehicle_types,
                "daily": daily,
            }
        )


class SummaryReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = ParkingRecord.objects.all()
        return Response(
            {
                "total_records": records.count(),
                "active": records.filter(status=ParkingRecord.Status.ACTIVE).count(),
                "reserved": records.filter(status=ParkingRecord.Status.RESERVED).count(),
                "exited": records.filter(status=ParkingRecord.Status.EXITED).count(),
                "paid": records.filter(status=ParkingRecord.Status.PAID).count(),
                "total_revenue": Payment.objects.filter(
                    payment_status=Payment.Status.COMPLETED
                ).aggregate(total=Sum("amount"))["total"]
                or 0,
            }
        )
