from django.urls import path
from .views import (
    CategoryListAPIView,
    BlogListAPIView,
    BlogDetailAPIView,
    BlogCommentsAPIView,
    BlogCreateAPIView
)

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("blogs/", BlogListAPIView.as_view(), name="blog-list"),
    path("blog-create/", BlogCreateAPIView.as_view()),
    path("blogs/<slug:slug>/", BlogDetailAPIView.as_view(), name="blog-detail"),
    path("blogs/<slug:slug>/comments/", BlogCommentsAPIView.as_view(), name="blog-comments"),
]