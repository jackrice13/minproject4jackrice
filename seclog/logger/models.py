from django.db import models
from django.contrib.auth.models import User


# ------------------------------------------------------------------
# LOOKUP / REFERENCE TABLES
# These hold reusable choices so you don't retype them on every incident
# ------------------------------------------------------------------

class IncidentType(models.Model):
    """
    Stores the type of incident (e.g. Phishing, Malware, DDoS).
    Keeping this in its own table means you can add new types without
    changing any code — just add a row to the database.
    """
    type_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.type_name


class AttackVector(models.Model):
    """
    How the attacker got in (e.g. Email, Web, USB, Insider).
    """
    vector_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.vector_name


# ------------------------------------------------------------------
# RESPONDERS
# Changed to try and use Django's user engine
# ------------------------------------------------------------------

class Responder(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=100)  # e.g. Analyst, IR Lead

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"


# ------------------------------------------------------------------
# CORE INCIDENT TABLE
# Every other table links back to this one
# ------------------------------------------------------------------

class Incident(models.Model):
    """
    The main incident record. Think of this as the 'spine' of the logger —
    everything else (assets, IoCs, evidence, etc.) hangs off this.
    """

    # --- Status & Severity choices ---
    # Storing choices as constants on the model keeps them organized
    class Status(models.TextChoices):
        OPEN        = 'OPEN',        'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED    = 'RESOLVED',    'Resolved'
        CLOSED      = 'CLOSED',      'Closed'

    class Severity(models.TextChoices):
        CRITICAL = 'CRITICAL', 'Critical'
        HIGH     = 'HIGH',     'High'
        MEDIUM   = 'MEDIUM',   'Medium'
        LOW      = 'LOW',      'Low'

    class DataClassification(models.TextChoices):
        PII          = 'PII',          'PII'
        PHI          = 'PHI',          'PHI'
        CONFIDENTIAL = 'CONFIDENTIAL', 'Confidential'
        PUBLIC       = 'PUBLIC',       'Public'

    # --- Core fields ---
    title    = models.CharField(max_length=255)
    status   = models.CharField(max_length=20,  choices=Status.choices,   default=Status.OPEN)
    severity = models.CharField(max_length=20,  choices=Severity.choices, default=Severity.MEDIUM)

    # ForeignKey = "many incidents can share one type/vector"
    # on_delete=SET_NULL means if you delete a type, the incident isn't deleted — the field just goes blank
    incident_type = models.ForeignKey(
        IncidentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    attack_vector = models.ForeignKey(
        AttackVector, on_delete=models.SET_NULL, null=True, blank=True
    )

    # --- Timestamps ---
    detected_at  = models.DateTimeField(null=True, blank=True)
    reported_at  = models.DateTimeField(null=True, blank=True)
    resolved_at  = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)  # set automatically when row is created

    # --- Detection & Assignment ---
    detected_by = models.CharField(max_length=255, blank=True)  # tool name, person, alert
    assigned_to = models.ForeignKey(
        Responder, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_incidents'
    )

    # --- Impact ---
    data_compromised     = models.BooleanField(default=False)
    data_classification  = models.CharField(
        max_length=20, choices=DataClassification.choices, blank=True
    )
    downtime_minutes     = models.PositiveIntegerField(null=True, blank=True)
    business_impact      = models.TextField(blank=True)

    # --- Technical Details ---
    cve_number      = models.CharField(max_length=20, blank=True)  # e.g. CVE-2024-1234
    repeat_incident = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.incident_id}] {self.title} — {self.status}"

    # This gives the auto-generated primary key a readable name in the admin panel
    @property
    def incident_id(self):
        return self.pk


# ------------------------------------------------------------------
# AFFECTED ASSETS
# One incident can affect many systems — so this is a separate table
# ------------------------------------------------------------------

class AffectedAsset(models.Model):
    """
    A system, device, or resource that was involved in the incident.
    Linked to Incident with a ForeignKey (many assets → one incident).
    """

    class AssetType(models.TextChoices):
        SERVER      = 'SERVER',      'Server'
        WORKSTATION = 'WORKSTATION', 'Workstation'
        MOBILE      = 'MOBILE',      'Mobile'
        CLOUD       = 'CLOUD',       'Cloud Resource'
        OTHER       = 'OTHER',       'Other'

    incident         = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='assets')
    hostname         = models.CharField(max_length=255, blank=True)
    ip_address       = models.GenericIPAddressField(null=True, blank=True)  # supports IPv4 & IPv6
    asset_type       = models.CharField(max_length=20, choices=AssetType.choices, blank=True)
    owner_department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"


# ------------------------------------------------------------------
# INDICATORS OF COMPROMISE (IoCs)
# Malicious IPs, domains, file hashes, etc. found during investigation
# ------------------------------------------------------------------

