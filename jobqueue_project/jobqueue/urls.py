from rest_framework.routers import DefaultRouter

from .views import JobDefinitionViewSet, JobExecutionViewSet

router = DefaultRouter()
router.register("predefined-jobs", JobDefinitionViewSet, basename="predefined-job")
router.register("job-definitions", JobDefinitionViewSet, basename="job-definition")
router.register("jobs", JobExecutionViewSet, basename="job")

urlpatterns = router.urls
