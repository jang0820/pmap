from django.urls import path
from .views import ImgListView

app_name = 'gal'

urlpatterns = [
    path('list/<str:dirname>', ImgListView.as_view(), name='list'),
]