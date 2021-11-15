from django.urls import path

from . import views

urlpatterns = [
    path("", views.scrape_url, name="scrape"),
]
