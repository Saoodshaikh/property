from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewset

# Initialize the DefaultRouter
router = DefaultRouter()
router.register(r'users', CustomUserViewset, basename='user')

# Define the urlpatterns to include the router URLs
urlpatterns = [
    path('', include(router.urls)),
]
