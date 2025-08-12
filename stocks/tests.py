from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
import requests

from stocks.models import Stock, StockPrice
from stocks.services import StockDataService, initialize_monitored_stocks

User = get_user_model()


class StockModelTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NASDAQ'
        )
    
    def test_stock_creation(self):
        self.assertEqual(self.stock.symbol, 'AAPL')
        self.assertEqual(self.stock.name, 'Apple Inc.')
        self.assertTrue(self.stock.is_active)
    
    def test_stock_str_representation(self):
        expected = 'AAPL - Apple Inc.'
        self.assertEqual(str(self.stock), expected)


class StockPriceModelTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NASDAQ'
        )
        self.stock_price = StockPrice.objects.create(
            stock=self.stock,
            price=Decimal('150.00')
        )
    
    def test_stock_price_creation(self):
        self.assertEqual(self.stock_price.price, Decimal('150.00'))
        self.assertEqual(self.stock_price.stock, self.stock)
    
    def test_latest_price_via_current_price_field(self):
        # Test that we can get current price from Stock model
        self.stock.current_price = Decimal('155.00')
        self.stock.save()
        
        # Reload from database
        stock = Stock.objects.get(symbol='AAPL')
        self.assertEqual(stock.current_price, Decimal('155.00'))




class StockServicesTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NASDAQ'
        )
    
    def test_fetch_and_update_stock(self):
        service = StockDataService()
        
        # Mock the API response
        mock_response_data = {
            'close': '150.00',
            'open': '149.00', 
            'high': '151.00',
            'low': '148.00',
            'volume': '1000000'
        }
        
        with patch('stocks.services.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            stock_price = service.fetch_and_update_stock('AAPL')
            
            self.assertIsNotNone(stock_price)
            self.assertEqual(stock_price.price, Decimal('150.00'))
            self.assertEqual(stock_price.volume, 1000000)
    
    def test_fetch_and_update_nonexistent_stock(self):
        service = StockDataService()
        
        # Mock the API response
        with patch('stocks.services.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {'close': '150.00'}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            stock_price = service.fetch_and_update_stock('NONEXISTENT')
            self.assertIsNone(stock_price)
    
    def test_initialize_monitored_stocks(self):
        # Clear existing stocks
        Stock.objects.all().delete()
        
        created_count = initialize_monitored_stocks()
        
        self.assertEqual(created_count, 10)  # Should create 10 stocks
        self.assertEqual(Stock.objects.count(), 10)
        
        # Run again, should not create duplicates
        created_count = initialize_monitored_stocks()
        self.assertEqual(created_count, 0)
        self.assertEqual(Stock.objects.count(), 10)
