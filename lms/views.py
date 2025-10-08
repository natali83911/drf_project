from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsOwnerOrModeratorCanEditReadNoCreateDelete

from .models import Course, Lesson, Subscription
from .paginators import StandardPagination
from .serializers import CourseSerializer, LessonSerializer
from .tasks import send_course_update_email


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        permission_classes = [IsOwnerOrModeratorCanEditReadNoCreateDelete]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()
        send_course_update_email.delay(course.id)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        permission_classes = [IsOwnerOrModeratorCanEditReadNoCreateDelete]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.all()

    def get_permissions(self):
        permission_classes = [IsOwnerOrModeratorCanEditReadNoCreateDelete]
        return [permission() for permission in permission_classes]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return self.destroy(request, *args, **kwargs)


class SubscriptionToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)
        subscription_qs = Subscription.objects.filter(user=user, course=course)

        if subscription_qs.exists():
            subscription_qs.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "подписка добавлена"

        return Response({"message": message})
