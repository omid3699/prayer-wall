# Generated migration to remove the misspelled `usermae` field that caused UUIDs to appear in the admin.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_options_alter_user_managers_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="usermae",
        ),
    ]
