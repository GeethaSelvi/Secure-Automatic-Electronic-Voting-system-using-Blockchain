# Generated by Django 5.1.7 on 2025-04-18 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voter', '0003_alter_voter_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='results',
            name='tx_hash',
            field=models.CharField(default=1, max_length=66),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voter',
            name='eth_address',
            field=models.CharField(default=1, max_length=42, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voter',
            name='eth_private_key',
            field=models.CharField(default=1, editable=False, max_length=66),
            preserve_default=False,
        ),
    ]
