# Generated by Django 2.2.3 on 2019-07-13 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialaccount',
            name='provider',
            field=models.CharField(choices=[('google', 'Google')], max_length=30, verbose_name='provider'),
        ),
        migrations.AlterField(
            model_name='socialapp',
            name='provider',
            field=models.CharField(choices=[('google', 'Google')], max_length=30, verbose_name='provider'),
        ),
    ]
