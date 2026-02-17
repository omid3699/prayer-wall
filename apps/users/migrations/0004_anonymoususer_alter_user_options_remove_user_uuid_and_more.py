import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_remove_user_usermae"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnonymousUser",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("display_name", models.CharField(default="Anonymous User", max_length=255)),
                ("ip_address", models.GenericIPAddressField()),
                ("user_agent", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="user",
            name="ip_address",
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="user_agent",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
