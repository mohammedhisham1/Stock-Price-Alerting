from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import logging

from .models import Alert, TriggeredAlert
from .serializers import (
    AlertSerializer, 
    AlertCreateSerializer, 
    TriggeredAlertSerializer,
)
from .tasks import evaluate_alert
logger = logging.getLogger(__name__)


class AlertViewSet(viewsets.ModelViewSet):
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
    queryset = TriggeredAlert.objects.all()
    serializer_class = TriggeredAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = TriggeredAlert.objects.filter(
            alert__user=self.request.user
        ).order_by('-triggered_at')
        
        # Filter by date range if provided
        days = self.request.query_params.get('days')
        if days:
            try:
                days = int(days)
                since = timezone.now() - timezone.timedelta(days=days)
                queryset = queryset.filter(triggered_at__gte=since)
            except ValueError:
                pass
                
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List user's triggered alerts with enhanced response format"""
        try:
            queryset = self.get_queryset()
            
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
            logger.error(f"Error fetching triggered alerts: {e}")
            return Response({
                'success': False,
                'error': 'Failed to fetch triggered alerts'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
