# Generated by Django 5.2 on 2025-05-19 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_product_product_photo_product_product_photo_mime'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='_base64_image',
            field=models.TextField(blank=True, null=True),
        ),
    ]
