from django.views.generic import TemplateView, ListView
import folium
import base64
import os
from map.models import Img
from pmap import settings

class MapView(TemplateView): #列出指定資料夾下所有圖片到地圖上
    template_name = 'map.html'    

    def get_gps(self, dirname):  #傳回指定資料夾內的第一個圖片GPS
        path = str(settings.BASE_DIR)+ "/media/img/"+ dirname #子資料夾路徑
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) and f[0:2]=='tH'] #找出子資料夾下的tH開頭的縮圖圖檔
        first = Img.objects.filter(filename=files[0])
        return {'lat':first[0].lat, 'lng':first[0].lng} #回傳第一個圖檔的GPS
    
    def get_context_data(self, **kwargs):
        dirname = kwargs['dirname']
        figure = folium.Figure()
        img_gps = self.get_gps(dirname) #取出第一個圖檔的GPS座標來建立地圖的起始位置
        #建立地圖
        map = folium.Map( 
            location = [img_gps['lat'], img_gps['lng']], #地圖開始的所在GPS
            zoom_start = 16,  #地圖縮放程度
            tiles = 'OpenStreetMap')  #使用的地圖系統
        map.add_to(figure)
        
        for imgexif in Img.objects.filter(dirname=dirname, filename__startswith="tH"): #只取資料庫內指定dirname的資料夾內，開頭是tH的圖片
            #使用popup建立彈出的圖片
            encoded = base64.b64encode(open(imgexif.path +'/'+imgexif.filename, 'rb').read())
            html = '<img src="data:image/jpeg;base64,{}">'.format
            iframe = folium.IFrame(html(encoded.decode('UTF-8')), width=170, height=170)
            x = folium.Popup(iframe, max_width=180)

            #將上方popup新增到此marker
            folium.Marker(
                location = [imgexif.lat, imgexif.lng],
                popup = x,
                tooltip = imgexif.dirname,
                icon = folium.Icon(icon='fa-mountain', prefix='fa')
            ).add_to(map)
        
        #與樣板map.html結合
        figure.render()
        return {"map": figure}


class MapListView(ListView):  #列出資料夾media\img下所有子資料夾
    template_name = 'maplist.html'
    queryset = {}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        imgpath = str(settings.BASE_DIR)+ "/media/img/"
        dirs = [d for d in os.listdir(imgpath) if os.path.isdir(os.path.join(str(settings.BASE_DIR)+ "/media/img/", d))] #找出子資料夾
        context["dirs"] = dirs
        return context

