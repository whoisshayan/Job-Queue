from rest_framework import mixins, viewsets

from .models import JobDefinition, JobExecution
from .serializers import JobDefinitionSerializer, JobExecutionSerializer


class JobDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobDefinition.objects.order_by("name")
    serializer_class = JobDefinitionSerializer


class JobExecutionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = JobExecution.objects.select_related("job_definition").order_by("-created_at", "-id")
    serializer_class = JobExecutionSerializer
