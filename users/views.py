from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]
