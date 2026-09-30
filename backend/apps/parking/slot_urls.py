from rest_framework.routers import DefaultRouter

from .views import ParkingSlotViewSet

router = DefaultRouter()
router.register("", ParkingSlotViewSet, basename="parking-slot")
urlpatterns = router.urls
