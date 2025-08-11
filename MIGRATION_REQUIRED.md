# 🔄 Database Migration Required

## **New Fields Added to Stock Model**

The following fields were added to `stocks.models.Stock`:

```python
current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
last_updated = models.DateTimeField(null=True, blank=True)
```

## **Migration Commands**

After deploying to Ubuntu EC2, run:

```bash
# Generate migration file
python manage.py makemigrations stocks

# Apply the migration
python manage.py migrate stocks

# Verify the migration
python manage.py showmigrations stocks
```

## **Expected Migration File**

The migration will add these fields to the existing `stocks_stock` table:
- `current_price`: DECIMAL(10,2) NULL
- `last_updated`: TIMESTAMP NULL

These fields will be populated automatically when the `fetch_all_stock_prices` Celery task runs.

## **No Data Loss**

✅ All existing data preserved  
✅ New fields are nullable (safe migration)  
✅ Backward compatible with existing code
