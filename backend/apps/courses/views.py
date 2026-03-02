from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from django.db.models import Count, Q, Exists, OuterRef, Value, BooleanField
from django.utils import timezone
from apps.courses.models import Course, Topic, CourseSubscription
from apps.courses.serializers import CourseSerializer, TopicSerializer, BuyCourseSerializer, MyCourseSerializer
from apps.courses.permissions import HasActiveCourseSubscription

class CourseListView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()

        qs = (
            Course.objects
            .filter(is_active=True)
            .annotate(
                # Kursni hech bo‘lmaganda 1 marta sotib olgan userlar soni
                buyers_total=Count("subscriptions__user", distinct=True),

                # Hozir aktiv userlar soni
                buyers_active=Count(
                    "subscriptions__user",
                    filter=Q(subscriptions__active=True, subscriptions__expires_at__gt=now),
                    distinct=True
                ),

                # Bo‘limlar soni
                sections_count=Count("sections", distinct=True),

                # Mavzular soni
                topics_count=Count("sections__topics", distinct=True),
            )
            .order_by("-created_at")
        )

        # ✅ request.user bo‘yicha is_bought
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            active_sub_qs = CourseSubscription.objects.filter(
                user=user,
                course=OuterRef("pk"),
                active=True,
                expires_at__gt=now,
            )
            qs = qs.annotate(is_bought=Exists(active_sub_qs))
        else:
            qs = qs.annotate(is_bought=Value(False, output_field=BooleanField()))

        return qs

class BuyCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        s = BuyCourseSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        course = get_object_or_404(Course, id=s.validated_data["course_id"], is_active=True)

        try:
            sub = CourseSubscription.start_or_renew(request.user, course)
        except ValueError:
            # 402 ishlatsa ham bo‘ladi, lekin ko‘p API’lar 400/403 qaytaradi
            return Response(
                {"detail": "Balans yetarli emas."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "ok": True,
                "course_id": str(course.id),
                "expires_at": sub.expires_at,
                "active": sub.active,
            },
            status=status.HTTP_200_OK
        )


class TopicDetailView(RetrieveAPIView):
    queryset = Topic.objects.select_related("section__course")
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveCourseSubscription]


class MyPurchasedCoursesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subs = (
            CourseSubscription.objects
            .filter(user=request.user, active=True, expires_at__gt=timezone.now())
            .select_related("course")
            .order_by("-expires_at")
        )
        courses = [s.course for s in subs]
        data = MyCourseSerializer(courses, many=True, context={"request": request}).data
        return Response(data)