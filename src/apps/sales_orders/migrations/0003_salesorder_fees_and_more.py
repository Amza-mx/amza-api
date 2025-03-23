# Generated by Django 5.0.6 on 2025-03-16 20:35

import django.db.models.expressions
import djmoney.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_orders', '0002_salesorder_total_amount_currency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='fees',
            field=models.GeneratedField(db_persist=True, expression=django.db.models.expressions.CombinedExpression(models.F('total_amount'), '*', models.Value(0.15)), output_field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='MXN', max_digits=10)),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='yield_amount_before_shipping',
            field=models.GeneratedField(db_persist=True, expression=django.db.models.expressions.CombinedExpression(models.F('total_amount'), '-', models.F('fees')), output_field=djmoney.models.fields.MoneyField(decimal_places=2, default_currency='MXN', max_digits=10)),
        ),
    ]
