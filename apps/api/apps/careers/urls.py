from django.urls import path

from . import views

urlpatterns = [
    path("careers/openings/", views.JobOpeningListView.as_view(), name="opening-list"),
    path(
        "careers/applications/",
        views.JobApplicationCreateView.as_view(),
        name="application-create",
    ),
]
