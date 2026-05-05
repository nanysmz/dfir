from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dfir_pericia", "0002_deviceanalysisresult_periciacase_analysisplan_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EvidenceFileProxy",
            fields=[],
            options={
                "verbose_name": "archivo de evidencia",
                "verbose_name_plural": "archivos de evidencia",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.evidencefile",),
        ),
        migrations.CreateModel(
            name="EvidenceItemProxy",
            fields=[],
            options={
                "verbose_name": "elemento de evidencia",
                "verbose_name_plural": "elementos de evidencia",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.evidenceitem",),
        ),
        migrations.CreateModel(
            name="PreservedArtifactProxy",
            fields=[],
            options={
                "verbose_name": "artefacto resguardado",
                "verbose_name_plural": "artefactos resguardados",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("dfir_pericia.preservedartifact",),
        ),
    ]
