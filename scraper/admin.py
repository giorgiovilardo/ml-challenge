from django.contrib import admin

from .models import ScraperResponse


class ScraperResponseAdmin(admin.ModelAdmin):
    list_display = ("url", "uuid", "failed_request")
    readonly_fields = ["uuid"]


admin.site.register(ScraperResponse, ScraperResponseAdmin)
