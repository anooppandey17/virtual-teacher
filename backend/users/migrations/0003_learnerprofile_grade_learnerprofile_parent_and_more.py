# Generated by Django 5.2.1 on 2025-05-25 04:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_adminprofile_learnerprofile_parentprofile_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="learnerprofile",
            name="grade",
            field=models.CharField(default="Grade", max_length=50),
        ),
        migrations.AddField(
            model_name="learnerprofile",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="learnerprofile",
            name="school",
            field=models.CharField(default="School", max_length=100),
        ),
        migrations.AddField(
            model_name="learnerprofile",
            name="teacher",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="students",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
