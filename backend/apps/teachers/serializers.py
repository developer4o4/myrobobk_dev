from rest_framework import serializers
from .models import Teacher


class TeacherListSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "username",
            "job",
            "direction",
            "experience",
            "work_place",
            "img",
            "slug",
            "courses",
        ]

    def get_img(self, obj):
        request = self.context.get("request")
        if obj.img:
            if request:
                return request.build_absolute_uri(obj.img.url)
            return obj.img.url
        return None

    def get_courses(self, obj):
        # kurslarni minimal qilib qaytaramiz
        return [
            {"id": c.id, "title": c.title, "price": str(c.price)}
            for c in obj.courses.all()
        ]


class TeacherDetailSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "username",
            "job",
            "about",
            "direction",
            "experience",
            "work_place",
            "img",
            "slug",
            "courses",
            "created_at",
        ]

    def get_img(self, obj):
        request = self.context.get("request")
        if obj.img:
            if request:
                return request.build_absolute_uri(obj.img.url)
            return obj.img.url
        return None

    def get_courses(self, obj):
        return [
            {
                "id": c.id,
                "title": c.title,
                "about": c.about,
                "price": str(c.price),
                "image": self._abs_image(c),
            }
            for c in obj.courses.all()
        ]

    def _abs_image(self, course):
        request = self.context.get("request")
        if getattr(course, "image", None):
            if course.image:
                if request:
                    return request.build_absolute_uri(course.image.url)
                return course.image.url
        return None