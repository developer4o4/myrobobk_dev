from django.urls import path
from .views import *

urlpatterns = [
    path("blogs/", BlogListAPIView.as_view()),
    path("blogs/<slug:slug>/", BlogDetailAPIView.as_view()),
]