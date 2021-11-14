from django.test import TestCase

from scraper.models import ScraperResponse


class ScraperResponseUnitTests(TestCase):
    def test_string_dunder_signals_when_request_is_successful(self):
        scraped_response_str = str(
            ScraperResponse.objects.create(url="https://www.example.com")
        )
        self.assertTrue(
            scraped_response_str.startswith("https://www.example.com - Scraped")
        )

    def test_string_dunder_signals_when_request_has_failed(self):
        failed_response_str = str(
            ScraperResponse.objects.create(
                url="https://www.example.com", has_request_failed=True
            )
        )
        self.assertTrue(
            failed_response_str.startswith("https://www.example.com - Failed")
        )
