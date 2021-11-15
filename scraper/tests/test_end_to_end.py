from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class EndToEndTests(APITestCase):
    def test_non_reachable_url_timeouts_and_fails(self):
        res = APIClient().post("/", data={"url": "http://10.0.0.1"}, format="json")

        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        self.assertTrue(res.data.get("failed_request"))
        self.assertEqual("http://10.0.0.1", res.data.get("url"))

    def test_good_url_with_no_regex_works(self):
        res = APIClient().post(
            "/", data={"url": "http://httpbin.org/get"}, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        self.assertFalse(res.data.get("failed_request"))
        self.assertEqual("http://httpbin.org/get", res.data.get("url"))

    def test_good_url_with_regex_works(self):
        res = APIClient().post(
            "/", data={"url": "http://httpbin.org/get", "regex": ".*"}, format="json"
        )

        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        self.assertFalse(res.data.get("failed_request"))
        self.assertTrue(res.data.get("matches_regex"))
        self.assertEqual("http://httpbin.org/get", res.data.get("url"))

    def test_url_with_no_schema_outputs_400_with_validation_errors(self):
        res = APIClient().post("/", data={"url": "httpbin.org/get"}, format="json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        self.assertEqual(
            {"url": ["Not a valid URL."]}, res.data.get("validation_errors")
        )

    def test_url_with_wrong_schema_outputs_400_with_validation_errors(self):
        res = APIClient().post(
            "/", data={"url": "ftp://httpbin.org/get"}, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        self.assertEqual(
            {"url": ["Not a valid URL."]}, res.data.get("validation_errors")
        )

    def test_url_with_bad_regex_outputs_400_with_validation_errors(self):
        res = APIClient().post(
            "/", data={"url": "http://httpbin.org/get", "regex": "["}, format="json"
        )

        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)
        self.assertEqual(
            {"regex": ["Not a valid regular expression."]},
            res.data.get("validation_errors"),
        )

    def test_matches_text_inside_the_body(self):
        res = APIClient().post(
            "/",
            data={"url": "http://httpbin.org/get", "regex": '"X-Amzn-Trace-Id"'},
            format="json",
        )
        print(res.data)
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
