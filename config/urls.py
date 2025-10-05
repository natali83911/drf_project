from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lms/", include("lms.urls", namespace="lms")),
    path("users/", include("users.urls", namespace="users")),
    # Генерация схемы OpenAPI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI с интерактивной документацией
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),

    # Альтернативно: Redoc UI
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
