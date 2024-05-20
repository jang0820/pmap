from django.shortcuts import render
from map.models import Img
from django.views.generic import TemplateView, ListView
from pmap import settings
import os

class GalView(TemplateView):
    template_name = 'img.html'
    imgpath = str(settings.BASE_DIR)+ "\\media\\img\\"

    dirs = [d for d in os.listdir(imgpath) if os.path.isdir(os.path.join(str(settings.BASE_DIR)+ "\\media\\img\\", d))] #找出子資料夾
    queryset = {}

    def get_context_data(self, **kwargs):
        dir = kwargs['dirname']
        imgs = Img.objects.filter(dirname=dir)
        context = super().get_context_data(**kwargs)
        context["imgs"] = imgs
        return context
    

class GalListView(ListView):
    template_name = 'gallist.html'
    imgpath = str(settings.BASE_DIR)+ "\\media\\img\\"
    dirs = [d for d in os.listdir(imgpath) if os.path.isdir(os.path.join(str(settings.BASE_DIR)+ "\\media\\img\\", d))] #找出子資料夾
    queryset = {}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dirs"] = self.dirs
        return context