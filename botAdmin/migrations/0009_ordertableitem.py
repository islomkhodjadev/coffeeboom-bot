# Generated by Django 5.0.6 on 2024-07-13 16:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('botAdmin', '0008_orders_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderTableItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(max_length=200)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordertableitem', to='botAdmin.tablenumber')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordertableitem', to='botAdmin.telegramuser')),
            ],
        ),
    ]
