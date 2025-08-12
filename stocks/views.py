from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings
import logging

from .models import Stock, StockPrice
from .serializers import StockSerializer, StockPriceSerializer, StockPriceHistorySerializer
from .services import StockDataService, initialize_monitored_stocks
from .tasks import fetch_all_stock_prices

logger = logging.getLogger(__name__)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for stock data operations"""
    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get('symbol', None)
        if symbol:
            queryset = queryset.filter(symbol__icontains=symbol)
        return queryset.order_by('symbol')
    
    @action(detail=False, methods=['get'])
    def current_prices(self, request):
        """Get current prices for all monitored stocks"""
        try:
            stocks = self.get_queryset()
            data = []
            
            for stock in stocks:
                latest_price = stock.prices.first()
                if latest_price:
                    data.append({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': float(latest_price.price),
                        'timestamp': latest_price.timestamp,
                        'exchange': stock.exchange
                    })
            
            return Response({
                'success': True,
                'count': len(data),
                'data': data,
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        """Get price history for a specific stock"""
        try:
            stock = self.get_object()
            hours = int(request.query_params.get('hours', 24))
            
            since = timezone.now() - timezone.timedelta(hours=hours)
            prices = StockPrice.objects.filter(
                stock=stock,
                timestamp__gte=since
            ).order_by('-timestamp')
            
            serializer = StockPriceSerializer(prices, many=True)
            
            return Response({
                'success': True,
                'symbol': stock.symbol,
                'period': f'{hours} hours',
                'count': prices.count(),
                'data': serializer.data
            })
            
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid hours parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def refresh_prices(self, request):
        """Manually trigger price refresh for all stocks"""
        try:
            # Trigger background task
            task = fetch_all_stock_prices.delay()
            
            return Response({
                'success': True,
                'message': 'Price refresh initiated',
                'task_id': task.id
            })
            
        except Exception as e:
            logger.error(f"Error initiating price refresh: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def refresh_price(self, request, pk=None):
        """Manually trigger price refresh for a specific stock"""
        try:
            stock = self.get_object()
            
            # Use the combined service method for immediate update
            service = StockDataService()
            result = service.fetch_and_update_stock(stock.symbol)
            
            if result:
                # Get the updated stock price
                stock.refresh_from_db()
                return Response({
                    'success': True,
                    'message': f'Price updated for {stock.symbol}',
                    'price': str(stock.current_price),
                    'updated_at': stock.last_updated
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to fetch and update price data'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Error refreshing price for stock: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def initialize_stocks(self, request):
        """Initialize monitored stocks (admin only)"""
        try:
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Admin access required'
                }, status=status.HTTP_403_FORBIDDEN)
            
            created_count = initialize_monitored_stocks()
            
            return Response({
                'success': True,
                'message': f'Initialized {created_count} stocks',
                'created_count': created_count
            })
            
        except Exception as e:
            logger.error(f"Error initializing stocks: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
