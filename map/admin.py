from django.contrib import admin
from .models import Img

class ImgAdmin(admin.ModelAdmin):
    list_display = ('lat', 'lng', 'imgtime', 'filename', 'dirname','path')

admin.site.register(Img, ImgAdmin)