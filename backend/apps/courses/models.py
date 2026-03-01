from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from apps.common.models import BaseModel
User = settings.AUTH_USER_MODEL


class Course(BaseModel):
    title = models.CharField(max_length=255)
    about = models.TextField(blank=True)
    image = models.ImageField(upload_to="courses/images/", blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Section(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("course", "order")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.course_id} - {self.title}"


class Topic(BaseModel):
    TYPE_CHOICES = (
        ("content", "Content"),
        ("code", "Code"),
    )

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=255)
    about = models.TextField(blank=True)
    video_url = models.CharField(max_length=500,blank=True, null=True)
    topic_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="content")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("section", "order")
        ordering = ["order", "id"]

    @property
    def is_code(self) -> bool:
        return self.topic_type == "code"

    def __str__(self):
        return self.title


# ===== CODE PART =====

class Problem(BaseModel):
    """Faqat Topic.topic_type = code bo'lganda ishlatiladi."""
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name="problem")
    title = models.CharField(max_length=255)
    statement = models.TextField()  # masala matni

    # ko'rsatma uchun (public)
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)

    def __str__(self):
        return self.title


class TestCase(BaseModel):
    """Hidden testlar ham shu yerda."""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="tests")
    input_data = models.TextField()
    output_data = models.TextField()
    is_hidden = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.problem_id} test#{self.id}"


class Submission(BaseModel):
    LANG_CHOICES = (
        ("py", "Python"),
        ("c", "C"),
        ("cpp", "C++"),
    )
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("error", "Error"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")

    language = models.CharField(max_length=10, choices=LANG_CHOICES)
    source_code = models.TextField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} -> {self.problem_id} ({self.status})"


# ===== SUBSCRIPTION =====

def add_one_month(dt):
    """
    'olgan sanadan keyingi oyning o'sha kunigacha'
    Agar keyingi oyda o'sha kun bo'lmasa (masalan 31), oxirgi kuniga tushadi.
    """
    from calendar import monthrange

    year = dt.year
    month = dt.month + 1
    if month == 13:
        month = 1
        year += 1
    day = min(dt.day, monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


class CourseSubscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_subscriptions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subscriptions")

    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    active = models.BooleanField(default=True)

    last_billed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "course")
        indexes = [
            models.Index(fields=["user", "course"]),
            models.Index(fields=["expires_at", "active"]),
        ]

    def __str__(self):
        return f"{self.user_id}-{self.course_id} active={self.active}"

    def is_valid(self) -> bool:
        return self.active and timezone.now() < self.expires_at

    @classmethod
    def start_or_renew(cls, user, course):
        """
        Sotib olish:
        - user.balance >= course.price bo'lsa yechadi
        - subscription create/renew qiladi (1 oy)
        """
        from django.apps import apps
        UserModel = apps.get_model(*User.split(".")) if "." in User else apps.get_model("users", "User")

        with transaction.atomic():
            u = UserModel.objects.select_for_update().get(pk=user.pk)
            price = Decimal(course.price)

            if u.balance < price:
                raise ValueError("Balans yetarli emas")

            u.balance -= price
            u.save(update_fields=["balance"])

            sub, created = cls.objects.select_for_update().get_or_create(
                user=u, course=course,
                defaults={
                    "started_at": timezone.now(),
                    "expires_at": add_one_month(timezone.now()),
                    "active": True,
                    "last_billed_at": timezone.now(),
                }
            )

            if not created:
                now = timezone.now()
                # agar oldin yopilgan bo'lsa ham, to'lov bo'lgach ochamiz
                sub.active = True
                # agar muddati o'tib ketgan bo'lsa, hozirdan 1 oy
                base = now if sub.expires_at <= now else sub.expires_at
                sub.expires_at = add_one_month(base)
                sub.last_billed_at = now
                sub.save(update_fields=["active", "expires_at", "last_billed_at"])

            return sub