# Generated by Django 5.0.7 on 2024-07-30 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0005_ticket_admin_alter_ticket_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
