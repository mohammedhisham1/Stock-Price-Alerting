from django.db import models
from django.utils import timezone


class Stock(models.Model):
    """Model representing a stock that we monitor"""
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class StockPrice(models.Model):
    """Model representing stock price data at a specific time"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    open_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    high_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    low_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        unique_together = ['stock', 'timestamp']

    def __str__(self):
        return f"{self.stock.symbol} - ${self.price} at {self.timestamp}"

    @classmethod
    def get_latest_price(cls, stock_symbol):
        """Get the latest price for a stock"""
        try:
            stock = Stock.objects.get(symbol=stock_symbol)
            latest_price = cls.objects.filter(stock=stock).first()
            return latest_price.price if latest_price else None
        except Stock.DoesNotExist:
            return None

    @classmethod
    def get_price_history(cls, stock_symbol, hours=24):
        """Get price history for a stock within specified hours"""
        try:
            stock = Stock.objects.get(symbol=stock_symbol)
            since = timezone.now() - timezone.timedelta(hours=hours)
            return cls.objects.filter(
                stock=stock,
                timestamp__gte=since
            ).order_by('timestamp')
        except Stock.DoesNotExist:
            return cls.objects.none()


class APIRequestLog(models.Model):
    """Model to track API requests and rate limiting"""
    endpoint = models.CharField(max_length=255)
    request_count = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    last_request = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['endpoint', 'date']

    def __str__(self):
        return f"{self.endpoint} - {self.request_count} requests on {self.date}"
