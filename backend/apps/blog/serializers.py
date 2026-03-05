from rest_framework import serializers
from .models import Category, Blog, Comment


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug"]


class BlogListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = ["id", "title", "slug", "description", "img", "views", "category", "created_at"]


class BlogDetailSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)

    class Meta:
        model = Blog
        fields = ["id", "title", "slug", "description", "img", "views", "category", "created_at", "updated_at"]


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["text"]

    def validate_text(self, value):
        value = (value or "").strip()
        if len(value) < 2:
            raise serializers.ValidationError("Kommentariya juda qisqa.")
        return value