from django.urls import include, path

from hello import views

urlpatterns = [
    path("", views.home, name="home"),
    path("docs/", views.docs, name="docs"),
    path("map/", views.map_view, name="map_view"),
    path("cannons/", views.cannon_list, name="cannon_list"),
    path("cannons/<slug:slug>/", views.cannon_detail, name="cannon_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("upload/", views.upload_cannon, name="upload_cannon"),
    path("upload/photo/", views.upload_photo, name="upload_photo"),
    path("cannons/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("profile/", views.profile, name="profile"),
    path("photos/<int:photo_id>/image/", views.photo_image, name="photo_image"),
    path("profiles/<int:profile_id>/image/", views.profile_image, name="profile_image"),
    path("signup/", views.signup, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]
