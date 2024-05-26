from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.utils.http import urlquote
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from . import models
import os
import shutil
import zipfile
from pathlib import Path
from map.models import Img
import exif
from PIL import Image #PIL 安裝pip install Pillow
from pmap import settings


def data2gps(data, ref): #將相片的GPS資料轉換成GPS數值
    gps = data[0] + data[1] / 60 + data[2] / 3600
    if ref == "S" or ref =='W' :
        gps = -gps
    return gps
    
def tr_datetime(x):  #2024:04:25 11:42:08轉換成2024-04-25 11:42:08
    y = x[:4]+"-"+x[5:7]+"-"+x[8:10]+x[10:]
    return y
    
def image_getgps(path, filename, dirname):  #找出圖片exif的GPS、日期時間、檔案名稱與資料夾
    filepath = path+"/"+filename
    with open(filepath, 'rb') as src:
        img = exif.Image(src)
    if img.has_exif:
        try:
            img.gps_longitude #讀取GPS資料
            gps = (data2gps(img.gps_latitude, img.gps_latitude_ref), 
                    data2gps(img.gps_longitude, img.gps_longitude_ref)) #相片的GPS轉換成GPS數值
            dt = tr_datetime(img.datetime)
        except AttributeError:
            print ('沒有GPS資料')
    else:
        print ('圖片沒有EXIF資訊')
    return  {"lat":gps[0], "lng":gps[1], "datetime":dt, "path":path, "dirname":dirname, "filename":filename}

def check_dul(lat, lng, datetime, filename):  #檢查該圖片是否已經加入資料庫
    if len(Img.objects.filter(lat=lat, lng=lng, imgtime=datetime, filename=filename)) > 0:
        return True
    else:
        return False

def img2db(dirname):  #找出所有資料夾下圖片加到資料庫
    path = str(settings.BASE_DIR)+ "/media/img/"+ dirname #子資料夾路徑
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))] #找出子資料夾下的所有圖檔
    for file in files:
        imgexif = image_getgps(path, file, dirname)
        if check_dul(imgexif['lat'], imgexif['lng'], imgexif['datetime'], imgexif['filename']) == True: #出現過的圖片刪除，重新加入
            Img.objects.filter(lat=imgexif['lat'], lng=imgexif['lng'], imgtime=imgexif['datetime'], filename=imgexif['filename']).delete() #刪除舊的
        imgobject = Img.objects.create(lat=imgexif['lat'], lng=imgexif['lng'], imgtime=imgexif['datetime'],path=imgexif['path'], filename=imgexif['filename'], dirname=imgexif['dirname'])
        imgobject.save()


@login_required
def uploadFile(request):  #上傳多張圖片的zip檔
    if request.method == "POST":
        if request.POST["fileTitle"]:
            fileTitle = request.POST["fileTitle"]
        else:
            fileTitle = request.FILES["uploadedFile"].name
        if request.user.is_authenticated and request.user.has_perm('file.file_upload'):
            uploadedFile = request.FILES["uploadedFile"]
            file = models.File(
            	title = fileTitle,
            	uploadedFile = uploadedFile,
            	user = request.user
            )
        file.save()
    files = models.File.objects.all().order_by("-id") #新上傳的壓縮檔放前面
    return render(request, "upload-file.html", context = { "files": files })


@login_required
def deleteFile(request, pk):
    dir = 'media/'
    unzipdir = 'media/img/'
    deletefile = models.File.objects.filter(pk = pk)
    f = deletefile[0]
    if (f.user == request.user and request.user.has_perm('file.file_delete')): #檔案上傳者且有刪除權限者才能刪除
        dirname = f.title[:-4]  #壓縮檔的檔名，去除.zip
        os.remove(dir+'{}'.format(f.uploadedFile))
        models.File.objects.filter(pk = pk).delete()
        shutil.rmtree(unzipdir+dirname)  #刪除解壓縮資料夾
        Img.objects.filter(dirname = dirname).delete()  #刪除該資料夾再資料表Img的所有圖片資料
    return HttpResponseRedirect(reverse('file:upload'))

@login_required
def downloadFile(request, pk):
    file = models.File.objects.filter(pk=pk)
    dir = 'media/'
    if file:
        f = file[0]
        path = dir+'{}'.format(f.uploadedFile)
        file = open(path, 'rb') # 讀取檔案
        response = FileResponse(file)
        di,fi = str(f.uploadedFile).split('/') #資料夾與檔名分開
        response['Content-Disposition'] = 'attachment;filename="%s"' % urlquote(fi)  #urlquote對檔名稱進行編碼
        return response
    else:
        return HttpResponse('檔案不存在!')
    
@login_required
def unzipFile(request, pk):  #將多張圖片的zip檔進行解壓縮
    dir = 'media/img/'
    unzipfile = models.File.objects.filter(pk = pk)
    f = unzipfile[0]
    if (f.user == request.user and request.user.has_perm('file.file_upload')): #檔案上傳者且有上傳權限者才能解壓縮
        with zipfile.ZipFile(f.uploadedFile.path, "r") as zip:
            odir = zip.namelist()[0].split('/')[0]  #壓縮檔只能有一層資料夾，取出資料夾名稱
            ndir = odir.encode('cp437').decode('big5')  #解壓縮中文資料夾出現亂碼進行修正
            if os.path.isdir(dir+ndir)==True: #檢查是否有相同資料夾，先刪除資料夾再解壓縮
                shutil.rmtree(dir+ndir)  #刪除資料夾
            zip.extractall(dir) #解壓縮
            os.rename(dir+odir,dir+ndir)  #重新命名資料夾
    return HttpResponseRedirect(reverse('file:upload'))

@login_required
def makeThumbnail(request, pk):  #製作縮圖並將圖檔加入資料庫
    dir = 'media/img/'
    unzipfile = models.File.objects.filter(pk = pk)
    f = unzipfile[0]
    if (f.user == request.user and request.user.has_perm('file.file_upload')): #檔案上傳者且有上傳權限者才能解壓縮
        dirname = f.title[:-4]  #壓縮檔的檔名，去除.zip
        dirpath = dir+dirname
        #找出不是tH開頭的圖片檔
        files = [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath,f)) and f[0:2]!='tH']  #

        for f in files:
            img = Image.open(dirpath+'/'+f)
            ex = img.info['exif']
            img.thumbnail((150, 150)) #製作縮圖
            print(img.size)
            img.save(dirpath+'/tH_'+f, exif=ex)  #儲存時會根據exif資料進行旋轉，不需事先旋轉
        img2db(dirname)  #將圖檔與縮圖檔案加入資料庫
    return HttpResponseRedirect(reverse('file:upload'))

