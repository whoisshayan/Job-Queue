from django.urls import reverse
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .jobs import JOB_REGISTRY, get_job, list_jobs, run_job
from .models import Job


class JobApiTests(APITestCase):
    def test_root_redirects_to_api_root(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], reverse("api-root"))

    def test_job_list_returns_state_field(self):
        Job.objects.create(
            name="Email users",
            description="Send the digest email.",
            state=Job.State.PENDING,
        )

        response = self.client.get(reverse("job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["state"], Job.State.PENDING)
        self.assertNotIn("status", response.data[0])
        self.assertNotIn("result", response.data[0])


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
