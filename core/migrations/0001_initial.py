# Generated by Django 5.2 on 2025-05-17 05:21

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillDate',
            fields=[
                ('billno', models.CharField(editable=False, max_length=25, primary_key=True, serialize=False)),
                ('date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.CharField(editable=False, max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('rr_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('mr_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('store_id', models.CharField(editable=False, max_length=20, primary_key=True, serialize=False)),
                ('store_name', models.CharField(max_length=100)),
                ('store_owner', models.CharField(max_length=100)),
                ('gst_number', models.CharField(max_length=20)),
                ('block', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('nearby', models.CharField(max_length=100)),
                ('pincode', models.CharField(max_length=6)),
                ('phone_number', models.CharField(max_length=15)),
                ('whatsapp_number', models.CharField(max_length=15)),
                ('location', models.CharField(max_length=100)),
                ('photo', models.ImageField(upload_to='store_photos/')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('agent_id', models.CharField(editable=False, max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('whatsapp_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('pincode', models.CharField(max_length=6)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AgentBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.agent')),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manager_id', models.CharField(blank=True, max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=20)),
                ('whatsapp_number', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('pincode', models.CharField(max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='agent',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.manager'),
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField()),
                ('billno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.billdate')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_id', models.CharField(editable=False, max_length=20, primary_key=True, serialize=False)),
                ('transaction_date', models.DateField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(choices=[('credit', 'credit'), ('return', 'return')], max_length=10)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.agent')),
            ],
        ),
        migrations.CreateModel(
            name='ManagerAgentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('transaction_date', models.DateField(default=django.utils.timezone.now)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.agent')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.manager')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.transaction')),
            ],
            options={
                'verbose_name': 'Manager-Agent Transaction',
                'verbose_name_plural': 'Manager-Agent Transactions',
                'unique_together': {('transaction', 'product')},
            },
        ),
    ]
