# Generated by Django 5.0.6 on 2025-02-03 17:34

import djmoney.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('sales_orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='total_amount_currency',
            field=djmoney.models.fields.CurrencyField(
                choices=[
                    ('MXN', 'Mexican Peso'),
                    ('USD', 'US Dollar'),
                    ('WHC', 'Warehouse Currency'),
                ],
                default='MXN',
                editable=False,
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name='salesorderdetail',
            name='unit_price_currency',
            field=djmoney.models.fields.CurrencyField(
                choices=[
                    ('MXN', 'Mexican Peso'),
                    ('USD', 'US Dollar'),
                    ('WHC', 'Warehouse Currency'),
                ],
                default='MXN',
                editable=False,
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name='salesorderdetailshipment',
            name='cost_currency',
            field=djmoney.models.fields.CurrencyField(
                choices=[
                    ('MXN', 'Mexican Peso'),
                    ('USD', 'US Dollar'),
                    ('WHC', 'Warehouse Currency'),
                ],
                default='MXN',
                editable=False,
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name='salesorder',
            name='total_amount',
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default_currency='MXN', max_digits=10
            ),
        ),
        migrations.AlterField(
            model_name='salesorderdetail',
            name='unit_price',
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default_currency='MXN', max_digits=10
            ),
        ),
        migrations.AlterField(
            model_name='salesorderdetailshipment',
            name='cost',
            field=djmoney.models.fields.MoneyField(
                decimal_places=2, default_currency='MXN', max_digits=10
            ),
        ),
    ]
