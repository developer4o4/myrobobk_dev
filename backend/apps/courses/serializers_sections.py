from rest_framework import serializers
from apps.courses.models import Section, Topic


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ("id", "title", "order")


class TopicMiniSerializer(serializers.ModelSerializer):
    is_code = serializers.BooleanField(read_only=True)

    class Meta:
        model = Topic
        fields = ("id", "title", "topic_type", "is_code", "order")