# Generated by Django 2.2 on 2020-07-22 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_book'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='book_catagory',
            new_name='book_category',
        ),
    ]
