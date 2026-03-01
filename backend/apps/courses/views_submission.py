from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.courses.models import Topic, Problem, Submission
from apps.courses.permissions import HasActiveCourseSubscription
from apps.courses.serializers_submission import SubmitCodeSerializer
from apps.courses.judge.evaluate import evaluate


class TopicSubmitView(APIView):
    """
    POST /api/topics/<uuid:topic_id>/submit/
    Body: {language: "py|c|cpp", source_code: "..."}
    """
    permission_classes = [permissions.IsAuthenticated, HasActiveCourseSubscription]

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic.objects.select_related("section__course"), id=topic_id)

        # subscription check shu topic->course bo'yicha ishlashi uchun:
        self.check_object_permissions(request, topic)

        if topic.topic_type != "code":
            return Response({"detail": "Bu mavzu code emas."}, status=400)

        problem = getattr(topic, "problem", None)
        if problem is None:
            # agar Problem OneToOne bo'lsa: topic.problem bo'ladi
            # ba'zan DoesNotExist bo'lishi mumkin:
            try:
                problem = Problem.objects.get(topic=topic)
            except Problem.DoesNotExist:
                return Response({"detail": "Problem topilmadi."}, status=400)

        s = SubmitCodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        language = s.validated_data["language"]
        source_code = s.validated_data["source_code"]
        source_code = source_code.encode().decode("unicode_escape")
        # DB ga submission yozamiz (history uchun)
        sub = Submission.objects.create(
            user=request.user,
            problem=problem,
            language=language,
            source_code=source_code,
            status="pending",
        )

        status, err = evaluate(problem, language, source_code)

        sub.status = status
        sub.error_message = err
        sub.save(update_fields=["status", "error_message"])

        resp = {
            "submission_id": str(sub.id),
            "status": status,                 # accepted|rejected|error
            "error_message": err,
        }
        return Response(resp, status=200)