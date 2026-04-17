from io import StringIO

from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .jobs import JOB_REGISTRY, get_job, list_jobs, run_job
from .models import Job, PredefinedJob


class JobApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_predefined_jobs")

    def test_root_redirects_to_api_root(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], reverse("api-root"))

    def test_predefined_job_list_returns_dropdown_data(self):
        response = self.client.get(reverse("predefined-job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data[0]["code_name"], "division_by_zero")
        self.assertIn("name", response.data[0])
        self.assertIn("description", response.data[0])

    def test_job_list_returns_selected_predefined_job_details(self):
        predefined_job = PredefinedJob.objects.get(code_name="sort_small_array")
        Job.objects.create(predefined_job=predefined_job, state=Job.State.PENDING)

        response = self.client.get(reverse("job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["predefined_job"], "sort_small_array")
        self.assertEqual(response.data[0]["code_name"], "sort_small_array")
        self.assertEqual(response.data[0]["name"], "Sort Small Array")
        self.assertEqual(response.data[0]["state"], Job.State.PENDING)
        self.assertNotIn("status", response.data[0])
        self.assertNotIn("result", response.data[0])

    def test_job_create_uses_selected_predefined_job_and_state(self):
        response = self.client.post(
            reverse("job-list"),
            {
                "predefined_job": "find_primes_1_to_100",
                "state": Job.State.RUNNING,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["predefined_job"], "find_primes_1_to_100")
        self.assertEqual(response.data["name"], "Find Prime Numbers 1 to 100")
        self.assertEqual(
            response.data["description"],
            "Finds all prime numbers between 1 and 100 and returns them as an array.",
        )
        self.assertEqual(response.data["state"], Job.State.RUNNING)


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


class JobModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("sync_predefined_jobs")

    def test_job_uses_metadata_from_related_predefined_job(self):
        predefined_job = PredefinedJob.objects.get(code_name="sum_1_to_1000")
        job = Job.objects.create(predefined_job=predefined_job)

        self.assertEqual(job.predefined_job.code_name, "sum_1_to_1000")
        self.assertEqual(job.predefined_job.name, "Sum Numbers 1 to 1000")
        self.assertEqual(
            job.predefined_job.description,
            "Calculates the sum of integers from 1 to 1000.",
        )
        self.assertEqual(job.state, Job.State.PENDING)

    def test_job_requires_predefined_job_selection(self):
        job = Job(state=Job.State.PENDING)

        with self.assertRaisesMessage(ValidationError, "This field cannot be null"):
            job.full_clean()


class SyncPredefinedJobsCommandTests(TestCase):
    def test_command_creates_and_updates_predefined_jobs_from_registry(self):
        predefined_job = PredefinedJob.objects.get(code_name="sort_small_array")
        PredefinedJob.objects.filter(pk=predefined_job.pk).update(
            name="Old name",
            description="Old description",
        )
        out = StringIO()

        call_command("sync_predefined_jobs", stdout=out)

        self.assertEqual(PredefinedJob.objects.count(), 6)

        predefined_job.refresh_from_db()
        self.assertEqual(predefined_job.name, "Sort Small Array")
        self.assertEqual(
            predefined_job.description,
            "Sorts a short predefined array of integers and returns the sorted result.",
        )
        self.assertIn("6 total", out.getvalue())
