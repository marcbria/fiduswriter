# Generated by Django 3.1.4 on 2021-06-07 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0016_delete_accessrightinvite"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accessright",
            name="rights",
            field=models.CharField(
                choices=[
                    ("write", "Writer"),
                    ("write-tracked", "Write with tracked changes"),
                    ("comment", "Commentator"),
                    (
                        "review-tracked",
                        "Reviewer who can write with tracked changes",
                    ),
                    ("review", "Reviewer"),
                    ("read", "Reader"),
                    ("read-without-comments", "Reader without comment access"),
                ],
                max_length=21,
            ),
        ),
    ]
