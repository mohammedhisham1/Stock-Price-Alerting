from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import logging

from .models import Alert, TriggeredAlert, NotificationTemplate
from .serializers import (
    AlertSerializer, 
    AlertCreateSerializer, 
    TriggeredAlertSerializer,
    NotificationTemplateSerializer
)
from .tasks import evaluate_alert, send_alert_notification

logger = logging.getLogger(__name__)


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user alerts"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AlertCreateSerializer
        return AlertSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new alert"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                alert = serializer.save()
                
                # Return full alert data
                response_serializer = AlertSerializer(alert)
                
                logger.info(f"Alert created: {alert}")
                
                return Response({
                    'success': True,
                    'message': 'Alert created successfully',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return Response({
                'success': False,
                'error': 'Failed to create alert'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """List user's alerts"""
        try:
            queryset = self.get_queryset()
            
            # Filter by active status
            is_active = request.query_params.get('is_active')
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
            # Filter by stock symbol
            stock_symbol = request.query_params.get('stock_symbol')
            if stock_symbol:
                queryset = queryset.filter(stock__symbol__icontains=stock_symbol)
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    'success': True,
                    'data': serializer.data
                })
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'count': queryset.count(),
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error listing alerts: {e}")
            return Response({
                'success': False,
                'error': 'Failed to fetch alerts'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an alert"""
        try:
            instance = self.get_object()
            instance.delete()
            
            logger.info(f"Alert deleted: {instance}")
            
            return Response({
                'success': True,
                'message': 'Alert deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            return Response({
                'success': False,
                'error': 'Failed to delete alert'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def test_alert(self, request, pk=None):
        """Test an alert by evaluating it immediately"""
        try:
            alert = self.get_object()
            
            # Trigger evaluation task
            task = evaluate_alert.delay(alert.id)
            result = task.get(timeout=30)
            
            return Response({
                'success': True,
                'message': 'Alert tested successfully',
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Error testing alert: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def triggered(self, request):
        """Get user's triggered alerts"""
        try:
            triggered_alerts = TriggeredAlert.objects.filter(
                alert__user=request.user
            ).order_by('-triggered_at')
            
            # Filter by date range
            days = request.query_params.get('days')
            if days:
                try:
                    days = int(days)
                    since = timezone.now() - timezone.timedelta(days=days)
                    triggered_alerts = triggered_alerts.filter(triggered_at__gte=since)
                except ValueError:
                    pass
            
            page = self.paginate_queryset(triggered_alerts)
            if page is not None:
                serializer = TriggeredAlertSerializer(page, many=True)
                return self.get_paginated_response({
                    'success': True,
                    'data': serializer.data
                })
            
            serializer = TriggeredAlertSerializer(triggered_alerts, many=True)
            return Response({
                'success': True,
                'count': triggered_alerts.count(),
                'data': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error fetching triggered alerts: {e}")
            return Response({
                'success': False,
                'error': 'Failed to fetch triggered alerts'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user's alert statistics"""
        try:
            user_alerts = Alert.objects.filter(user=request.user)
            triggered_alerts = TriggeredAlert.objects.filter(alert__user=request.user)
            
            stats = {
                'total_alerts': user_alerts.count(),
                'active_alerts': user_alerts.filter(is_active=True).count(),
                'inactive_alerts': user_alerts.filter(is_active=False).count(),
                'total_triggered': triggered_alerts.count(),
                'triggered_this_week': triggered_alerts.filter(
                    triggered_at__gte=timezone.now() - timezone.timedelta(days=7)
                ).count(),
                'triggered_this_month': triggered_alerts.filter(
                    triggered_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count(),
                'alert_types': {
                    'threshold': user_alerts.filter(alert_type='threshold').count(),
                    'duration': user_alerts.filter(alert_type='duration').count(),
                }
            }
            
            return Response({
                'success': True,
                'data': stats
            })
            
        except Exception as e:
            logger.error(f"Error fetching alert statistics: {e}")
            return Response({
                'success': False,
                'error': 'Failed to fetch statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TriggeredAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing triggered alerts"""
    queryset = TriggeredAlert.objects.all()
    serializer_class = TriggeredAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TriggeredAlert.objects.filter(
            alert__user=self.request.user
        ).order_by('-triggered_at')
    
    @action(detail=True, methods=['post'])
    def resend_notification(self, request, pk=None):
        """Resend notification email for a triggered alert"""
        try:
            triggered_alert = self.get_object()
            
            # Trigger notification task
            task = send_alert_notification.delay(triggered_alert.id)
            result = task.get(timeout=30)
            
            return Response({
                'success': True,
                'message': 'Notification resend initiated',
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Error resending notification: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
