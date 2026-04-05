from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import Incident
from .forms import NewIncidentForm

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
    }
    return render(request, 'logger/index.html', context)

def newIncident(request):
    if request.method == 'POST':
        form = NewIncidentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logger:index')
    else:
        form = NewIncidentForm()

    return render(request, 'logger/new_incident.html', {'form': form})

def editIncident(request):
    return HttpResponse("Hello, world. You're at the editIncident Page.")

def infoGather(request):
    return HttpResponse("Hello, world. You're at the infoGather Page.")

def resolveIncident(request):
    return HttpResponse("Hello, world. You're at the resolveIncident Page.")