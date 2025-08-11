from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from stocks.models import Stock

User = get_user_model()


class Alert(models.Model):
    """Model representing a user's stock alert"""
    
    ALERT_TYPES = [
        ('threshold', 'Threshold Alert'),
        ('duration', 'Duration Alert'),
    ]
    
    CONDITIONS = [
        ('above', 'Above'),
        ('below', 'Below'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    condition = models.CharField(max_length=10, choices=CONDITIONS)
    threshold_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Required for duration alerts (minimum 1 minute)"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Duration tracking fields
    condition_first_met = models.DateTimeField(null=True, blank=True)
    condition_currently_met = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'stock'], name='alert_active_stock_idx'),
            models.Index(fields=['user', 'is_active'], name='alert_user_active_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'stock', 'alert_type', 'condition', 'threshold_price'],
                condition=models.Q(is_active=True),
                name='unique_active_alert_per_user_stock_condition'
            )
        ]
    
    def __str__(self):
        duration_str = f" for {self.duration_minutes}min" if self.alert_type == 'duration' else ""
        return f"{self.user.username}: {self.stock.symbol} {self.condition} ${self.threshold_price}{duration_str}"
    
    def clean(self):
        """Validate model fields"""
        from django.core.exceptions import ValidationError
        if self.alert_type == 'duration':
            if not self.duration_minutes:
                raise ValidationError("Duration minutes is required for duration alerts")
            if self.duration_minutes < 1:
                raise ValidationError("Duration must be at least 1 minute")
        if self.alert_type == 'threshold' and self.duration_minutes:
            self.duration_minutes = None
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def check_condition(self, current_price):
        """Check if the alert condition is met with the current price"""
        if self.condition == 'above':
            return current_price > self.threshold_price
        elif self.condition == 'below':
            return current_price < self.threshold_price
        return False
    
    def get_condition_display_text(self):
        """Get human-readable condition text"""
        return f"goes {self.condition} ${self.threshold_price}"
    
    def should_trigger(self, current_price):
        """Determine if the alert should be triggered"""
        condition_met = self.check_condition(current_price)
        
        if self.alert_type == 'threshold':
            return condition_met
        
        elif self.alert_type == 'duration':
            now = timezone.now()
            
            if condition_met:
                if not self.condition_currently_met:
                    # Condition just became met
                    self.condition_first_met = now
                    self.condition_currently_met = True
                    self.save(update_fields=['condition_first_met', 'condition_currently_met'])
                    return False
                
                # Check if duration has passed
                duration_passed = now - self.condition_first_met
                required_duration = timezone.timedelta(minutes=self.duration_minutes)
                
                return duration_passed >= required_duration
            
            else:
                # Condition is not met, reset tracking
                if self.condition_currently_met:
                    self.condition_first_met = None
                    self.condition_currently_met = False
                    self.save(update_fields=['condition_first_met', 'condition_currently_met'])
                return False
        
        return False


class TriggeredAlert(models.Model):
    """Model representing alerts that have been triggered"""
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='triggered_instances')
    trigger_price = models.DecimalField(max_digits=10, decimal_places=2)
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    # Notification tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    notification_error = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"Triggered: {self.alert} at ${self.trigger_price} on {self.triggered_at}"


class NotificationTemplate(models.Model):
    """Model for email notification templates"""
    
    TEMPLATE_TYPES = [
        ('threshold', 'Threshold Alert'),
        ('duration', 'Duration Alert'),
    ]
    
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, unique=True)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.template_type.title()} Template"
