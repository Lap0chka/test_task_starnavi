from . import views
from django.urls import path, include
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
