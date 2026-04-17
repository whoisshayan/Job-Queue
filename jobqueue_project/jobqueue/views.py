from rest_framework import viewsets

from .models import Job, PredefinedJob
from .serializers import JobSerializer, PredefinedJobSerializer


class PredefinedJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredefinedJob.objects.order_by("name")
    serializer_class = PredefinedJobSerializer


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("predefined_job").order_by("id")
    serializer_class = JobSerializer
