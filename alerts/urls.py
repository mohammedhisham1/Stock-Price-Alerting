from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, TriggeredAlertViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'triggered-alerts', TriggeredAlertViewSet, basename='triggered-alert')

urlpatterns = [
    path('', include(router.urls)),
]
