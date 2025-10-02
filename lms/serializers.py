from rest_framework import serializers

from .models import Course, Lesson
from .validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    video_url = serializers.URLField(
        required=False, allow_blank=True, validators=[validate_youtube_link]
    )

    class Meta:
        model = Lesson
        fields = "__all__"

    def validate_video_url(self, value):
        """Валидация URL видео"""
        if value and not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                "URL должен начинаться с http:// или https://"
            )
        return value


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return obj.subscriptions.filter(user=user).exists()
