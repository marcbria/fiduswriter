# Generated by Django 4.1 on 2022-09-29 08:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0009_alter_user_contacts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="contacts",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
