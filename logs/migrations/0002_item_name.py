# Generated by Django 4.2.6 on 2023-10-13 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='name',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
