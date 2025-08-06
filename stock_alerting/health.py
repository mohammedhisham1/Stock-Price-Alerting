from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.db import connection
import redis
from django.conf import settings


@require_GET
def health_check(request):
    """Basic health check endpoint"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check Redis connection
        try:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            redis_status = "OK"
        except:
            redis_status = "ERROR"
        
        return JsonResponse({
            'status': 'OK',
            'timestamp': timezone.now().isoformat(),
            'database': 'OK',
            'redis': redis_status,
            'version': '1.0.0'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'ERROR',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
