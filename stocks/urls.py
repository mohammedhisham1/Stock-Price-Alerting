from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import StockViewSet

router = SimpleRouter()
router.register(r'', StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
