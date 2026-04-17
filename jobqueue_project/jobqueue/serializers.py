from rest_framework import serializers

from .models import Job, PredefinedJob


class PredefinedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredefinedJob
        fields = ["id", "code_name", "name", "description"]
        read_only_fields = fields


class JobSerializer(serializers.ModelSerializer):
    predefined_job = serializers.SlugRelatedField(
        slug_field="code_name",
        queryset=PredefinedJob.objects.all(),
    )
    code_name = serializers.CharField(source="predefined_job.code_name", read_only=True)
    name = serializers.CharField(source="predefined_job.name", read_only=True)
    description = serializers.CharField(source="predefined_job.description", read_only=True)

    class Meta:
        model = Job
        fields = ["id", "predefined_job", "code_name", "name", "description", "state"]
        read_only_fields = ["id", "code_name", "name", "description"]
