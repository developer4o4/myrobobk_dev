from rest_framework.permissions import BasePermission
from django.utils import timezone
from apps.courses.models import CourseSubscription, Topic

class HasActiveCourseSubscription(BasePermission):
    message = "Kurs yopiq. To'lov qiling."

    def has_object_permission(self, request, view, obj):
        # obj Topic yoki Course bo'lishi mumkin
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if hasattr(obj, "course"):
            course = obj.course
        elif isinstance(obj, Topic):
            course = obj.section.course
        else:
            course = obj

        sub = CourseSubscription.objects.filter(user=user, course=course, active=True).first()
        if not sub:
            return False
        return timezone.now() < sub.expires_at