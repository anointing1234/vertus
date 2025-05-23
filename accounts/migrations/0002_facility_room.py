# Generated by Django 5.2 on 2025-05-03 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('standard', 'Standard Room'), ('presidential', 'Presidential Room'), ('suite', 'Bedroom Suite'), ('executive', 'Executive Deluxe')], max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('price_per_night', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='room_images/')),
                ('size', models.CharField(default='600 Sq', max_length=20)),
                ('bed_type', models.CharField(default='2 Single Bed', max_length=50)),
                ('occupancy', models.CharField(default='Three Persons', max_length=50)),
                ('facilities', models.ManyToManyField(blank=True, to='accounts.facility')),
            ],
        ),
    ]