class IndicatorOfCompromise(models.Model):
    """
    A piece of evidence that a system was involved in malicious activity.
    One incident can have many IoCs.
    """

    class IoCType(models.TextChoices):
        IP        = 'IP',        'IP Address'
        DOMAIN    = 'DOMAIN',    'Domain'
        FILE_HASH = 'FILE_HASH', 'File Hash'
        URL       = 'URL',       'URL'
        EMAIL     = 'EMAIL',     'Email Address'

    incident  = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='iocs')
    ioc_type  = models.CharField(max_length=20, choices=IoCType.choices)
    ioc_value = models.CharField(max_length=255)   # the actual hash, IP, domain, etc.
    notes     = models.TextField(blank=True)

    def __str__(self):
        return f"{self.ioc_type}: {self.ioc_value}"


# ------------------------------------------------------------------
# RESPONSE ACTIONS
# What was done at each phase: Containment, Eradication, Recovery
# ------------------------------------------------------------------

class ResponseAction(models.Model):
    """
    A single action taken during incident response.
    Tracking phase lets you see the full timeline of what was done and when.
    """

    class Phase(models.TextChoices):
        CONTAINMENT  = 'CONTAINMENT',  'Containment'
        ERADICATION  = 'ERADICATION',  'Eradication'
        RECOVERY     = 'RECOVERY',     'Recovery'

    incident     = models.ForeignKey(Incident,  on_delete=models.CASCADE,  related_name='response_actions')
    phase        = models.CharField(max_length=20, choices=Phase.choices)
    action_taken = models.TextField()
    performed_by = models.ForeignKey(Responder, on_delete=models.SET_NULL, null=True, blank=True)
    performed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.phase} — {self.action_taken[:60]}"


# ------------------------------------------------------------------
# MITRE ATT&CK MAPPINGS
# Maps the incident to the MITRE ATT&CK framework (great for your program!)
# ------------------------------------------------------------------

class MitreMapping(models.Model):
    """
    Links an incident to a MITRE ATT&CK tactic and technique.
    One incident can map to multiple techniques.
    Example: tactic='Initial Access', technique_id='T1566', technique_name='Phishing'
    """
    incident       = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='mitre_mappings')
    tactic         = models.CharField(max_length=100)   # e.g. Initial Access, Execution
    technique_id   = models.CharField(max_length=20)    # e.g. T1566
    technique_name = models.CharField(max_length=150)   # e.g. Phishing

    def __str__(self):
        return f"{self.technique_id} — {self.technique_name}"


# ------------------------------------------------------------------
# EVIDENCE
# Logs, screenshots, files collected during investigation
# ------------------------------------------------------------------

class Evidence(models.Model):
    """
    A piece of digital evidence tied to an incident.
    Chain of custody notes are important for any formal investigation.
    """

    class EvidenceType(models.TextChoices):
        LOG        = 'LOG',        'Log File'
        SCREENSHOT = 'SCREENSHOT', 'Screenshot'
        FILE       = 'FILE',       'File / Artifact'
        NOTE       = 'NOTE',       'Written Note'

    incident                = models.ForeignKey(Incident,  on_delete=models.CASCADE,  related_name='evidence')
    evidence_type           = models.CharField(max_length=20, choices=EvidenceType.choices)
    file_path               = models.CharField(max_length=500, blank=True)  # path or URL to the file
    description             = models.TextField(blank=True)
    collected_by            = models.ForeignKey(Responder, on_delete=models.SET_NULL, null=True, blank=True)
    collected_at            = models.DateTimeField(null=True, blank=True)
    chain_of_custody_notes  = models.TextField(blank=True)

    def __str__(self):
        return f"{self.evidence_type} — {self.description[:60]}"


# ------------------------------------------------------------------
# POST-INCIDENT REVIEW
# Written after the incident is closed — lessons learned, root cause, etc.
# ------------------------------------------------------------------

class PostIncidentReview(models.Model):
    """
    A post-mortem / after-action report for the incident.
    OneToOneField means each incident can only have ONE review (makes sense logically).
    """
    # OneToOneField is like a ForeignKey but enforces a 1-to-1 relationship
    incident        = models.OneToOneField(Incident,  on_delete=models.CASCADE, related_name='post_incident_review')
    root_cause      = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    followup_actions= models.TextField(blank=True)
    authored_by     = models.ForeignKey(Responder, on_delete=models.SET_NULL, null=True, blank=True)
    authored_at     = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Review for Incident #{self.incident.pk}"

class ClosingNote(models.Model):
    incident = models.OneToOneField(
        Incident, on_delete=models.CASCADE, related_name='closing_note'
    )
    summary         = models.TextField()
    resolution      = models.TextField()
    authored_by     = models.ForeignKey(
        Responder, on_delete=models.SET_NULL, null=True, blank=True
    )
    authored_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Closing Note for Incident #{self.incident.pk}"
