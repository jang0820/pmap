from django.urls import path
from .views import MapView

app_name = 'map'

urlpatterns = [
    path('go', MapView.as_view(), name='go'),
]