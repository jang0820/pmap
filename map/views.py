from django.views.generic import TemplateView
import folium
import base64
import exif
import os
from map.models import Img

class MapView(TemplateView):
    template_name = 'map.html'    
    def data2gps(self, data, ref): #將相片的GPS資料轉換成GPS數值
        gps = data[0] + data[1] / 60 + data[2] / 3600
        if ref == "S" or ref =='W' :
            gps = -gps
        return gps

    def image_getgps(self, path, filename, dirname):
        filepath = path+"\\"+filename
        with open(filepath, 'rb') as src:
            img = exif.Image(src)
        if img.has_exif:
            try:
                img.gps_longitude
                gps = (self.data2gps(img.gps_latitude, img.gps_latitude_ref), 
                       self.data2gps(img.gps_longitude, img.gps_longitude_ref)) #相片的GPS轉換成GPS數值
                dt = img.datetime
            except AttributeError:
                print ('沒有GPS資料')
        else:
            print ('圖片沒有EXIF資訊')
        return  {"lat":gps[0], "lng":gps[1], "datetime":dt, "path":path, "dirname":dirname, "filename":filename}
    
    def tr_datetime(self, x):  #2024:04:25 11:42:08轉換成2024-04-25 11:42:08
        y = x[:4]+"-"+x[5:7]+"-"+x[8:10]+x[10:]
        return y
    
    def check_dul(self, lat, lng, filename):  #檢查該圖片是否已經加入資料庫
        if len(Img.objects.filter(lat=lat, lng=lng, filename=filename)) > 0:
            return True
        else:
            return False

    def img2db(self, dirname):  #找出所有資料夾下圖片加到資料庫，並傳回最後一個資料夾的第一個圖片GPS
        pwd = os.path.dirname(__file__)  #找出目前檔案views.py的所在資料夾
        path = pwd+'\\img'
        path2 = path + "\\" + dirname #子資料夾路徑
        files = [f for f in os.listdir(path2) if os.path.isfile(os.path.join(path2,f))] #找出子資料夾下的圖檔
        for file in files:
            imgexif = self.image_getgps(path2, file, dir)
            if self.check_dul(imgexif['lat'], imgexif['lng'], imgexif['filename']) == False: #每張圖片只加入一次
                imgobject = Img.objects.create(lat=imgexif['lat'], lng=imgexif['lng'], imgtime=self.tr_datetime(imgexif['datetime']),path=imgexif['path'], filename=imgexif['filename'], dirname=imgexif['dirname'])
                imgobject.save()
        first = Img.objects.filter(filename=files[0])
        return {'lat':first[0].lat, 'lng':first[0].lng} #回傳第一個圖檔的GPS
    
    def get_context_data(self, **kwargs):
        dirname = kwargs['dirname']
        figure = folium.Figure()
        img_gps = self.img2db(dirname) #取出第一個圖檔的GPS座標來建立地圖的起始位置
        #建立地圖
        map = folium.Map( 
            location = [img_gps['lat'], img_gps['lng']], #地圖開始的所在GPS
            zoom_start = 16,  #開始的地圖縮放程度
            tiles = 'OpenStreetMap')  #使用的地圖系統
        map.add_to(figure)       
        for imgexif in Img.objects.all():
            #使用popup建立彈出的圖片
            encoded = base64.b64encode(open(imgexif.path +'\\'+imgexif.filename, 'rb').read())
            html = '<img src="data:image/jpeg;base64,{}">'.format
            iframe = folium.IFrame(html(encoded.decode('UTF-8')), width=160, height=160)
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
