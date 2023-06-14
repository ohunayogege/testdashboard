# Generated by Django 4.2.1 on 2023-05-22 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_user_bank_branch_code_alter_user_pin'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedAccountNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_branch_code', models.CharField(blank=True, default='', max_length=100)),
                ('account_name', models.CharField(blank=True, default='', max_length=100)),
                ('account_number', models.CharField(blank=True, default='', max_length=100)),
                ('account_type', models.CharField(blank=True, choices=[('Fixed Deposit', 'Fixed Deposit'), ('Savings', 'Savings'), ('Current', 'Current'), ('Dormant', 'Dormant')], default='Savings', max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='account_status',
            field=models.CharField(blank=True, choices=[('Verified', 'Verified'), ('Dormant', 'Dormant'), ('Suspend', 'Suspend'), ('Pending Verification', 'Pending Verification')], default='Verified', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='account_type',
            field=models.CharField(blank=True, choices=[('Fixed Deposit', 'Fixed Deposit'), ('Savings', 'Savings'), ('Current', 'Current'), ('Dormant', 'Dormant')], default='Savings', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email Address'),
        ),
    ]