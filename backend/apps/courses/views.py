from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from apps.courses.models import Course, Topic, CourseSubscription
from apps.courses.serializers import CourseSerializer, TopicSerializer, BuyCourseSerializer
from apps.courses.permissions import HasActiveCourseSubscription
class CourseListView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()

        return (
            Course.objects
            .filter(is_active=True)
            .annotate(
                # Kursni hech bo'lmaganda 1 marta sotib olgan userlar soni
                buyers_total=Count("subscriptions__user", distinct=True),

                # Hozir aktiv userlar soni
                buyers_active=Count(
                    "subscriptions__user",
                    filter=Q(subscriptions__active=True, subscriptions__expires_at__gt=now),
                    distinct=True
                ),

                # Bo'limlar soni
                sections_count=Count("sections", distinct=True),

                # Mavzular soni (Course -> Section -> Topic)
                topics_count=Count("sections__topics", distinct=True),
            )
            .order_by("-created_at")
        )

class BuyCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = BuyCourseSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        course = get_object_or_404(Course, id=s.validated_data["course_id"], is_active=True)

        try:
            sub = CourseSubscription.start_or_renew(request.user, course)
        except ValueError:
            return Response({"detail": "Balans yetarli emas."}, status=402)

        return Response({
            "ok": True,
            "course_id": course.id,
            "expires_at": sub.expires_at,
            "active": sub.active
        })


class TopicDetailView(RetrieveAPIView):
    queryset = Topic.objects.select_related("section__course")
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveCourseSubscription]