from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course, Payment
from .permissions import IsOwnerOrModeratorCanEditReadNoCreateDelete
from .serializers import PaymentSerializer, RegisterSerializer, UserSerializer
from .services import (convert_usd_to_rub, create_checkout_session,
                       create_stripe_price, create_stripe_product)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrModeratorCanEditReadNoCreateDelete,
    ]


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    # def perform_create(self, serializer):
    #     user = serializer.save(is_active=True)
    #     user.set_password(user.password)
    #     user.save()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="create-payment",
    )
    def create_payment(self, request):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        product = create_stripe_product(
            name=course.title, description=course.description
        )
        unit_amount = convert_usd_to_rub(course.price)
        price = create_stripe_price(product_id=product.id, unit_amount=unit_amount)

        success_url = request.build_absolute_uri("/")
        cancel_url = request.build_absolute_uri("/")

        session = create_checkout_session(
            price_id=price.id, success_url=success_url, cancel_url=cancel_url
        )

        payment = Payment.objects.create(
            user=request.user,
            paid_course=course,
            stripe_product_id=product.id,
            stripe_price_id=price.id,
            stripe_checkout_session_id=session.id,
            payment_url=session.url,
            amount=unit_amount,
        )

        return Response(
            {"payment_url": session.url, "payment_id": payment.id},
            status=status.HTTP_201_CREATED,
        )
