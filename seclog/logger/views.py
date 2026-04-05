from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Incident
from .forms import RegisterForm, NewIncidentForm, EditIncidentForm, AffectedAssetForm, IoCForm, ResponseActionForm, MitreMappingForm, EvidenceForm, ClosingNoteForm, Incident, Responder, ClosingNote


def landing(request):
    print(f"Method: {request.method}")
    print(f"Is authenticated: {request.user.is_authenticated}")

    if request.user.is_authenticated:
        print("User is authenticated, redirecting to index")
        return redirect('logger:index')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(f"Auth result: {user}")
        if user is not None:
            login(request, user)
            print(f"Logged in, redirecting...")
            return redirect('logger:index')
        else:
            error = 'Invalid credentials.'

    return render(request, 'logger/landing.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('logger:landing')


@login_required(login_url='/')
def index(request):
    open_incidents = Incident.objects.filter(
        status__in=['OPEN', 'IN_PROGRESS']
    ).order_by('-reported_at')

    closed_incidents = Incident.objects.filter(
        status__in=['RESOLVED', 'CLOSED']
    ).order_by('-resolved_at')

    context = {
        'open_incidents': open_incidents,
        'closed_incidents': closed_incidents,
        'responders': Responder.objects.all(),
    }
    return render(request, 'logger/index.html', context)


@login_required(login_url='/')
def newIncident(request):
    if request.method == 'POST':
        form = NewIncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            return redirect('logger:editIncident', pk=incident.pk)
    else:
        form = NewIncidentForm()
    return render(request, 'logger/new_incident.html', {'form': form})


@login_required(login_url='/')
def editIncident(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'incident':
            form = EditIncidentForm(request.POST, instance=incident)
            if form.is_valid():
                form.save()
        elif form_type == 'asset':
            form = AffectedAssetForm(request.POST)
            if form.is_valid():
                asset = form.save(commit=False)
                asset.incident = incident
                asset.save()
        elif form_type == 'ioc':
            form = IoCForm(request.POST)
            if form.is_valid():
                ioc = form.save(commit=False)
                ioc.incident = incident
                ioc.save()
        elif form_type == 'action':
            form = ResponseActionForm(request.POST)
            if form.is_valid():
                action = form.save(commit=False)
                action.incident = incident
                action.save()
        elif form_type == 'mitre':
            form = MitreMappingForm(request.POST)
            if form.is_valid():
                mitre = form.save(commit=False)
                mitre.incident = incident
                mitre.save()
        elif form_type == 'evidence':
            form = EvidenceForm(request.POST)
            if form.is_valid():
                evidence = form.save(commit=False)
                evidence.incident = incident
                evidence.save()

        return redirect('logger:editIncident', pk=incident.pk)

    context = {
        'incident':       incident,
        'incident_form':  EditIncidentForm(instance=incident),
        'asset_form':     AffectedAssetForm(),
        'ioc_form':       IoCForm(),
        'action_form':    ResponseActionForm(),
        'mitre_form':     MitreMappingForm(),
        'evidence_form':  EvidenceForm(),
        'assets':         incident.assets.all(),
        'iocs':           incident.iocs.all(),
        'actions':        incident.response_actions.all(),
        'mitre_mappings': incident.mitre_mappings.all(),
        'evidence':       incident.evidence.all(),
    }
    return render(request, 'logger/edit_incident.html', context)

@login_required(login_url='/')
def myIncidents(request):
    open_incidents = Incident.objects.filter(
        status__in=['OPEN', 'IN_PROGRESS'],
        assigned_to__user=request.user        # filter by logged in user
    ).order_by('-reported_at')

    closed_incidents = Incident.objects.filter(
        status__in=['RESOLVED', 'CLOSED'],
        assigned_to__user=request.user
    ).order_by('-resolved_at')

    context = {
        'open_incidents': open_incidents,
        'closed_incidents': closed_incidents,
        'responders': Responder.objects.all(),
    }
    return render(request, 'logger/my_incidents.html', context)

def infoGather(request):
    return render(request, 'logger/index.html')

def resolveIncident(request):
    return render(request, 'logger/index.html')
@login_required(login_url='/')
def quickClose(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == 'POST':
        form = ClosingNoteForm(request.POST)
        if form.is_valid():
            from django.utils import timezone

            # Update existing closing note or create a new one
            closing_note, created = ClosingNote.objects.update_or_create(
                incident=incident,
                defaults={
                    'summary':     form.cleaned_data['summary'],
                    'resolution':  form.cleaned_data['resolution'],
                    'authored_by': form.cleaned_data['authored_by'],
                }
            )

            incident.status = Incident.Status.CLOSED
            incident.resolved_at = timezone.now()
            incident.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'errors': 'Invalid request method'})

def register(request):
    if request.user.is_authenticated:
        return redirect('logger:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.email      = form.cleaned_data['email']
            user.save()

            # Get or create the Responder in case signal didn't fire
            responder, created = Responder.objects.get_or_create(user=user)
            responder.role = form.cleaned_data['role']
            responder.save()

            login(request, user)
            return redirect('logger:index')
    else:
        form = RegisterForm()

    return render(request, 'logger/landing.html', {
        'form': form,
        'show_register': True
    })