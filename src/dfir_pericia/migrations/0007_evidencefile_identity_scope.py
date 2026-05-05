from django.db import migrations, models


def backfill_evidence_file_identity_scope(apps, schema_editor):
    EvidenceFile = apps.get_model("dfir_pericia", "EvidenceFile")
    EvidenceItem = apps.get_model("dfir_pericia", "EvidenceItem")

    evidence_files = EvidenceFile.objects.all().order_by("pk")
    for evidence_file in evidence_files.iterator():
        scoped_case_ids = list(
            dict.fromkeys(
                list(
                    EvidenceItem.objects.filter(evidence_file_id=evidence_file.pk).values_list(
                        "pericia_case_id", flat=True
                    )
                )
                + list(
                    EvidenceItem.objects.filter(evidence_files=evidence_file).values_list(
                        "pericia_case_id", flat=True
                    )
                )
            )
        )
        if len(scoped_case_ids) == 1 and scoped_case_ids[0]:
            evidence_file.identity_scope = f"case:{scoped_case_ids[0]}"
        else:
            evidence_file.identity_scope = "global"
        evidence_file.save(update_fields=["identity_scope"])


class Migration(migrations.Migration):

    dependencies = [
        ("dfir_pericia", "0006_evidenceitemsource"),
    ]

    operations = [
        migrations.AddField(
            model_name="evidencefile",
            name="identity_scope",
            field=models.CharField(
                db_index=True,
                default="global",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="evidencefile",
            name="source_path",
            field=models.CharField(max_length=1024),
        ),
        migrations.RunPython(
            backfill_evidence_file_identity_scope,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="evidencefile",
            constraint=models.UniqueConstraint(
                fields=("identity_scope", "source_path"),
                name="unique_evidence_file_identity_scope_source_path",
            ),
        ),
    ]
