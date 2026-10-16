from django.urls import path

from . import views

urlpatterns = [path("gallery/", views.GalleryImageListView.as_view(), name="gallery-list")]
