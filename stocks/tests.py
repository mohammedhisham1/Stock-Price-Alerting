from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
import requests

from stocks.models import Stock, StockPrice
from stocks.services import StockDataService, update_stock_price, initialize_monitored_stocks

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


class StockDataServiceTest(TestCase):
    def setUp(self):
        self.service = StockDataService()
    
    @patch('stocks.services.requests.get')
    def test_fetch_quote_success_simplified(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'close': '150.25',
            'open': '149.50',
            'high': '151.00',
            'low': '148.75',
            'volume': '1000000'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        quote_data = self.service.fetch_quote('AAPL')
        self.assertIsNotNone(quote_data)
        self.assertEqual(quote_data['price'], Decimal('150.25'))
    
    @patch('stocks.services.requests.get')
    def test_fetch_quote_failure(self, mock_get):
        # Mock failed API response (RequestException)
        mock_get.side_effect = requests.RequestException('API Error')
        
        quote_data = self.service.fetch_quote('AAPL')
        self.assertIsNone(quote_data)
    
    @patch('stocks.services.requests.get')
    def test_fetch_quote_success(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'close': '150.25',
            'open': '149.50',
            'high': '151.00',
            'low': '148.75',
            'volume': '1000000'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        quote = self.service.fetch_quote('AAPL')
        self.assertEqual(quote['price'], Decimal('150.25'))
        self.assertEqual(quote['open'], Decimal('149.50'))
        self.assertEqual(quote['volume'], 1000000)


class StockServicesTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NASDAQ'
        )
    
    def test_update_stock_price(self):
        quote_data = {
            'price': Decimal('150.00'),
            'open': Decimal('149.00'),
            'high': Decimal('151.00'),
            'low': Decimal('148.00'),
            'volume': 1000000
        }
        
        stock_price = update_stock_price('AAPL', quote_data)
        
        self.assertIsNotNone(stock_price)
        self.assertEqual(stock_price.price, Decimal('150.00'))
        self.assertEqual(stock_price.volume, 1000000)
    
    def test_update_stock_price_nonexistent_stock(self):
        quote_data = {'price': Decimal('150.00')}
        stock_price = update_stock_price('NONEXISTENT', quote_data)
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
