from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dfir_pericia", "0002_deviceanalysisresult_periciacase_analysisplan_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PericiaPointProxy",
            fields=[],
            options={
                "verbose_name": "punto de pericia",
                "verbose_name_plural": "puntos de pericia",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.periciapoint",),
        ),
        migrations.CreateModel(
            name="AnalysisPlanProxy",
            fields=[],
            options={
                "verbose_name": "plan de analisis",
                "verbose_name_plural": "planes de analisis",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.analysisplan",),
        ),
        migrations.CreateModel(
            name="DeviceAnalysisResultProxy",
            fields=[],
            options={
                "verbose_name": "resultado de analisis por dispositivo",
                "verbose_name_plural": "resultados de analisis por dispositivo",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.deviceanalysisresult",),
        ),
        migrations.CreateModel(
            name="PericiaExecutionProxy",
            fields=[],
            options={
                "verbose_name": "ejecucion de pericia",
                "verbose_name_plural": "ejecuciones de pericia",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.periciaexecution",),
        ),
        migrations.CreateModel(
            name="PericiaFindingProxy",
            fields=[],
            options={
                "verbose_name": "hallazgo de pericia",
                "verbose_name_plural": "hallazgos de pericia",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.periciafinding",),
        ),
    ]
