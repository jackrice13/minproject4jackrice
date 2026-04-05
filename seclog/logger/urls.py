from django.urls import path
from . import views

app_name = 'logger'

urlpatterns = [
    path('', views.landing, name='landing'),                          # ← added
    path('logger/', views.index, name='index'),
    path('logger/my-incidents/', views.myIncidents, name='myIncidents'),
    path('logger/new/', views.newIncident, name='newIncident'),
    path('logger/edit/<int:pk>/', views.editIncident, name='editIncident'),
    path('logger/gather/', views.infoGather, name='infoGather'),
    path('logger/resolve/', views.resolveIncident, name='resolveIncident'),
    path('logout/', views.logout_view, name='logout'),                # ← added
]