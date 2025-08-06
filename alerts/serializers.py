from rest_framework import serializers
from .models import Alert, TriggeredAlert, NotificationTemplate
from stocks.models import Stock


class AlertSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'stock', 'stock_symbol', 'stock_name', 'alert_type', 
            'condition', 'threshold_price', 'duration_minutes', 'is_active',
            'condition_first_met', 'condition_currently_met', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stock_symbol', 'stock_name', 'condition_first_met', 
            'condition_currently_met', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        alert_type = data.get('alert_type')
        duration_minutes = data.get('duration_minutes')
        
        if alert_type == 'duration' and not duration_minutes:
            raise serializers.ValidationError(
                "Duration minutes is required for duration alerts"
            )
        
        if alert_type == 'threshold' and duration_minutes:
            data['duration_minutes'] = None
        
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AlertCreateSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(write_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'stock_symbol', 'alert_type', 'condition', 
            'threshold_price', 'duration_minutes'
        ]
    
    def validate_stock_symbol(self, value):
        try:
            stock = Stock.objects.get(symbol=value.upper(), is_active=True)
            return stock
        except Stock.DoesNotExist:
            raise serializers.ValidationError(f"Stock '{value}' not found or not active")
    
    def validate(self, data):
        alert_type = data.get('alert_type')
        duration_minutes = data.get('duration_minutes')
        
        if alert_type == 'duration' and not duration_minutes:
            raise serializers.ValidationError(
                "Duration minutes is required for duration alerts"
            )
        
        if alert_type == 'threshold' and duration_minutes:
            data['duration_minutes'] = None
        
        return data
    
    def create(self, validated_data):
        stock = validated_data.pop('stock_symbol')
        validated_data['stock'] = stock
        validated_data['user'] = self.context['request'].user
        return Alert.objects.create(**validated_data)


class TriggeredAlertSerializer(serializers.ModelSerializer):
    alert = AlertSerializer(read_only=True)
    stock_symbol = serializers.CharField(source='alert.stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='alert.stock.name', read_only=True)
    alert_type = serializers.CharField(source='alert.alert_type', read_only=True)
    condition = serializers.CharField(source='alert.condition', read_only=True)
    threshold_price = serializers.DecimalField(
        source='alert.threshold_price', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = TriggeredAlert
        fields = [
            'id', 'alert', 'stock_symbol', 'stock_name', 'alert_type',
            'condition', 'threshold_price', 'trigger_price', 'triggered_at',
            'email_sent', 'email_sent_at', 'notification_error'
        ]
        read_only_fields = '__all__'


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'template_type', 'subject', 'html_content', 
            'text_content', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
