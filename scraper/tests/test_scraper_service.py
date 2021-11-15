from datetime import timedelta

import marshmallow
from django.test import TestCase

from scraper import scraper_service
from scraper.models import ScraperResponse


class ScraperServiceIntegrationTests(TestCase):
    def test_returns_a_failed_response_on_http_client_failure(self):
        res = scraper_service.perform_request(url="http://10.0.0.1", regex=None)
        self.assertTrue(res.failed_request)
        self.assertEqual(res.url, "http://10.0.0.1")
        self.assertIsNone(res.regex)

    def test_returns_a_successful_response_with_no_regex(self):
        res = scraper_service.perform_request(url="http://httpbin.org/get", regex=None)
        self.assertFalse(res.failed_request)
        self.assertEqual(res.url, "http://httpbin.org/get")
        self.assertIsNone(res.regex)

    def test_returns_a_successful_response(self):
        res = scraper_service.perform_request(url="http://httpbin.org/get", regex=".*")
        self.assertFalse(res.failed_request)
        self.assertTrue(res.matches_regex)
        self.assertEqual(res.url, "http://httpbin.org/get")
        self.assertEqual(res.regex, ".*")


class RequestValidatorUnitTests(TestCase):
    def test_raise_validation_error_on_bad_regex_with_proper_message(self):
        dto_with_invalid_regex = {"url": "https://www.example.com", "regex": "["}

        self.assertRaisesMessage(
            marshmallow.exceptions.ValidationError,
            "Not a valid regular expression.",
            scraper_service.ScrapeRequestValidator().load,
            dto_with_invalid_regex,
        )

    def test_null_regex_field_causes_no_errors(self):
        dto = {"url": "https://www.example.com", "regex": None}

        self.assertEqual(dto, scraper_service.ScrapeRequestValidator().load(dto))

    def test_missing_regex_field_causes_no_errors_and_sets_regex_to_None(self):
        dto_with_missing_regex = {"url": "https://www.example.com"}
        validated_dto = scraper_service.ScrapeRequestValidator().load(
            dto_with_missing_regex
        )

        self.assertNotEqual(dto_with_missing_regex, validated_dto)
        self.assertTrue(validated_dto.get("regex") is None)

    def test_only_http_and_https_allowed_in_url_schema(self):
        dto_with_invalid_ftp_schema = {"url": "ftp://www.example.com"}
        dto_with_invalid_sftp_schema = {"url": "sftp://www.example.com"}
        dto_with_invalid_magnet_schema = {"url": "magnet://www.example.com"}

        self.assertRaisesMessage(
            marshmallow.exceptions.ValidationError,
            "Not a valid URL.",
            scraper_service.ScrapeRequestValidator().load,
            dto_with_invalid_ftp_schema,
        )
        self.assertRaisesMessage(
            marshmallow.exceptions.ValidationError,
            "Not a valid URL.",
            scraper_service.ScrapeRequestValidator().load,
            dto_with_invalid_sftp_schema,
        )
        self.assertRaisesMessage(
            marshmallow.exceptions.ValidationError,
            "Not a valid URL.",
            scraper_service.ScrapeRequestValidator().load,
            dto_with_invalid_magnet_schema,
        )

    def test_returns_a_list_of_messages_in_case_of_more_than_one_failure(self):
        invalid_dto = {"url": 32, "regex": "["}
        exception = None

        try:
            scraper_service.ScrapeRequestValidator().load(invalid_dto)
        except marshmallow.exceptions.ValidationError as e:
            exception = e

        self.assertEqual(
            exception.messages,
            {"url": ["Not a valid URL."], "regex": ["Not a valid regular expression."]},
        )

    def test_url_with_no_schema_is_a_validation_error(self):
        invalid_dto = {"url": "www.example.com"}
        self.assertRaisesMessage(
            marshmallow.exceptions.ValidationError,
            "Not a valid URL.",
            scraper_service.ScrapeRequestValidator().load,
            invalid_dto,
        )


class ResponseMapperUnitTests(TestCase):
    def test_maps_correctly_a_failed_request_without_regex(self):
        response_model = ScraperResponse.objects.create(
            url="https://www.e.it", failed_request=True
        )
        response_dict = scraper_service.map_scraper_response_to_dict(response_model)
        self.assertEqual(
            response_dict,
            {
                "failed_request": True,
                "url": "https://www.e.it",
                "uuid": response_model.uuid,
            },
        )

    def test_maps_correctly_a_failed_request_with_regex(self):
        response_model = ScraperResponse.objects.create(
            url="https://www.e.it", failed_request=True, regex=".*"
        )
        response_dict = scraper_service.map_scraper_response_to_dict(response_model)
        self.assertEqual(
            response_dict,
            {
                "failed_request": True,
                "regex": ".*",
                "url": "https://www.e.it",
                "uuid": response_model.uuid,
            },
        )

    def test_maps_correctly_a_successful_request_without_regex(self):
        response_model = ScraperResponse.objects.create(
            url="https://www.e.it", roundtrip=timedelta(seconds=0.1), status_code=200
        )
        response_dict = scraper_service.map_scraper_response_to_dict(response_model)
        self.assertEqual(
            response_dict,
            {
                "failed_request": False,
                "roundtrip": response_model.roundtrip,
                "status_code": 200,
                "url": "https://www.e.it",
                "uuid": response_model.uuid,
            },
        )

    def test_maps_correctly_a_successful_request_with_regex(self):
        response_model = ScraperResponse.objects.create(
            url="https://www.e.it",
            regex=".*",
            matches_regex=True,
            roundtrip=timedelta(seconds=0.1),
            status_code=200,
        )
        response_dict = scraper_service.map_scraper_response_to_dict(response_model)
        self.assertEqual(
            response_dict,
            {
                "failed_request": False,
                "matches_regex": True,
                "regex": ".*",
                "roundtrip": response_model.roundtrip,
                "status_code": 200,
                "url": "https://www.e.it",
                "uuid": response_model.uuid,
            },
        )
