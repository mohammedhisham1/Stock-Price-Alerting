from rest_framework import serializers
from .models import Stock, StockPrice


class StockSerializer(serializers.ModelSerializer):
    latest_price = serializers.SerializerMethodField()
    price_change_24h = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'exchange', 'is_active', 
                 'latest_price', 'price_change_24h', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_price(self, obj):
        latest_price = obj.prices.first()
        return float(latest_price.price) if latest_price else None
    
    def get_price_change_24h(self, obj):
        latest_prices = obj.prices.all()[:2]
        if len(latest_prices) >= 2:
            current = latest_prices[0].price
            previous = latest_prices[1].price
            change = current - previous
            return {
                'amount': float(change),
                'percentage': float((change / previous) * 100) if previous else 0
            }
        return None


class StockPriceSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    
    class Meta:
        model = StockPrice
        fields = ['id', 'stock', 'stock_symbol', 'price', 'open_price', 
                 'high_price', 'low_price', 'close_price', 'volume', 
                 'timestamp', 'created_at']
        read_only_fields = ['id', 'created_at']


class StockPriceHistorySerializer(serializers.Serializer):
    symbol = serializers.CharField()
    prices = StockPriceSerializer(many=True, read_only=True)
    period = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
