# Generated by Django 2.2 on 2020-07-24 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_auto_20200722_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_status',
            field=models.CharField(default='active', max_length=100),
        ),
    ]
