from django.urls import path
from .views import GalListView, GalView, GalSearchDirListView

app_name = 'gal'

urlpatterns = [
    path('list/<str:dirname>', GalView.as_view(), name='listdir'),
    path('searchdir/', GalSearchDirListView.as_view(), name='searchdir'),
    path('list/', GalListView.as_view(), name='list'),
]