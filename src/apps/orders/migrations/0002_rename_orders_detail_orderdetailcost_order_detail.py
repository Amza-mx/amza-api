# Generated by Django 5.0.6 on 2024-06-30 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderdetailcost',
            old_name='orders_detail',
            new_name='order_detail',
        ),
    ]
