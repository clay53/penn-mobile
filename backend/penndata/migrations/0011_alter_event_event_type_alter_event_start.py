# Generated by Django 5.0.2 on 2024-03-15 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("penndata", "0010_auto_20240228_0150"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="event_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("PENN TODAY", "Penn Today"),
                    ("VENTURE LAB", "Venture Lab"),
                    ("PENN ENGINEERING", "Penn Engineering"),
                    ("WHARTON", "Wharton"),
                    ("RODIN COLLEGE HOUSE", "Rodin College House"),
                    ("HARNWELL COLLEGE HOUSE", "Harnwell College House"),
                    ("HARRISON COLLEGE HOUSE", "Harrison College House"),
                    ("GUTMANN COLLEGE HOUSE", "Gutmann College House"),
                    ("RADIAN COLLEGE HOUSE", "Radian College House"),
                    ("LAUDER COLLEGE HOUSE", "Lauder College House"),
                    ("HILL COLLEGE HOUSE", "Hill College HouseE"),
                    ("KCECH COLLEGE HOUSE", "Kcech College House"),
                    ("WARE COLLEGE HOUSE", "Ware College House"),
                    ("FISHER HASSENFELD COLLEGE HOUSE", "Fisher Hassenfeld College House"),
                    ("RIEPE COLLEGE HOUSE", "Riepe College House"),
                    ("DU BOIS COLLEGE HOUSE", "Du Bois College House"),
                    ("GREGORY COLLEGE HOUSE", "Gregory College House"),
                    ("STOUFFER COLLEGE HOUSE", "Stouffer College House"),
                ],
                default=None,
                max_length=63,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="start",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
