# Generated by Django 4.1.3 on 2022-11-16 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_rename_content_news_source_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="timestamp",
            field=models.DateTimeField(default=0),
        ),
    ]
