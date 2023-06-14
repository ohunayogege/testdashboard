# Generated by Django 4.2.1 on 2023-05-22 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_user_has_pin_user_pin_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bank_branch_code',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='pin',
            field=models.CharField(blank=True, default='', max_length=4, verbose_name='Transaction Pin'),
        ),
    ]
