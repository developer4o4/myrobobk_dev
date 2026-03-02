from rest_framework import serializers
from apps.courses.models import Course, Section, Topic, CourseSubscription, Problem, TestCase


class CourseSerializer(serializers.ModelSerializer):
    buyers_total = serializers.IntegerField(read_only=True)
    buyers_active = serializers.IntegerField(read_only=True)
    sections_count = serializers.IntegerField(read_only=True)
    topics_count = serializers.IntegerField(read_only=True)
    is_bought = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id", "title", "about", "image", "price", "is_active",
            "buyers_total", "buyers_active",
            "sections_count", "topics_count",
            "is_bought",
        )

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = (
            "title",
            "statement",
            "sample_input",
            "sample_output",
        )
class TopicSerializer(serializers.ModelSerializer):
    is_code = serializers.BooleanField(read_only=True)

    problem = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = (
            "id",
            "title",
            "about",
            "video_url",
            "topic_type",
            "is_code",
            "order",
            "problem",
        )

    def get_problem(self, obj):
        if obj.topic_type == "code" and hasattr(obj, "problem"):
            return ProblemSerializer(obj.problem).data
        return None
class BuyCourseSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()

class MyCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "about", "image", "price"]