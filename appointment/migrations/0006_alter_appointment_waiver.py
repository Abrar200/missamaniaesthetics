# Generated by Django 4.2.13 on 2024-06-27 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0005_services_alter_service_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='waiver',
            field=models.TextField(null=True),
        ),
    ]
