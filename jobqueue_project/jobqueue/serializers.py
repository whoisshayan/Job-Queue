from rest_framework import serializers

from .models import JobDefinition, JobExecution


class JobDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDefinition
        fields = ["id", "code_name", "name", "description"]
        read_only_fields = fields


class JobExecutionSerializer(serializers.ModelSerializer):
    job_definition = serializers.SlugRelatedField(
        slug_field="code_name",
        queryset=JobDefinition.objects.all(),
    )
    job_name_snapshot = serializers.CharField(read_only=True)
    job_description_snapshot = serializers.CharField(read_only=True)

    class Meta:
        model = JobExecution
        fields = [
            "id",
            "job_definition",
            "job_name_snapshot",
            "job_description_snapshot",
            "status",
            "result",
            "start_time",
            "end_time",
            "duration",
            "worker_id",
            "output_file_path",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "job_name_snapshot",
            "job_description_snapshot",
            "status",
            "result",
            "start_time",
            "end_time",
            "duration",
            "worker_id",
            "output_file_path",
            "created_at",
        ]
