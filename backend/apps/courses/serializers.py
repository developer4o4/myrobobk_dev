from rest_framework import serializers
from apps.courses.models import Course, Section, Topic, CourseSubscription, Problem, TestCase


class CourseSerializer(serializers.ModelSerializer):
    buyers_total = serializers.IntegerField(read_only=True)
    buyers_active = serializers.IntegerField(read_only=True)
    sections_count = serializers.IntegerField(read_only=True)
    topics_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Course
        fields = (
            "id", "title", "about", "image", "price", "is_active",
            "buyers_total", "buyers_active",
            "sections_count", "topics_count","is_bought"
        )
class TopicSerializer(serializers.ModelSerializer):
    is_code = serializers.BooleanField(read_only=True)

    class Meta:
        model = Topic
        fields = ("id", "title", "about", "video_url", "topic_type", "is_code", "order")

class BuyCourseSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()

class MyCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "about", "image", "price"]