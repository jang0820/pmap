from django.urls import path
from .views import MapView,  MapListView

app_name = 'map'

urlpatterns = [
    path('go', MapView.as_view(), name='go'),
    path('go/<str:dirname>', MapView.as_view(), name='godir'),
    path('list/', MapListView.as_view(), name='list'),
]