from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Category, Blog, Comment
from .serializers import (
    CategoryListSerializer,
    BlogListSerializer,
    BlogDetailSerializer,
    CommentSerializer
)


class CategoryListAPIView(APIView):
    def get(self, request):
        qs = Category.objects.all().order_by("title", "id")
        ser = CategoryListSerializer(qs, many=True)
        return Response(ser.data)


class BlogListAPIView(APIView):
    """
    GET /api/blogs/?category=<slug yoki id>
    - category berilsa: shu category ga bog'langan bloglar
    - category berilmasa: barcha bloglar
    """
    def get(self, request):
        category_param = request.query_params.get("category")

        qs = Blog.objects.select_related("category").all().order_by("-created_at", "-id")

        if category_param:
            # category=slug bo'lishi ham, id bo'lishi ham mumkin
            if category_param.isdigit():
                qs = qs.filter(category_id=int(category_param))
            else:
                qs = qs.filter(category__slug=category_param)

        ser = BlogListSerializer(qs, many=True, context={"request": request})
        return Response(ser.data)


class BlogDetailAPIView(APIView):
    """
    GET /api/blogs/<slug>/
    (xohlasangiz id bilan ham qilsa bo'ladi)
    """
    def get(self, request, slug):
        blog = get_object_or_404(Blog.objects.select_related("category"), slug=slug)
        ser = BlogDetailSerializer(blog, context={"request": request})
        return Response(ser.data)


class BlogCommentsAPIView(APIView):
    """
    GET /api/blogs/<slug>/comments/
    Commentlar oxirgi yozilgani birinchi bo'lib chiqadi.
    """
    def get(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)

        comments = (
            Comment.objects
            .select_related("user")
            .filter(blog=blog)
            .order_by("-created_at", "-id")
        )

        ser = CommentSerializer(comments, many=True)
        return Response({
            "blog": {"id": blog.id, "title": blog.title, "slug": blog.slug},
            "count": comments.count(),
            "results": ser.data
        })