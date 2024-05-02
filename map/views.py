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

    def image_getgps(self, dir, filename):
        path = dir+"\\"+filename
        with open(path, 'rb') as src:
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
        return  {"lat":gps[0], "lng":gps[1], "datetime":dt, "dir":dir, "filename":filename}
    
    def tr_datetime(self, x):  #2024:04:25 11:42:08轉換成2024-04-25 11:42:08
        y = x[:4]+"-"+x[5:7]+"-"+x[8:10]+x[10:]
        return y
    
    def check_dul(self, lat, lng, filename):  #檢查該圖片是否已經加入資料庫
        if len(Img.objects.filter(lat=lat, lng=lng, filename=filename)) > 0:
            return True
        else:
            return False

    def img2db(self, **kwargs):
        pwd = os.path.dirname(__file__)  #找出目前檔案views.py的所在資料夾
        dir = pwd+'\\img'
        files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f))]
        #filename = '1.jpg'
        for file in files:
            imgexif = self.image_getgps(dir, file)
            if self.check_dul(imgexif['lat'], imgexif['lng'], imgexif['filename']) == False: #每張圖片只加入一次
                imgobject = Img.objects.create(lat=imgexif['lat'], lng=imgexif['lng'], imgtime=self.tr_datetime(imgexif['datetime']), filename=imgexif['filename'], dirname=imgexif['dir'])
                imgobject.save()


    def get_context_data(self, **kwargs):
        figure = folium.Figure()
        self.img2db()
        '''pwd = os.path.dirname(__file__)  #找出目前檔案views.py的所在資料夾
        filename = '1.jpg'
        imgexif = self.image_getgps(pwd, filename)
        if self.check_dul(imgexif['lat'], imgexif['lng'], imgexif['filename']) == False: #每張圖片只加入一次
            imgobject = Img.objects.create(lat=imgexif['lat'], lng=imgexif['lng'], imgtime=self.tr_datetime(imgexif['datetime']), filename=imgexif['filename'], dirname=imgexif['dir'])
            imgobject.save()'''
        #建立地圖
        map = folium.Map( 
            location = [25.03, 121.6], #地圖開始的所在GPS
            zoom_start = 16,  #開始的地圖縮放程度
            tiles = 'OpenStreetMap')  #使用的地圖系統
        map.add_to(figure)       
        for imgexif in Img.objects.all():
            #使用popup建立彈出的圖片
            encoded = base64.b64encode(open(imgexif.dirname +'\\'+imgexif.filename, 'rb').read())
            html = '<img src="data:image/jpeg;base64,{}">'.format
            iframe = folium.IFrame(html(encoded.decode('UTF-8')), width=160, height=160)
            x = folium.Popup(iframe, max_width=180)

            #將上方popup新增到此marker
            folium.Marker(
                location = [imgexif.lat, imgexif.lng],
                popup = x,
                tooltip = '台北大縱走',
                icon = folium.Icon(icon='fa-mountain', prefix='fa')
            ).add_to(map)
        
        #與樣板map.html結合
        figure.render()
        return {"map": figure}
