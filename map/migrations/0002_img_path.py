# Generated by Django 4.2.11 on 2024-05-02 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("map", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="img",
            name="path",
            field=models.CharField(
                default="", help_text="path", max_length=200, verbose_name="path"
            ),
        ),
    ]
