from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging

from .models import Stock, StockPrice
from .serializers import StockSerializer, StockPriceSerializer

logger = logging.getLogger(__name__)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get('symbol', None)
        if symbol:
            queryset = queryset.filter(symbol__icontains=symbol)
        return queryset.order_by('symbol')
    
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
    
    @action(detail=False, methods=['get'])
    def current_prices(self, request):
        """Get current prices for all active stocks"""
        try:
            stocks = self.get_queryset()
            
            # Get latest price for each stock efficiently
            stocks_with_prices = []
            for stock in stocks:
                latest_price = stock.prices.first()  # Already ordered by -timestamp
                stock_data = {
                    'id': stock.id,
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'current_price': float(latest_price.price) if latest_price else None,
                    'last_updated': latest_price.timestamp if latest_price else None
                }
                stocks_with_prices.append(stock_data)
            
            return Response({
                'success': True,
                'count': len(stocks_with_prices),
                'data': stocks_with_prices
            })
            
        except Exception as e:
            logger.error(f"Error fetching current prices: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
