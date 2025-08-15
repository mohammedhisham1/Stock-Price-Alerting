from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from unittest.mock import patch

from alerts.models import Alert, TriggeredAlert
from stocks.models import Stock, StockPrice

User = get_user_model()


class AlertModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NASDAQ'
        )
    
    def test_threshold_alert_creation(self):
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            threshold_price=Decimal('200.00')
        )
        
        self.assertEqual(alert.alert_type, 'threshold')
        self.assertEqual(alert.condition, 'above')
        self.assertEqual(alert.threshold_price, Decimal('200.00'))
        self.assertIsNone(alert.duration_minutes)
        self.assertTrue(alert.is_active)
    
    def test_duration_alert_creation(self):
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='duration',
            condition='below',
            threshold_price=Decimal('150.00'),
            duration_minutes=60
        )
        
        self.assertEqual(alert.alert_type, 'duration')
        self.assertEqual(alert.duration_minutes, 60)
    
    def test_check_condition_above(self):
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            threshold_price=Decimal('200.00')
        )
        
        self.assertTrue(alert.check_condition(Decimal('205.00')))
        self.assertFalse(alert.check_condition(Decimal('195.00')))
        self.assertFalse(alert.check_condition(Decimal('200.00')))
    
    def test_check_condition_below(self):
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='below',
            threshold_price=Decimal('150.00')
        )
        
        self.assertTrue(alert.check_condition(Decimal('145.00')))
        self.assertFalse(alert.check_condition(Decimal('155.00')))
        self.assertFalse(alert.check_condition(Decimal('150.00')))
    
    def test_threshold_alert_should_trigger(self):
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            threshold_price=Decimal('200.00')
        )
        
        self.assertTrue(alert.should_trigger(Decimal('205.00')))
        self.assertFalse(alert.should_trigger(Decimal('195.00')))
    
    def test_duration_alert_should_trigger(self):
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='duration',
            condition='above',
            threshold_price=Decimal('200.00'),
            duration_minutes=1  # 1 minute for testing
        )
        
        # First time condition is met - should not trigger yet
        self.assertFalse(alert.should_trigger(Decimal('205.00')))
        
        # Simulate time passing by manually setting the timestamp
        alert.condition_first_met = timezone.now() - timezone.timedelta(minutes=2)
        alert.save()
        
        # Now it should trigger
        self.assertTrue(alert.should_trigger(Decimal('205.00')))
    
    def test_alert_str_representation(self):
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            threshold_price=Decimal('200.00')
        )
        
        expected = 'testuser: AAPL above $200.00'
        self.assertEqual(str(alert), expected)


class TriggeredAlertModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            exchange='NASDAQ'
        )
        self.alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            threshold_price=Decimal('200.00')
        )
    
    def test_triggered_alert_creation(self):
        triggered_alert = TriggeredAlert.objects.create(
            alert=self.alert,
            trigger_price=Decimal('205.00')
        )
        
        self.assertEqual(triggered_alert.alert, self.alert)
        self.assertEqual(triggered_alert.trigger_price, Decimal('205.00'))
        self.assertFalse(triggered_alert.email_sent)
        self.assertIsNone(triggered_alert.email_sent_at)


