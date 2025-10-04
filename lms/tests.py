from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTest(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.user_owner = User.objects.create_user(
            email="owner@example.com", password="pass"
        )
        self.user_other = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        self.user_moderator = User.objects.create_user(
            email="moderator@example.com", password="pass"
        )
        # присваиваем группу модераторов
        mod_group = Group.objects.get_or_create(name="moderators")[0]
        self.user_moderator.groups.add(mod_group)

        # Создаем курс
        self.course = Course.objects.create(
            title="Test Course", description="Desc", owner=self.user_owner
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Test Lesson",
            description="Desc",
            owner=self.user_owner,
        )

        self.url_list = reverse(
            "lms:lesson-list-create"
        )  # URL для списка и создания уроков
        self.url_detail = reverse("lms:lesson-detail", kwargs={"pk": self.lesson.pk})

    def test_lesson_list_authenticated(self):
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_create_owner_forbidden_for_moderator(self):
        self.client.force_authenticate(user=self.user_moderator)
        data = {
            "course": self.course.id,
            "title": "New Lesson",
            "description": "Description",
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_create_owner_success(self):
        self.client.force_authenticate(user=self.user_owner)
        data = {
            "course": self.course.id,
            "title": "New Lesson",
            "description": "Description",
        }
        response = self.client.post(self.url_list, data)
        if response.status_code != status.HTTP_201_CREATED:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_update_owner_and_moderator(self):
        # Обновление урока владельцем
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.patch(self.url_detail, {"title": "Updated Title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Title")

        # Обновление урока модератором
        self.client.force_authenticate(user=self.user_moderator)
        response = self.client.patch(self.url_detail, {"title": "Moderator Update"})
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        )

    def test_lesson_delete_owner_and_forbidden_for_other(self):
        # Удаление владельцем
        self.client.force_authenticate(user=self.user_owner)
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Удаление посторонним (не владельцем)
        self.lesson = Lesson.objects.create(
            course=self.course, title="Test2", description="Desc", owner=self.user_owner
        )
        self.client.force_authenticate(user=self.user_other)
        url = reverse("lms:lesson-detail", kwargs={"pk": self.lesson.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="user1@example.com", password="pass")
        self.course = Course.objects.create(
            title="Course 1", description="Desc", owner=self.user
        )
        self.url = reverse("lms:subscription-toggle")

    def test_add_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_remove_subscription(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_requires_course_id(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
