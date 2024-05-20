from django.urls import path
from .views import GalListView, GalView

app_name = 'gal'

urlpatterns = [
    path('list/<str:dirname>', GalView.as_view(), name='listdir'),
    path('list/', GalListView.as_view(), name='list'),
]