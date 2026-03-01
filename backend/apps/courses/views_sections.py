from rest_framework.generics import ListAPIView
from rest_framework import permissions
from django.shortcuts import get_object_or_404

from apps.courses.models import Course, Section, Topic
from apps.courses.serializers_sections import SectionSerializer, TopicMiniSerializer


class CourseSectionsView(ListAPIView):
    """
    GET /api/courses/<course_id>/sections/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SectionSerializer

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs["course_id"], is_active=True)
        return Section.objects.filter(course=course).order_by("order", "id")


class SectionTopicsView(ListAPIView):
    """
    GET /api/sections/<section_id>/topics/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = TopicMiniSerializer

    def get_queryset(self):
        section = get_object_or_404(Section, id=self.kwargs["section_id"])
        return Topic.objects.filter(section=section).order_by("order", "id")