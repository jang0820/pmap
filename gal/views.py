import os
from django.shortcuts import render
from map.models import Img
from django.views.generic import TemplateView, ListView
from pmap import settings
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from map.models import Img

class GalView(TemplateView): #將指定資料夾下不是tH開頭的圖片製作成相簿
    template_name = 'img.html'
    imgpath = str(settings.BASE_DIR)+ "/media/img/"
    queryset = {}

    def get_context_data(self, **kwargs):
        dir = kwargs['dirname']
        imgs = Img.objects.filter(dirname=dir).exclude(filename__startswith='tH') #取出指定資料夾，排除tH開頭的縮圖
        context = super().get_context_data(**kwargs)
        context["imgs"] = imgs
        return context
    
class GalListView(ListView): #列出media/img下的所有子資料夾，每分頁10個資料夾
    template_name = 'gallist.html'
    queryset = {}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        imgpath = str(settings.BASE_DIR)+ "/media/img/"
        dirs = [d for d in os.listdir(imgpath) if os.path.isdir(os.path.join(str(settings.BASE_DIR)+ "/media/img/", d))] #找出子資料夾
        context["dirs"] = dirs
        limit = 10  #每個分頁10個資料夾
        paginator = Paginator(dirs, limit)  #設定分頁的資料夾數量
        page = self.request.GET.get('page')  #取出網址的page的值(?page=xx)
        try:
            dirp = paginator.page(page)  #指定第幾個page
        except PageNotAnInteger:  #page不是整數
            dirp = paginator.page(1)  #指定第一個分頁
        except EmptyPage:  #不存在的分頁
            dirp = paginator.page(1)  #指定第一個分頁
        context["dirp"] = dirp
        return context

class GalSearchDirListView(ListView):  #使用字串搜尋資料夾media\img下的子資料夾名稱
    template_name = 'galsearchdirlist.html'
    queryset = {}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            query = self.request.GET['query'] #取出網址的page的字串(?query=xxx)
            imgs = Img.objects.filter(dirname__contains=query) #取出所有子資料夾名稱是否包含字串query
            dirs = []
            for item in imgs: #所有資料夾名稱只取一次
                if item.dirname not in dirs: dirs.append(item.dirname)
            context["dirs"] = dirs
        return context