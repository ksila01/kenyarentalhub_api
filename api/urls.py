from rest_framework.routers import DefaultRouter
from .views import RentalPropertyViewSet

router = DefaultRouter()
router.register(r'rentals', RentalPropertyViewSet)

urlpatterns = router.urls