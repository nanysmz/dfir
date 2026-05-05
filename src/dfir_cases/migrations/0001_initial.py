from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dfir_pericia", "0002_deviceanalysisresult_periciacase_analysisplan_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PericiaCaseProxy",
            fields=[],
            options={
                "verbose_name": "caso pericial",
                "verbose_name_plural": "casos periciales",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.periciacase",),
        ),
        migrations.CreateModel(
            name="PericiaDocumentProxy",
            fields=[],
            options={
                "verbose_name": "documento pericial",
                "verbose_name_plural": "documentos periciales",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.periciadocument",),
        ),
        migrations.CreateModel(
            name="RequestedPointProxy",
            fields=[],
            options={
                "verbose_name": "punto solicitado",
                "verbose_name_plural": "puntos solicitados",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.requestedpoint",),
        ),
    ]
