from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='StoreProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.CharField(max_length=20, unique=True)),
                ('sku', models.CharField(blank=True, max_length=100)),
                ('title', models.CharField(blank=True, max_length=255)),
                ('brand', models.CharField(blank=True, max_length=255)),
                ('category', models.CharField(blank=True, max_length=255)),
                ('price_mxn', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('tracking_type', models.CharField(choices=[('regular', 'Regular'), ('marketplace', 'Marketplace')], default='regular', max_length=20)),
                ('tracking_enabled', models.BooleanField(default=True)),
                ('keepa_marketplace', models.CharField(default='US', max_length=2)),
                ('keepa_tracking_id', models.CharField(blank=True, max_length=100)),
                ('last_us_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('last_keepa_notification_at', models.DateTimeField(blank=True, null=True)),
                ('keepa_available', models.BooleanField(default=True)),
                ('keepa_unavailable_reason', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='KeepaNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asin', models.CharField(blank=True, max_length=20)),
                ('marketplace', models.CharField(blank=True, max_length=10)),
                ('event_type', models.CharField(blank=True, max_length=50)),
                ('message', models.TextField(blank=True)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store_product', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='keepa_notifications', to='store_products.storeproduct')),
            ],
        ),
    ]
