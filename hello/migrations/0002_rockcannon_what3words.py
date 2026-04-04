from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hello", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rockcannon",
            name="what3words",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
