# Generated by Django 4.2.2 on 2023-07-13 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TheBlogsApp', '0004_rename_creationdate_blogpost_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='creation_date',
            field=models.DateTimeField(),
        ),
    ]