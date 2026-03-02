from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Blog
from .serializers import BlogListSerializer


class BlogListAPIView(APIView):

    def get(self, request):

        blogs = Blog.objects.filter(is_active=True).order_by("-created_at")

        serializer = BlogListSerializer(
            blogs,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BlogDetailAPIView(APIView):

    def get(self, request, slug):

        blog = Blog.objects.get(slug=slug)

        blog.views += 1
        blog.save()

        serializer = BlogListSerializer(
            blog,
            context={"request": request}
        )

        return Response(serializer.data)