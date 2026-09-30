from rest_framework.routers import DefaultRouter

from .views import ParkingRecordViewSet

router = DefaultRouter()
router.register("", ParkingRecordViewSet, basename="parking-record")
urlpatterns = router.urls
