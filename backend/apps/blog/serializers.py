from rest_framework import serializers
from .models import Blog


class BlogListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = [
            "title",
            "description",
            "img",
            "slug",
            "views",
            "created_at",
        ]