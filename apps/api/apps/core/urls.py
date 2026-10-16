from django.urls import path

from . import views

urlpatterns = [
    path("site/", views.SiteSettingsView.as_view(), name="site-settings"),
    path("testimonials/", views.TestimonialListView.as_view(), name="testimonial-list"),
    path("team/", views.TeamMemberListView.as_view(), name="team-list"),
    path("health/", views.HealthView.as_view(), name="health"),
]
