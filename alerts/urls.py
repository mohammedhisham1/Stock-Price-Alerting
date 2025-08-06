from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, TriggeredAlertViewSet

router = DefaultRouter()
router.register(r'', AlertViewSet)
router.register(r'triggered', TriggeredAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
