from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dfir_pericia", "0002_deviceanalysisresult_periciacase_analysisplan_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="RequestedPointResponseProxy",
            fields=[],
            options={
                "verbose_name": "respuesta a punto solicitado",
                "verbose_name_plural": "respuestas a puntos solicitados",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.requestedpointresponse",),
        ),
        migrations.CreateModel(
            name="ReportSectionProxy",
            fields=[],
            options={
                "verbose_name": "seccion del informe",
                "verbose_name_plural": "secciones del informe",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.reportsection",),
        ),
    ]
