from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"posts", views.PostViewSet)
router.register(r"comments", views.CommentViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
