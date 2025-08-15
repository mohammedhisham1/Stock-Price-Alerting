from django.contrib import admin
from .models import Alert, TriggeredAlert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'stock', 'alert_type', 'condition', 'threshold_price', 
        'duration_minutes', 'is_active', 'created_at'
    ]
    list_filter = ['alert_type', 'condition', 'is_active', 'stock', 'created_at']
    search_fields = ['user__username', 'stock__symbol', 'stock__name']
    ordering = ['-created_at']
    readonly_fields = ['condition_first_met', 'condition_currently_met', 'created_at', 'updated_at']


@admin.register(TriggeredAlert)
class TriggeredAlertAdmin(admin.ModelAdmin):
    list_display = [
        'alert', 'trigger_price', 'triggered_at', 'email_sent', 'email_sent_at'
    ]
    list_filter = ['email_sent', 'triggered_at', 'alert__alert_type']
    search_fields = ['alert__user__username', 'alert__stock__symbol']
    ordering = ['-triggered_at']
    readonly_fields = ['triggered_at', 'email_sent_at']


