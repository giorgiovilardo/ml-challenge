import uuid

from django.db import models


class ScraperResponse(models.Model):
    url = models.URLField()
    regex = models.CharField(max_length=200, null=True, blank=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    has_request_failed = models.BooleanField(default=False)
    roundtrip = models.DurationField(blank=True, null=True)
    status_code = models.IntegerField(blank=True, null=True)
    matches_regex = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.url} - {'Failed Request' if self.has_request_failed else 'Scraped'} - {self.uuid}"
