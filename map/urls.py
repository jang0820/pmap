from django.urls import path
from .views import MapView,  MapListView

app_name = 'map'

urlpatterns = [
    path('list/<str:dirname>', MapView.as_view(), name='listdir'),
    path('list/', MapListView.as_view(), name='list'),
]