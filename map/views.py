from django.views.generic import TemplateView
import folium
import base64
import exif
import os

class MapView(TemplateView):
    template_name = 'map.html'    
    def data2gps(self, data, ref): #將相片的GPS資料轉換成GPS數值
        gps = data[0] + data[1] / 60 + data[2] / 3600
        if ref == "S" or ref =='W' :
            gps = -gps
        return gps

    def image_getgps(self, path):
        with open(path, 'rb') as src:
            img = exif.Image(src)
        if img.has_exif:
            try:
                img.gps_longitude
                gps = (self.data2gps(img.gps_latitude, img.gps_latitude_ref), 
                       self.data2gps(img.gps_longitude, img.gps_longitude_ref)) #相片的GPS轉換成GPS數值
            except AttributeError:
                print ('沒有GPS資料')
        else:
            print ('圖片沒有EXIF資訊')
        return  {"lat":gps[0],"lng":gps[1]}
    
    def get_context_data(self, **kwargs):
        figure = folium.Figure()
        pwd = os.path.dirname(__file__)  #找出目前檔案views.py的所在資料夾
        path = pwd + '\\1.jpg'
        gps = self.image_getgps(path)
        #建立地圖
        map = folium.Map( 
            location = [gps['lat'], gps['lng']], #地圖開始的所在GPS
            zoom_start = 16,  #開始的地圖縮放程度
            tiles = 'OpenStreetMap')  #使用的地圖系統

        map.add_to(figure)
        #使用popup建立彈出的圖片
        encoded = base64.b64encode(open(pwd +'\\1.jpg', 'rb').read())
        html = '<img src="data:image/jpeg;base64,{}">'.format
        iframe = folium.IFrame(html(encoded.decode('UTF-8')), width=160, height=160)
        x = folium.Popup(iframe, max_width=180)

        #將上方popup新增到此marker
        folium.Marker(
            location = [gps['lat'], gps['lng']],
            popup = x,
            tooltip = '台北大縱走',
            icon = folium.Icon(icon='fa-mountain', prefix='fa')
        ).add_to(map)
        
        #與樣板map.html結合
        figure.render()
        return {"map": figure}
