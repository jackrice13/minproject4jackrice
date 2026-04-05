from django import forms
from .models import Incident, IncidentType, AttackVector, Responder

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