from rest_framework import generics, permissions, viewsets


from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            if self.request.user.groups.filter(name='moderators').exists():
                self.permission_denied(self.request, message="Модераторам запрещено создавать курсы")
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            if self.request.user.groups.filter(name="moderators").exists():
                self.permission_denied(
                    self.request, message="Модераторам запрещено создавать уроки"
                )
            permission_classes = [permissions.IsAuthenticated]
        elif self.request.method == "GET":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        elif self.request.method == 'GET':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj
