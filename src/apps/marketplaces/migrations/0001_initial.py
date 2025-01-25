# Generated by Django 5.0.6 on 2024-12-21 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Marketplace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('platform', models.CharField(choices=[('AMAZON', 'amazon'), ('WOOCOMMERCE', 'woocommerce')], default='AMAZON', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
