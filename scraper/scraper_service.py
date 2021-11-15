from __future__ import annotations

import re

import requests
from marshmallow import Schema, ValidationError, fields, validates

from scraper.models import ScraperResponse


class ScrapeRequestValidator(Schema):
    url = fields.URL(required=True, schemes=("http", "https"))
    regex = fields.String(load_default=None, required=False)

    @validates("regex")
    def validate_regex(self, regex):
        if regex:
            try:
                re.compile(regex)
            except re.error:
                raise ValidationError("Not a valid regular expression.")


def perform_request(*, url: str, regex: str | None) -> ScraperResponse:
    dto = {"url": url, "regex": regex}

    ScrapeRequestValidator().load(dto)

    try:
        res = requests.get(url, timeout=5)
    except:
        return ScraperResponse.objects.create(url=url, regex=regex, failed_request=True)

    return ScraperResponse.objects.create(
        url=url,
        regex=regex,
        roundtrip=res.elapsed,
        status_code=res.status_code,
        matches_regex=_check_if_regex_matches_content(regex=regex, content=res.text),
    )


def _check_if_regex_matches_content(*, regex: str, content: str):
    if regex is not None:
        return True if re.match(regex, content) else False
    return None


def map_scraper_response_to_dict(scraper_response: ScraperResponse):
    return {
        k: v
        for k, v in scraper_response.__dict__.items()
        if v is not None
        and k
        in [
            "url",
            "regex",
            "uuid",
            "failed_request",
            "roundtrip",
            "status_code",
            "matches_regex",
        ]
    }
