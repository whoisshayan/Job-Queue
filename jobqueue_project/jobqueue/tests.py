from io import StringIO

from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .jobs import JOB_REGISTRY, get_job, list_jobs, run_job
from .models import JobDefinition, JobExecution


class JobExecutionApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_predefined_jobs")

    def test_root_redirects_to_api_root(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], reverse("api-root"))

    def test_job_definition_list_returns_catalog_data(self):
        response = self.client.get(reverse("job-definition-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data[0]["code_name"], "division_by_zero")
        self.assertIn("name", response.data[0])
        self.assertIn("description", response.data[0])

    def test_predefined_job_alias_returns_catalog_data(self):
        response = self.client.get(reverse("predefined-job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data[0]["code_name"], "division_by_zero")

    def test_job_list_returns_selected_job_definition_details(self):
        job_definition = JobDefinition.objects.get(code_name="sort_small_array")
        JobExecution.objects.create(job_definition=job_definition)

        response = self.client.get(reverse("job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["job_definition"], "sort_small_array")
        self.assertEqual(response.data[0]["job_name_snapshot"], "Sort Small Array")
        self.assertEqual(
            response.data[0]["job_description_snapshot"],
            "Sorts a short predefined array of integers and returns the sorted result.",
        )
        self.assertEqual(response.data[0]["status"], JobExecution.Status.PENDING)
        self.assertEqual(response.data[0]["result"], "")
        self.assertIsNone(response.data[0]["start_time"])
        self.assertIsNone(response.data[0]["end_time"])

    def test_job_create_defaults_status_to_pending(self):
        response = self.client.post(
            reverse("job-list"),
            {
                "job_definition": "find_primes_1_to_100",
                "job_name_snapshot": "Wrong name",
                "job_description_snapshot": "Wrong description",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["job_definition"], "find_primes_1_to_100")
        self.assertEqual(response.data["job_name_snapshot"], "Find Prime Numbers 1 to 100")
        self.assertEqual(
            response.data["job_description_snapshot"],
            "Finds all prime numbers between 1 and 100 and returns them as an array.",
        )
        self.assertEqual(response.data["status"], JobExecution.Status.PENDING)
        self.assertEqual(response.data["result"], "")
        self.assertIsNone(response.data["start_time"])
        self.assertIsNone(response.data["end_time"])
        self.assertIsNone(response.data["duration"])
        self.assertIsNone(response.data["worker_id"])
        self.assertIsNone(response.data["output_file_path"])
        self.assertIn("created_at", response.data)

    def test_job_retrieve_returns_execution_details(self):
        job_definition = JobDefinition.objects.get(code_name="sum_1_to_1000")
        execution = JobExecution.objects.create(job_definition=job_definition)

        response = self.client.get(reverse("job-detail", args=[execution.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["job_definition"], "sum_1_to_1000")
        self.assertEqual(response.data["job_name_snapshot"], "Sum Numbers 1 to 1000")
        self.assertEqual(response.data["status"], JobExecution.Status.PENDING)


class JobRegistryTests(SimpleTestCase):
    def test_registry_contains_all_expected_jobs(self):
        self.assertEqual(
            set(JOB_REGISTRY.keys()),
            {
                "print_1_to_100",
                "sort_small_array",
                "sum_1_to_1000",
                "find_primes_1_to_100",
                "division_by_zero",
                "infinite_loop",
            },
        )

    def test_get_job_returns_metadata(self):
        job = get_job("sum_1_to_1000")

        self.assertEqual(job.name, "Sum Numbers 1 to 1000")
        self.assertEqual(
            job.description,
            "Calculates the sum of integers from 1 to 1000.",
        )

    def test_run_job_executes_callable_by_code_name(self):
        self.assertEqual(run_job("sort_small_array"), [1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(run_job("sum_1_to_1000"), 500500)
        self.assertEqual(
            run_job("find_primes_1_to_100"),
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97],
        )

    def test_list_jobs_returns_all_job_definitions(self):
        self.assertEqual(len(list_jobs()), 6)

    def test_unknown_job_raises_helpful_error(self):
        with self.assertRaisesMessage(KeyError, "Unknown job code_name: missing_job"):
            get_job("missing_job")

    def test_error_job_raises_runtime_error(self):
        with self.assertRaises(ZeroDivisionError):
            run_job("division_by_zero")


class JobExecutionModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_predefined_jobs")

    def test_job_execution_uses_selected_job_definition(self):
        job_definition = JobDefinition.objects.get(code_name="sum_1_to_1000")
        execution = JobExecution.objects.create(job_definition=job_definition)

        self.assertEqual(execution.job_definition.code_name, "sum_1_to_1000")
        self.assertEqual(execution.job_name_snapshot, "Sum Numbers 1 to 1000")
        self.assertEqual(
            execution.job_description_snapshot,
            "Calculates the sum of integers from 1 to 1000.",
        )
        self.assertEqual(execution.job_definition.name, "Sum Numbers 1 to 1000")
        self.assertEqual(
            execution.job_definition.description,
            "Calculates the sum of integers from 1 to 1000.",
        )
        self.assertEqual(execution.status, JobExecution.Status.PENDING)
        self.assertEqual(execution.result, "")
        self.assertIsNone(execution.start_time)
        self.assertIsNone(execution.end_time)
        self.assertIsNone(execution.duration)
        self.assertIsNone(execution.worker_id)
        self.assertIsNone(execution.output_file_path)

    def test_job_execution_keeps_snapshot_after_job_definition_changes(self):
        job_definition = JobDefinition.objects.get(code_name="sort_small_array")
        execution = JobExecution.objects.create(job_definition=job_definition)

        job_definition.name = "Updated Sort Name"
        job_definition.description = "Updated description"
        job_definition.save()

        execution.refresh_from_db()
        self.assertEqual(execution.job_name_snapshot, "Sort Small Array")
        self.assertEqual(
            execution.job_description_snapshot,
            "Sorts a short predefined array of integers and returns the sorted result.",
        )

    def test_job_execution_requires_job_definition(self):
        execution = JobExecution()

        with self.assertRaisesMessage(ValidationError, "This field cannot be null"):
            execution.full_clean()


class SyncPredefinedJobsCommandTests(TestCase):
    def test_command_creates_and_updates_job_definitions_from_registry(self):
        call_command("sync_predefined_jobs")
        job_definition = JobDefinition.objects.get(code_name="sort_small_array")
        JobDefinition.objects.filter(pk=job_definition.pk).update(
            name="Old name",
            description="Old description",
        )
        out = StringIO()

        call_command("sync_predefined_jobs", stdout=out)

        self.assertEqual(JobDefinition.objects.count(), 6)

        job_definition.refresh_from_db()
        self.assertEqual(job_definition.name, "Sort Small Array")
        self.assertEqual(
            job_definition.description,
            "Sorts a short predefined array of integers and returns the sorted result.",
        )
        self.assertIn("Synced job definitions", out.getvalue())
