from django.contrib import admin
from .models import Stock, StockPrice


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'exchange', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'exchange', 'created_at']
    search_fields = ['symbol', 'name']
    ordering = ['symbol']


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'price', 'volume', 'timestamp', 'created_at']
    list_filter = ['stock', 'timestamp']
    search_fields = ['stock__symbol', 'stock__name']
    ordering = ['-timestamp']
    readonly_fields = ['created_at']
