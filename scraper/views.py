import marshmallow
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import scraper_service


@api_view(["POST"])
def scrape_url(request):
    unvalidated_url = request.data.get("url", "")
    unvalidated_regex = request.data.get("regex", None)

    try:
        scraper_response = scraper_service.perform_request(
            url=unvalidated_url, regex=unvalidated_regex
        )
    except marshmallow.ValidationError as e:
        return Response(
            {"validation_errors": e.messages}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        scraper_service.map_scraper_response_to_dict(scraper_response),
        status=status.HTTP_201_CREATED,
    )
