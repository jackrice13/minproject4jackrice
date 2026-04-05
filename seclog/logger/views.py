from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def newIncident(request):
    return HttpResponse("Hello, world. You're at the newIncident Page.")

def editIncident(request):
    return HttpResponse("Hello, world. You're at the editIncident Page.")

def infoGather(request):
    return HttpResponse("Hello, world. You're at the infoGather Page.")

def resolveIncident(request):
    return HttpResponse("Hello, world. You're at the resolveIncident Page.")