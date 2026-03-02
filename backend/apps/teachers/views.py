from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Teacher
from .serializers import TeacherListSerializer, TeacherDetailSerializer


class TeachersListAPIView(APIView):
    def get(self, request):
        qs = Teacher.objects.filter(is_active=True).prefetch_related("courses").order_by("-created_at")
        serializer = TeacherListSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherDetailAPIView(APIView):
    def get(self, request, slug):
        teacher = get_object_or_404(
            Teacher.objects.filter(is_active=True).prefetch_related("courses"),
            slug=slug,
        )
        serializer = TeacherDetailSerializer(teacher, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)