from rest_framework.routers import DefaultRouter

from .views import JobViewSet, PredefinedJobViewSet

router = DefaultRouter()
router.register("predefined-jobs", PredefinedJobViewSet, basename="predefined-job")
router.register("jobs", JobViewSet, basename="job")

urlpatterns = router.urls
