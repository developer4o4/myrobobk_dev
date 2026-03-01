from django.urls import path
from apps.courses.views import CourseListView, BuyCourseView, TopicDetailView
from apps.courses.views_submission import TopicSubmitView
from apps.courses.views_sections import CourseSectionsView, SectionTopicsView
urlpatterns = [
    path("courses/", CourseListView.as_view()),
    path("courses/buy/", BuyCourseView.as_view()),
    path("courses/<uuid:course_id>/sections/", CourseSectionsView.as_view()),
    path("sections/<uuid:section_id>/topics/", SectionTopicsView.as_view()),
    path("topics/<uuid:pk>/", TopicDetailView.as_view()),
    path("topics/<uuid:topic_id>/submit/", TopicSubmitView.as_view()),
]