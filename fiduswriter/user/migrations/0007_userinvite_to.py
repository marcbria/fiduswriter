# Generated by Django 3.1.4 on 2021-05-28 13:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0006_userinvite"),
    ]

    operations = [
        migrations.AddField(
            model_name="userinvite",
            name="to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="invites_to",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
