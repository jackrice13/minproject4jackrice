from django.contrib import admin
from .models import (
    IncidentType,
    AttackVector,
    Responder,
    Incident,
    AffectedAsset,
    IndicatorOfCompromise,
    ResponseAction,
    MitreMapping,
    Evidence,
    PostIncidentReview,
)


# ------------------------------------------------------------------
# INLINE CLASSES
# These let you edit related records directly inside the Incident page
# instead of having to navigate to a separate page for each one.
# ------------------------------------------------------------------

class AffectedAssetInline(admin.TabularInline):
    model = AffectedAsset
    extra = 1  # shows 1 blank row by default so you can add one immediately


class IndicatorOfCompromiseInline(admin.TabularInline):
    model = IndicatorOfCompromise
    extra = 1


class ResponseActionInline(admin.TabularInline):
    model = ResponseAction
    extra = 1


class MitreMappingInline(admin.TabularInline):
    model = MitreMapping
    extra = 1


class EvidenceInline(admin.StackedInline):
    # StackedInline gives each evidence record more vertical space
    # which is better here since Evidence has lots of fields
    model = Evidence
    extra = 1


class PostIncidentReviewInline(admin.StackedInline):
    model = PostIncidentReview
    extra = 0  # 0 because a review only gets written after closure


# ------------------------------------------------------------------
# MAIN MODEL ADMIN CLASSES
# These control how each model looks in the admin list and detail views
# ------------------------------------------------------------------

@admin.register(IncidentType)
class IncidentTypeAdmin(admin.ModelAdmin):
    list_display  = ('type_name',)
    search_fields = ('type_name',)


@admin.register(AttackVector)
class AttackVectorAdmin(admin.ModelAdmin):
    list_display  = ('vector_name',)
    search_fields = ('vector_name',)


@admin.register(Responder)
class ResponderAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'get_email', 'role']

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    # Columns shown on the incident list page
    list_display = (
        'id', 'title', 'status', 'severity',
        'incident_type', 'assigned_to', 'detected_at', 'repeat_incident'
    )

    # Sidebar filters on the right side of the list page
    list_filter = ('status', 'severity', 'incident_type', 'attack_vector', 'repeat_incident')

    # Search bar — searches across these fields
    search_fields = ('title', 'cve_number', 'detected_by', 'business_impact')

    # Fields that can be edited directly on the list page without opening the record
    list_editable = ('status', 'severity')

    # How fields are grouped on the detail/edit page
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'status', 'severity', 'incident_type', 'attack_vector')
        }),
        ('Detection & Assignment', {
            'fields': ('detected_by', 'assigned_to', 'detected_at', 'reported_at', 'resolved_at')
        }),
        ('Impact', {
            'fields': ('data_compromised', 'data_classification', 'downtime_minutes', 'business_impact')
        }),
        ('Technical Details', {
            'fields': ('cve_number', 'repeat_incident')
        }),
    )

    # Inlines embed the related tables directly on the Incident detail page
    inlines = [
        AffectedAssetInline,
        IndicatorOfCompromiseInline,
        ResponseActionInline,
        MitreMappingInline,
        EvidenceInline,
        PostIncidentReviewInline,
    ]

    # Default sort order — newest incidents first
    ordering = ('-created_at',)


@admin.register(AffectedAsset)
class AffectedAssetAdmin(admin.ModelAdmin):
    list_display  = ('hostname', 'ip_address', 'asset_type', 'owner_department', 'incident')
    search_fields = ('hostname', 'ip_address', 'owner_department')
    list_filter   = ('asset_type',)


@admin.register(IndicatorOfCompromise)
class IndicatorOfCompromiseAdmin(admin.ModelAdmin):
    list_display  = ('ioc_type', 'ioc_value', 'incident')
    search_fields = ('ioc_value', 'notes')
    list_filter   = ('ioc_type',)


@admin.register(ResponseAction)
class ResponseActionAdmin(admin.ModelAdmin):
    list_display  = ('phase', 'action_taken', 'performed_by', 'performed_at', 'incident')
    search_fields = ('action_taken',)
    list_filter   = ('phase',)


@admin.register(MitreMapping)
class MitreMappingAdmin(admin.ModelAdmin):
    list_display  = ('technique_id', 'technique_name', 'tactic', 'incident')
    search_fields = ('technique_id', 'technique_name', 'tactic')
    list_filter   = ('tactic',)


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display  = ('evidence_type', 'description', 'collected_by', 'collected_at', 'incident')
    search_fields = ('description', 'chain_of_custody_notes')
    list_filter   = ('evidence_type',)


@admin.register(PostIncidentReview)
class PostIncidentReviewAdmin(admin.ModelAdmin):
    list_display  = ('incident', 'authored_by', 'authored_at')
    search_fields = ('root_cause', 'lessons_learned', 'followup_actions')