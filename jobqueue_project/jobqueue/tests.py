from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
