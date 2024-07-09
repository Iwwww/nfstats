# Generated by Django 5.0.6 on 2024-07-15 04:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('flow_path', models.CharField(max_length=255)),
                ('snmp_com', models.CharField(default='public', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snmpid', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('sampling', models.BooleanField(default=False)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.host')),
            ],
        ),
        migrations.CreateModel(
            name='Speed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_bps', models.BigIntegerField()),
                ('out_bps', models.BigIntegerField()),
                ('date', models.DateTimeField()),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.interface')),
            ],
        ),
    ]
