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
            #dirr = zip.namelist()[0]
            odir = zip.namelist()[0].split('/')[0]  #壓縮檔只能有一層資料夾，取出資料夾名稱
            ndir = odir.encode('cp437').decode('big5')  #解壓縮中文資料夾出現亂碼進行修正
            if os.path.isdir(dir+ndir)==True: #檢查是否有相同資料夾，先刪除資料夾再解壓縮
                shutil.rmtree(dir+ndir)  #刪除資料夾
            zip.extractall(dir) #解壓縮
            os.rename(dir+odir,dir+ndir)  #重新命名資料夾
    return HttpResponseRedirect(reverse('file:upload'))

@login_required
def makeThumbnail(request, pk):  #將多張圖片的zip檔進行解壓縮
    dir = 'media/img/'
    unzipfile = models.File.objects.filter(pk = pk)
    f = unzipfile[0]
    if (f.user == request.user and request.user.has_perm('file.file_upload')): #檔案上傳者且有上傳權限者才能解壓縮
        dirname = f.title[:-4]  #壓縮檔的檔名，去除.zip
        dirpath = dir+dirname
        #os.chdir(dirpath)  # 更換資料夾
        #找出不是ss開頭的圖片檔
        files = [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath,f)) and f[0:2]!='tH']  #

        for f in files:
            img = Image.open(dirpath+'/'+f)
            ex = img.info['exif']
            img.thumbnail((150, 150)) #製作縮圖
            print(img.size)
            img.save(dirpath+'/tH_'+f, exif=ex)  #儲存時會根據exif資料進行旋轉，不需事先旋轉
    return HttpResponseRedirect(reverse('file:upload'))