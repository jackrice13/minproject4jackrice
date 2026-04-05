from django.urls import path
from . import views

app_name = 'logger'

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.newIncident, name='newIncident'),
    path('edit/', views.editIncident, name='editIncident'),
    path('gather/', views.infoGather, name='infoGather'),
    path('resolve/', views.resolveIncident, name='resolveIncident'),
]