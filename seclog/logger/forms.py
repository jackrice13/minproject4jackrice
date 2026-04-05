from django import forms
from .models import Incident, IncidentType, AttackVector, Responder
from .models import AffectedAsset, IndicatorOfCompromise, ResponseAction, MitreMapping, Evidence

class NewIncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'title',
            'severity',
            'incident_type',
            'attack_vector',
            'detected_by',
            'reported_at',
            'assigned_to',
        ]
        widgets = {
            'reported_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class EditIncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'title', 'status', 'severity', 'incident_type', 'attack_vector',
            'detected_by', 'detected_at', 'reported_at', 'resolved_at',
            'assigned_to', 'data_compromised', 'data_classification',
            'downtime_minutes', 'business_impact', 'cve_number', 'repeat_incident',
        ]
        widgets = {
            'detected_at':  forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reported_at':  forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'resolved_at':  forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'business_impact': forms.Textarea(attrs={'rows': 3}),
        }


class AffectedAssetForm(forms.ModelForm):
    class Meta:
        model = AffectedAsset
        fields = ['hostname', 'ip_address', 'asset_type', 'owner_department']


class IoCForm(forms.ModelForm):
    class Meta:
        model = IndicatorOfCompromise
        fields = ['ioc_type', 'ioc_value', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class ResponseActionForm(forms.ModelForm):
    class Meta:
        model = ResponseAction
        fields = ['phase', 'action_taken', 'performed_by', 'performed_at']
        widgets = {
            'action_taken':  forms.Textarea(attrs={'rows': 2}),
            'performed_at':  forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class MitreMappingForm(forms.ModelForm):
    class Meta:
        model = MitreMapping
        fields = ['tactic', 'technique_id', 'technique_name']


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['evidence_type', 'file_path', 'description', 'collected_by', 'collected_at', 'chain_of_custody_notes']
        widgets = {
            'description':            forms.Textarea(attrs={'rows': 2}),
            'chain_of_custody_notes': forms.Textarea(attrs={'rows': 2}),
            'collected_at':           forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }