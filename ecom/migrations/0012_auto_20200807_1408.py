# Generated by Django 2.2.10 on 2020-08-07 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0011_auto_20200807_1402'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='receiver',
            new_name='reciver',
        ),
    ]