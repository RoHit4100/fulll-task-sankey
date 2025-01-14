# Generated by Django 5.1.1 on 2024-10-20 04:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('route_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('route_name', models.CharField(max_length=100)),
                ('route_origin', models.CharField(max_length=100)),
                ('route_destination', models.CharField(max_length=100)),
                ('route_stops', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('trip_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('vehicle_id', models.IntegerField()),
                ('driver_name', models.CharField(max_length=100)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trip.route')),
            ],
        ),
    ]
