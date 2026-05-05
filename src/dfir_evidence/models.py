from dfir_pericia.models import EvidenceFile, EvidenceItem, PreservedArtifact


class EvidenceFileProxy(EvidenceFile):
    class Meta:
        proxy = True
        app_label = "dfir_evidence"
        verbose_name = EvidenceFile._meta.verbose_name
        verbose_name_plural = EvidenceFile._meta.verbose_name_plural


class EvidenceItemProxy(EvidenceItem):
    class Meta:
        proxy = True
        app_label = "dfir_evidence"
        verbose_name = EvidenceItem._meta.verbose_name
        verbose_name_plural = EvidenceItem._meta.verbose_name_plural


class PreservedArtifactProxy(PreservedArtifact):
    class Meta:
        proxy = True
        app_label = "dfir_evidence"
        verbose_name = PreservedArtifact._meta.verbose_name
        verbose_name_plural = PreservedArtifact._meta.verbose_name_plural
